from asyncio import sleep, wait, create_task
from io import BytesIO
from random import choice
from datetime import timedelta, datetime

from pytz import timezone

from discord.ext import commands, tasks
from discord import (
    Intents,
    Message,
    Embed,
    TextChannel,
    Role,
    Guild,
    Interaction,
    VoiceChannel,
    Member,
    errors,
    Member,
    File,
    Activity,
    ActivityType
)
from discord.app_commands import guild_only
from aiohttp import ClientSession

from wavelink import Node, Pool

from config import (
    GuildChannel,
    GuildRole,
    ModularBotConst,
    GuildMessage
)
from ModularBot import ModularUtil, Prayers


class ModularBotTask:

    _guild: Guild
    _role: Role

    session: ClientSession
    _praytime_message: Message
    _praytime_channel: TextChannel
    _praytimes: dict

    async def _begin_loop_task(self):

        if not self._pull_data.is_running():
            self._pull_data.start()

        if not self._prayer_time.is_running():
            self._prayer_time.start()

        if not self._lockdown_channel.is_running():
            self._lockdown_channel.start()

        if not self._change_activity.is_running():
            self._change_activity.start()

    async def __ramadhan_checker(self) -> None:
        self._is_ramadhan: bool = False

        if self._praytimes:
            time: datetime = ModularUtil.get_time()
            ramadhan_start: datetime = datetime.strptime(
                f"{self._praytimes['ramadhan']['start']} {time.strftime('%Y')}", "%B %d %Y")
            ramadhan_end: datetime = datetime.strptime(
                f"{self._praytimes['ramadhan']['end']} {time.strftime('%Y')}", "%B %d %Y")

            role: Role = self._guild.get_role(GuildRole.THE_MUSKETEER)
            channel: TextChannel = self.get_channel(
                GuildChannel.PRAYER_CHANNEL)
            overwrites = channel.overwrites_for(role)

            if ramadhan_start.date() <= time.date() < ramadhan_end.date():
                self._praytime_message = await self._praytime_channel.fetch_message(self._praytime_channel.last_message_id)

                if time.date() > self._praytime_message.created_at.astimezone(timezone(ModularBotConst.TIMEZONE)).date():
                    self._praytime_message = None

                self._is_ramadhan = True

            else:
                self._is_ramadhan = False
                self._praytime_message = None

            if not overwrites.view_channel is self._is_ramadhan:
                await channel.set_permissions(role, view_channel=True)

    @staticmethod
    async def _connect_nodes_lavalink(bot: commands.Bot) -> None:
        await bot.wait_until_ready()
        inactive_timeout: int = timedelta(minutes=30).total_seconds()

        nodes: list[Node] = [Node(uri=ModularBotConst.LAVALINK_SERVER, password=ModularBotConst.LAVALINK_PASSWORD, inactive_player_timeout=inactive_timeout)]

        await Pool.connect(nodes=nodes, client=bot, cache_capacity=20)

    @tasks.loop(hours=1)
    async def _pull_data(self) -> None:
        try:
            self._praytimes = await Prayers.get_prayertime(session=self.session)
            await self.__ramadhan_checker()
        except:
            pass

    @tasks.loop(seconds=30)
    async def _prayer_time(self) -> None:
        if self._praytimes:
            time: datetime = ModularUtil.get_time()

            if self._is_ramadhan:
                is_praytime: Embed | None = Prayers.prayers_generator(
                    praytimes=self._praytimes, time=time)

                if is_praytime is not None:
                    if self._praytime_message is not None:
                        await self._praytime_message.delete()

                    self._praytime_message = await self._praytime_channel.send(embed=is_praytime)

    @tasks.loop(seconds=30)
    async def _lockdown_channel(self) -> None:
        time: datetime = ModularUtil.get_time()

        async def _do_the_lockdown(view_channel: bool):
            for channel in self._guild.text_channels:
                channel: TextChannel = channel
                overwrites = channel.overwrites_for(self._role)

                if channel.is_nsfw() and channel.id != GuildChannel.BINCANG_HARAM_CHANNEL and overwrites.view_channel != view_channel:
                    await channel.set_permissions(self._role, view_channel=view_channel)
                    await sleep(2)

            return

        if self._praytimes and self._is_ramadhan:
            imsak: str = self._praytimes.get('Subuh')
            buka: str = self._praytimes.get('Maghrib')
            imsak: datetime = datetime.strptime(
                imsak, '%H:%M') - timedelta(minutes=10)
            buka: datetime = datetime.strptime(buka, '%H:%M')

            if time.time() >= buka.time():
                await _do_the_lockdown(view_channel=True)

            elif time.time() >= imsak.time() and time.time() < buka.time():
                await _do_the_lockdown(view_channel=False)

        else:
            if time.strftime('%A-%H') == ModularBotConst.LockDownTime.END:
                await _do_the_lockdown(view_channel=True)

            elif time.strftime('%A-%H') == ModularBotConst.LockDownTime.START:
                await _do_the_lockdown(view_channel=False)

    @tasks.loop(seconds=30)
    async def _change_activity(self: commands.Bot) -> None:
        the_musketter_count: int = len(
            self._guild.get_role(GuildRole.THE_MUSKETEER).members)

        async def a() -> None:
            await self.change_presence(activity=Activity(type=ActivityType.watching, name=f"{the_musketter_count} Hamba Allah"))

        async def b() -> None:
            await self.change_presence(activity=Activity(type=ActivityType.playing, name=f"bareng {the_musketter_count} Member"))

        async def c() -> None:
            await self.change_presence(activity=Activity(type=ActivityType.listening, name=f"@{ModularBotConst.BOT_NAME.replace(' ', '')}"))

        async def d() -> None:
            await self.change_presence(activity=Activity(type=ActivityType.competing, name=f"{ModularBotConst.SERVER_NAME.replace(' ', '')}"))

        await choice([a, b, c, d])()


