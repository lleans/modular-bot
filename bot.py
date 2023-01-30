from asyncio import wait, ensure_future
from io import BytesIO
from re import search, IGNORECASE
from random import choice
from typing import Union
from os import getenv

from datetime import timedelta, datetime
from discord.ext import commands, tasks
from discord import Intents, Message, Embed, TextChannel, Role, Guild, Interaction, VoiceChannel, Member, errors, Member, File, User, Activity, ActivityType, Object
from aiohttp import ClientSession
from wavelink.pool import NodePool

from const import GuildChannel, GuildRole, ModularBotConst, GuildMessage
from ModularBot import ModularUtil, Prayers, Reaction


class ModularBotTask:

    async def _begin_loop_task(self):        
        self._prayer_time.start()
        self._lockdown_channel.start()
        self._pull_data.start()

    @staticmethod
    async def _connect_nodes(bot: commands.Bot) -> None:
        await bot.wait_until_ready()
        await NodePool.create_node(
            bot=bot,
            host='lavalink',
            port=2333,
            password='youshallnotpass'
        )

        print("Wavelink connected")

    @tasks.loop(hours=12)
    async def _pull_data(self) -> None:
        # Pullin data from API
        self._praytimes = await Prayers.get_prayertime(session=self.session)

    @tasks.loop(seconds=30)
    async def _prayer_time(self) -> None:
        message: Message = None
        time: datetime = ModularUtil.get_time()
        
        is_praytime: Union[Embed, None] = Prayers.prayers_generator(praytimes=self._praytimes, time=time)
        if is_praytime is not None:
            channel: TextChannel = self.get_channel(GuildChannel.PRAYER_CHANNEL)

            if message is not None:
                await message.delete()
                
            message = await channel.send(embed=is_praytime)

    @tasks.loop(seconds=30)
    async def _lockdown_channel(self) -> None:
        time: datetime = ModularUtil.get_time()
        role: Role = self._guild.get_role(GuildRole.MAGICIAN)

        if time.strftime('%A-%H') == "Friday-21":
            for channel in self._guild.text_channels:
                if channel.is_nsfw() and channel.id != GuildChannel.BINCANG_HARAM_CHANNEL:
                    return await channel.set_permissions(role, view_channel=True)
        elif time.strftime('%A-%H') == "Friday-09":
            for channel in self._guild.text_channels:
                if channel.is_nsfw() and channel.id != GuildChannel.BINCANG_HARAM_CHANNEL:
                    return await channel.set_permissions(role, view_channel=False)
        else:
            ramadhan_start: datetime = datetime.strptime(self._praytimes['ramadhan']['start'], "%B %d")
            ramadhan_end: datetime = datetime.strptime(self._praytimes['ramadhan']['end'], "%B %d")
            if ramadhan_start.date() <= time.date() < ramadhan_end.date():
                for key, val in self._praytimes:
                    timestrip = datetime.strptime(val, '%H:%M')
                    timestrip = timestrip - timedelta(minutes=10)

                    if timestrip.strftime('%H:%M') == val and (key == "Subuh" or key == "Fajr"):
                        for channel in self._guild.text_channels:
                            if channel.is_nsfw() and channel.id != GuildChannel.BINCANG_HARAM_CHANNEL:
                                return await channel.set_permissions(role, view_channel=False)

