from datetime import datetime
from os import path
from io import BytesIO
from logging import Logger, getLogger, INFO, StreamHandler

from aiohttp import ClientSession
from discord import (
	Embed,
	Emoji,
	Interaction,
	Message,
	InteractionResponded,
	MessageFlags,
)
from discord.utils import _ColourFormatter
from discord.ui import View
from PIL import Image
from easy_pil import load_image_async, Editor, Font
from pytz import timezone

from config import ModularBotConst, GuildMessage


class ModularUtil:
	__IP_GEOLOCATION_URL = "http://ip-api.com/json/"
	__ASSETS_DIR = path.join(path.dirname(__file__), "assets")

	@staticmethod
	def get_time() -> datetime:
		return datetime.now(timezone(ModularBotConst.TIMEZONE))

	@staticmethod
	def convert_color(color: str) -> int:
		return int(color.lstrip("#"), 16)

	@staticmethod
	def truncate_string(text: str, /, max: int = 150) -> str:
		if len(text) > max:
			return text[: max - 3] + "..."
		return text

	@classmethod
	async def get_geolocation(cls, session: ClientSession) -> str | None:
		async with session.get(cls.__IP_GEOLOCATION_URL) as resp:
			if resp.status == 200:
				temp: dict = await resp.json()
				return f"{temp.get('city', None)}, {temp.get('regionName', None)}, {temp.get('country', None)}"
			else:
				return None

	@staticmethod
	def setup_log():
		logger: Logger = getLogger(ModularBotConst.BOT_NAME)
		logger.setLevel(INFO)

		handler = StreamHandler()
		handler.setFormatter(_ColourFormatter())
		logger.addHandler(handler)

	@staticmethod
	def simple_log(message: str):
		logger: Logger = getLogger(ModularBotConst.BOT_NAME)
		logger.info(message)

	@staticmethod
	async def send_response(
		interaction: Interaction,
		/,
		message: str = None,
		embed: Embed = None,
		emoji: Emoji | str = None,
		view: View = None,
		ephemeral: bool = False,
	) -> Message:
		msg: Message = None
		temp: str = str()

		if not view:
			view = View()

		def change_emoji(
			message: str, emoji: Emoji | str, ephemeral: bool = False
		) -> str:
			if isinstance(emoji, str) and ephemeral:
				return f"{emoji} {message}"

			if isinstance(emoji, Emoji):
				return f"{str(emoji)} {message}"

			return message

		try:
			temp = change_emoji(message, emoji, ephemeral)
			await interaction.response.send_message(
				temp, embed=embed, ephemeral=ephemeral, view=view
			)
			msg = await interaction.original_response()
		except InteractionResponded:
			msg = await interaction.original_response()
			flags: MessageFlags = msg.flags
			ephemeral = flags.ephemeral

			temp = change_emoji(message, emoji, ephemeral)

			msg = await interaction.followup.send(
				temp, embed=embed, ephemeral=ephemeral, view=view, wait=True
			)

		if emoji and not ephemeral:
			await msg.add_reaction(emoji)

		return msg

	@classmethod
	async def banner_creator(
		cls, username: str, avatar: str, is_welcome=True
	) -> BytesIO:
		if is_welcome:
			title: str = "Welcome".upper()
			mssg: str = GuildMessage.Banner.WELCOME.upper()
			banner: str = Image.open(path.join(cls.__ASSETS_DIR, "welcome.png"))

		else:
			title = "Goodbye".upper()
			mssg = GuildMessage.Banner.LEAVE.upper()
			banner: str = Image.open(path.join(cls.__ASSETS_DIR, "leaving.jpg"))

		profile_size: int = 2.2

		profile: Image = await load_image_async(avatar)
		background: Editor = Editor(banner)

		profile_size: int = int(background.image.size[1] // profile_size)
		wI, hI = background.image.size

		profile: Editor = (
			Editor(profile).resize((profile_size, profile_size)).circle_image()
		)
		bold_font: Font = Font(
			path=path.join(cls.__ASSETS_DIR, "gibson_bold.ttf"), size=hI // 5
		)
		regular_font: Font = Font(
			path=path.join(cls.__ASSETS_DIR, "gibson_bold.ttf"), size=hI // 10
		)
		small_font: Font = Font(
			path=path.join(cls.__ASSETS_DIR, "gibson_semibold.ttf"), size=hI // 15
		)

		x, y = ((wI - profile_size) // 2, (hI - profile_size) // 5)
		blur: Image = Image.new("RGBA", background.image.size)

		blurs: Editor = Editor(blur)
		blurs.ellipse(
			(x, y), profile_size, profile_size, outline="white", stroke_width=hI // 65
		).blur(amount=8)
		background.paste(blurs, (0, 0))
		background.paste(profile, (x, y))
		background.ellipse(
			(x, y), profile_size, profile_size, outline="white", stroke_width=hI // 65
		)

		blurs: Editor = Editor(blur)
		blurs.text(
			(wI // 2, hI // 8 * 5), title, color="black", font=bold_font, align="center"
		).blur(amount=8)
		background.paste(blurs, (0, 0))
		background.text(
			(wI // 2, hI // 8 * 5), title, color="white", font=bold_font, align="center"
		)

		blurs: Editor = Editor(blur)
		blurs.text(
			(wI // 2, hI // 5 * 4),
			username.upper(),
			color="black",
			font=regular_font,
			align="center",
		).blur(amount=8)
		background.paste(blurs, (0, 0))
		background.text(
			(wI // 2, hI // 5 * 4),
			username.upper(),
			color="white",
			font=regular_font,
			align="center",
		)

		blurs: Editor = Editor(blur)
		blurs.text(
			(wI // 2, hI // 10 * 9),
			mssg,
			color="black",
			font=small_font,
			align="center",
		).blur(amount=8)
		background.paste(blurs, (0, 0))
		background.text(
			(wI // 2, hI // 10 * 9),
			mssg,
			color="white",
			font=small_font,
			align="center",
		)

		return background.image_bytes