class ModularBotBase(commands.Bot):

    _guild: Guild

    async def _help_embed(self) -> Embed:
        desc: str = f"Here's a few feature that's available on {ModularBotConst.SERVER_NAME}."
        embed: Embed = Embed(title=f"Menu {ModularBotConst.SERVER_NAME}",
                             description=desc, color=ModularUtil.convert_color(choice(ModularBotConst.Color.RANDOM)))

        for command in await self.tree.fetch_commands():
            if command.description:
                embed.add_field(name=f"**/{command.name}**",
                                value=command.description, inline=True)

            else:
                embed.add_field(name=f"**{command.name}**",
                                value="Access it through Apps Command", inline=True)
        embed.set_author(name=self.user.name,
                         icon_url=self.user.display_avatar)
        embed.set_footer(
            text=f" © {ModularBotConst.BOT_NAME} • If there is something wrong contact Admin")
        return embed

    async def _analytics(self) -> None:
        member_count: int = self._guild.member_count
        the_musketter_count: int = len(
            self._guild.get_role(GuildRole.THE_MUSKETEER).members)
        bot_count: int = len(self._guild.get_role(GuildRole.BOT).members)
        channel_count: int = len(self._guild.channels)
        role_count: int = len(self._guild.roles)

        voice_channels: list[VoiceChannel] = [self.get_channel(channel) for channel in [
            GuildChannel.MEMBER_ANALYTICS,
            GuildChannel.USER_ANALYTICS,
            GuildChannel.BOT_ANALYTICS,
            GuildChannel.CHANNEL_ANALYTICS,
            GuildChannel.ROLE_ANALYTICS
        ]]
        texts: list[str] = [
            f"Jumlah Member: {member_count}",
            f"Jumlah User: {the_musketter_count}",
            f"Jumlah Bot: {bot_count}",
            f"Jumlah Channel: {channel_count}",
            f"Jumlah Role: {role_count}"
        ]

        for channel, name in zip(voice_channels, texts):
            await wait([
                create_task(channel.edit(name=name)),
                create_task(sleep(ModularBotConst.REQUEST_LIMIT))
            ])