class ModularBotBase:


    async def _help_embed(self) -> Embed:
        desc: str = f"Berikut beberapa fitur yang tersedia di server {ModularBotConst.SERVER_NAME}."
        e: Embed = Embed(title=f"Menu {ModularBotConst.SERVER_NAME}",
                        description=desc, color=ModularUtil.convert_color(choice(ModularBotConst.COLOR['random_array'])))
        
        for c in await self.tree.fetch_commands():
            e.add_field(name=f"**/{c.name}**", value=c.description, inline=True)
        e.set_author(name=self.user.name, icon_url=self.user.display_avatar)
        e.set_footer(
            text=f" © {ModularBotConst.BOT_NAME} • Development mode, if there is something wrong contact Admin")
        return e
    
    async def anlytics(self) -> None:
        member_count: int = self._guild.member_count
        the_musketter_count: int = len(self._guild.get_role(GuildRole.THE_MUSKETEER).members)
        bot_count: int = len(self._guild.get_role(GuildRole.BOT).members)
        channel_count: int = len(self._guild.channels)
        role_count: int = len(self._guild.roles)

        member_channel_edit: VoiceChannel = self.get_channel(GuildChannel.MEMBER_ANALYTICS)
        user_channel_edit: VoiceChannel = self.get_channel(GuildChannel.USER_ANALYTICS)
        bot_channel_edit: VoiceChannel = self.get_channel(GuildChannel.BOT_ANALYTICST)
        channel_channel_edit: VoiceChannel = self.get_channel(GuildChannel.CHANNEL_ANLYTICS)
        role_channel_edit: VoiceChannel = self.get_channel(GuildChannel.ROLE_ANLYTICS)

        return await wait([member_channel_edit.edit(name=f"Jumlah Member: {member_count}"),
            user_channel_edit.edit(name=f"Jumlah User: {the_musketter_count}"),
            bot_channel_edit.edit(name=f"Jumlah BOT: {bot_count}"),
            channel_channel_edit.edit(name=f"Jumlah Channel: {channel_count}"),
            role_channel_edit.edit(name=f"Jumlah Role: {role_count}")
        ])



class ModularBotClient(commands.Bot, ModularBotBase, ModularBotTask):

    def __init__(self) -> None:
        intents: Intents = Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__("!pkyyk", intents=intents)

        self.synced: bool = False
        self._guild: Guild = None
        

    async def on_member_join(self, member: Member) -> None:
        if member.guild.id != self.get_guild(self._guild):
            return

        await self.anlytics()
        welcome_banner: BytesIO = await ModularUtil.banner_creator(member.name, member.avatar.url)

        welcome_channel: TextChannel = self.get_channel(GuildChannel.WELCOME_CHANNEL)
        image_file: File = File(BytesIO(welcome_banner.getbuffer()), filename='image.png')

        try:
            return await wait([ensure_future(welcome_channel.send(file=image_file)), 
            ensure_future(member.send(GuildMessage.DM_MESSAGE))])
        except errors.Forbidden:
            pass

    async def on_member_remove(self, member: Member) -> None:
        await self.anlytics()
        leave_banner: BytesIO = await ModularUtil.banner_creator(member.name, member.avatar.url, is_welcome=False)

        leave_channel: TextChannel = self.get_channel(GuildChannel.GOODBYE_CHANNEL)
        image_file: File = File(BytesIO(leave_banner.getbuffer()), filename='image.png')

        return await leave_channel.send(file=image_file)

    async def on_message(self, message: Message) -> None:
        if message.author == self.user:
            return
        elif self.user.mentioned_in(message=message) and search(rf"<@{self.user.id}>|<@!{self.user.id}>", message.content, flags=IGNORECASE):
            await message.channel.send(embed=await self._help_embed())

        # Need fix 
        await message.channel.send(Reaction.message_generator(message=message.clean_content))

    async def setup_hook(self) -> None:
        self.session: ClientSession = ClientSession()
        self._praytimes = await Prayers.get_prayertime(session=self.session)
        self.loop.create_task(self._connect_nodes(self))

        await self.load_extension('ModularBot.command')

        return await super().setup_hook()

    async def on_ready(self) -> None:
        print(f"Logged as {self.user.name}, {self.user.id}")
        self._guild = self.get_guild(ModularBotConst.SERVER_ID)

        await self._begin_loop_task()

        if not self.synced:
            await self.tree.sync()
            self.synced = True

        await wait([ensure_future(self.anlytics()),
            ensure_future(self.change_presence(activity=Activity(type=ActivityType.watching, name=f"{len(self._guild.get_role(GuildRole.THE_MUSKETEER).members)} Hamba Allah")))
        ])


bot: commands.Bot = ModularBotClient()

@bot.tree.command(name='help', description='Help user to find command')
async def _help(interaction: Interaction) -> None:
    await interaction.response.send_message(embed=await bot._help_embed())

@bot.tree.command(name='ping', description='Ping how much latency with user')
async def _ping(interaction: Interaction) -> None:
    where: str = await ModularUtil.get_geolocation(bot.session)
    await interaction.response.send_message(f":cloud: Ping {round(bot.latency * 1000)}ms, server location {where} :earth_americas:")

bot.run(open("TOKEN").readline() or getenv("TOKEN").strip())
