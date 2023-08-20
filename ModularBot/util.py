from datetime import datetime
from os import path
from io import BytesIO
from typing import Union
from logging import Logger, getLogger, INFO, StreamHandler

from aiohttp import ClientSession
from discord import Embed, Emoji, Interaction, Message, InteractionResponded, MessageFlags
from discord.utils import _ColourFormatter
from discord.ui import View
from PIL import Image
from easy_pil import load_image_async, Editor, Font
from pytz import timezone

from config import ModularBotConst, GuildMessage


class ModularUtil:
    __IP_GEOLOCATION_URL = "http://ip-api.com/json/"
    __ASSETS_DIR = path.join(path.dirname(__file__), "assets")

    @classmethod
    def get_time(cls) -> datetime:
        return datetime.now(timezone(ModularBotConst.TIMEZONE))

    @classmethod
    def convert_color(cls, color: str) -> int:
        return int(color.lstrip('#'), 16)

    @classmethod
    async def get_geolocation(cls, session: ClientSession) -> str:
        async with session.get(cls.__IP_GEOLOCATION_URL) as resp:
            if (resp.status == 200):
                resp = await resp.json()
                return f"{resp['city']}, {resp['regionName']}, {resp['country']}"
            else:
                return
            
    @classmethod
    def setup_log(cls):
        logger: Logger = getLogger(ModularBotConst.BOT_NAME)
        logger.setLevel(INFO)

        handler = StreamHandler()
        handler.setFormatter(_ColourFormatter())
        logger.addHandler(handler)
            
    @classmethod
    def simple_log(cls, message: str):
        logger: Logger = getLogger(ModularBotConst.BOT_NAME)
        logger.info(message)

    @classmethod
    async def send_response(cls, interaction: Interaction, /, message: str = None, embed: Embed = None, emoji: Union[Emoji, str] = None, view: View = None, ephemeral: bool = False) -> Message:
        msg: Message = None
        temp: str = str()

        if not view:
            view = View()

        def change_emoji(message: str, emoji: Union[Emoji, str], ephemeral: bool = False) -> str:
            if isinstance(emoji, str) and ephemeral:
                return f"{emoji} {message}"
            
            if isinstance(emoji, Emoji):
                return f"{str(emoji)} {message}"

            return message

        try:
            temp = change_emoji(message, emoji, ephemeral)
            await interaction.response.send_message(temp, embed=embed, ephemeral=ephemeral, view=view)
            msg = await interaction.original_response()
        except InteractionResponded:
            msg = await interaction.original_response()
            flags: MessageFlags = msg.flags
            ephemeral = flags.ephemeral

            temp = change_emoji(message, emoji, ephemeral)

            msg = await interaction.followup.send(temp, embed=embed, ephemeral=ephemeral, view=view, wait=True)

        if emoji and not ephemeral:
            await msg.add_reaction(emoji)

        return msg

    @classmethod
    async def banner_creator(cls, username: str, avatar: str, is_welcome=True) -> BytesIO:
        title: str = "Welcome".upper()
        mssg: str = GuildMessage.BANNER['welcome_banner'].upper()
        banner: str = ModularBotConst.IMAGE['welcome_banner']

        if not is_welcome:
            title = "Goodbye".upper()
            mssg = GuildMessage.BANNER['leave_banner'].upper()
            banner: str = ModularBotConst.IMAGE['leave_banner']

        profile_size: int = 2.2

        profile: Image = await load_image_async(avatar)
        backgr: Image = await load_image_async(banner)
        background: Editor = Editor(backgr)

        profile_size: int = int(background.image.size[1]//profile_size)
        wI, hI = background.image.size

        profile: Editor = Editor(profile).resize(
            (profile_size, profile_size)).circle_image()
        bold_font: Font = Font(path=path.join(
            cls.__ASSETS_DIR, 'gibson_bold.ttf'), size=hI//5)
        regular_font: Font = Font(path=path.join(
            cls.__ASSETS_DIR, 'gibson_bold.ttf'), size=hI//10)
        small_font: Font = Font(path=path.join(
            cls.__ASSETS_DIR, 'gibson_semibold.ttf'), size=hI//15)

        x, y = ((wI-profile_size)//2, (hI-profile_size)//5)
        blur: Image = Image.new('RGBA', background.image.size)

        blurs: Editor = Editor(blur)
        blurs.ellipse((x, y), profile_size, profile_size,
                      outline='white', stroke_width=hI//65).blur(amount=8)
        background.paste(blurs, (0, 0))
        background.paste(profile, (x, y))
        background.ellipse((x, y), profile_size, profile_size,
                           outline='white', stroke_width=hI//65)

        blurs: Editor = Editor(blur)
        blurs.text((wI//2, hI//8*5), title, color="black",
                   font=bold_font, align='center').blur(amount=8)
        background.paste(blurs, (0, 0))
        background.text((wI//2, hI//8*5), title, color="white",
                        font=bold_font, align='center')

        blurs: Editor = Editor(blur)
        blurs.text((wI//2, hI//5*4), username.upper(), color="black",
                   font=regular_font, align='center').blur(amount=8)
        background.paste(blurs, (0, 0))
        background.text((wI//2, hI//5*4), username.upper(),
                        color="white", font=regular_font, align='center')

        blurs: Editor = Editor(blur)
        blurs.text((wI//2, hI//10*9), mssg, color="black",
                   font=small_font, align='center').blur(amount=8)
        background.paste(blurs, (0, 0))
        background.text((wI//2, hI//10*9), mssg, color="white",
                        font=small_font, align='center')

        return background.image_bytes