class ModularBotClient(ModularBotBase, ModularBotTask):

    def __init__(self) -> None:
        intents: Intents = Intents.default()
        intents.members = True
        intents.message_content = True

        self._praytime_channel: TextChannel = None
        self._praytimes: dict = None
        self._guild: Guild = None
        self._role: Role = None

        super().__init__(ModularBotConst.BOT_PREFIX, intents=intents)

        self.synced: bool = False

    async def on_guild_channel_delete(self, *_):
        await self._analytics()

    async def on_guild_channel_create(self, *_):
        await self._analytics()

    async def on_guild_role_delete(self, *_):
        await self._analytics()

    async def on_guild_role_create(self, *_):
        await self._analytics()

    async def on_member_join(self, member: Member) -> None:
        if not member.guild.id is self._guild.id:
            return

        welcome_banner: BytesIO = await ModularUtil.banner_creator(str(member.name), member.avatar.url)

        welcome_channel: TextChannel = self.get_channel(
            GuildChannel.WELCOME_CHANNEL)
        image_file: File = File(
            BytesIO(welcome_banner.getbuffer()), filename='image.png')
        await wait([
            create_task(welcome_channel.send(file=image_file)),
            create_task(self._analytics())
        ])

        try:
            return await member.send(GuildMessage.DM_MESSAGE)
        except errors.Forbidden:
            return

    async def on_member_remove(self, member: Member) -> None:
        leave_banner: BytesIO = await ModularUtil.banner_creator(str(member.name), member.avatar.url, is_welcome=False)

        leave_channel: TextChannel = self.get_channel(
            GuildChannel.GOODBYE_CHANNEL)
        image_file: File = File(
            BytesIO(leave_banner.getbuffer()), filename='image.png')

        return await wait([
            create_task(self._analytics()),
            create_task(leave_channel.send(file=image_file))
        ])

    async def on_message(self, message: Message) -> None:
        if message.author == self.user:
            return

        elif self.user.mentioned_in(message=message) and self.user.mention in message.content:
            await message.channel.send(embed=await self._help_embed())

        # TODO Need fix
        # if not message.channel.is_nsfw():
        #     react: str | Embed = Reaction.message_generator(message=message.clean_content)
        #     if not react:
        #         return
        #     await message.channel.send(embed=react) if isinstance(react, Embed) else await message.channel.send(react)

    async def setup_hook(self) -> None:
        self.session: ClientSession = ClientSession()
        self._praytime_message: Message = None
        ModularUtil.setup_log()

        self.loop.create_task(self._connect_nodes_lavalink(self))

        await self.load_extension('ModularBot.command')

        return await super().setup_hook()

    async def on_ready(self) -> None:
        ModularUtil.simple_log(f"Logged as {self.user.name}, {self.user.id}")

        self._guild = self.get_guild(ModularBotConst.SERVER_ID)
        self._role: Role = self._guild.get_role(GuildRole.MAGICIAN)
        self._praytime_channel: TextChannel = self.get_channel(
            GuildChannel.PRAYER_CHANNEL)

        if not self.synced:
            await self.tree.sync()
            self.synced = True

        await wait([
            create_task(self._begin_loop_task()),
            create_task(self._analytics())
        ])


bot: commands.Bot = ModularBotClient()


@bot.tree.command(name='help', description='Help user to find command')
@guild_only()
async def _help(interaction: Interaction) -> None:
    await ModularUtil.send_response(interaction, embed=await bot._help_embed(), ephemeral=True)


@bot.tree.command(name='ping', description='Ping how much latency with user')
@guild_only()
async def _ping(interaction: Interaction) -> None:
    where: str = await ModularUtil.get_geolocation(bot.session)
    message: str = "Something went wrong on our side."

    if where:
        message = f":cloud: Ping {round(bot.latency * 1000)}ms, bot server location {where} :earth_americas:"

    await ModularUtil.send_response(interaction, message=message, ephemeral=True)

bot.run(token=ModularBotConst.TOKEN.strip())
