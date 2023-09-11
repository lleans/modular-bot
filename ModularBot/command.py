from asyncio import wait, create_task
from datetime import timedelta

from discord import Interaction, Embed, Member, Role, Message
from discord.ext import commands
from discord.app_commands import ContextMenu, checks, Choice, AppCommandError, MissingPermissions, CheckFailure, describe, choices, command, guild_only
from discord.ui import View

from wavelink import Playable, Player, Playlist, QueueEmpty
from wavelink.ext.spotify import SpotifyTrack

from .util import ModularUtil
from .player import MusicPlayerBase, MusicPlayer, TrackType
from config import GuildRole, ModularBotConst


async def setup(bot: commands.Bot) -> None:
    await wait([
        create_task(bot.add_cog(Administrator(bot))),
        create_task(bot.add_cog(Multimedia(bot))),
        create_task(bot.add_cog(Playground(bot)))
    ])

    ModularUtil.simple_log("Cog loaded")


@guild_only()
class Administrator(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self._bot.tree.add_command(ContextMenu(
            name="Revoke Access Magician",
            callback=self._revoke_magician
        ))
        self._bot.tree.add_command(ContextMenu(
            name="Revoke Access From Server",
            callback=self._revoke_access
        ))
        super().__init__()

    @command(name='purge', description='To Purge message')
    @checks.has_permissions(manage_messages=True)
    async def _purge(self, interaction: Interaction, amount: int = 1) -> None:
        await interaction.response.defer(ephemeral=True)

        await interaction.channel.purge(limit=amount, check=lambda msg: not interaction.message)
        temp: Message = await ModularUtil.send_response(interaction, message=f"**{amount}** message purged", emoji="✅")
        await temp.delete(delay=3)

    @checks.has_permissions(administrator=True)
    async def _revoke_magician(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(timestamp=ModularUtil.get_time())
        embed.set_footer(
            text=f'From {interaction.user.name} ', icon_url=interaction.user.display_avatar)
        is_exist: Role = user.get_role(GuildRole.MAGICIAN)

        if is_exist:
            is_exist.delete()
            embed.color = ModularUtil.convert_color(
                ModularBotConst.COLOR['success'])
            embed.description = f"Succesfully revoke <@&{is_exist.name}> from user <@{user.name}>"
        else:
            embed.color = ModularUtil.convert_color(
                ModularBotConst.COLOR['failed'])
            embed.description = f"User <@{user.name}> does not have role <@&{is_exist.name}>"

        await ModularUtil.send_response(interaction, embed=embed)

    @checks.has_permissions(administrator=True)
    async def _revoke_access(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(timestamp=ModularUtil.get_time())
        embed.set_footer(
            text=f'From {interaction.user.name} ', icon_url=interaction.user.display_avatar)
        is_exist: Role = user.get_role(GuildRole.THE_MUSKETEER)

        if is_exist:
            is_exist.delete()
            embed.color = ModularUtil.convert_color(
                ModularBotConst.COLOR['success'])
            embed.description = f"Succesfully revoke <@&{is_exist.name}> from <@{user.name}>"
        else:
            embed.color = ModularUtil.convert_color(
                ModularBotConst.COLOR['failed'])
            embed.description = f"<@{user.name}> does not have role <@&{is_exist.name}>"

        await ModularUtil.send_response(interaction, embed=embed)

    async def cog_app_command_error(self, interaction: Interaction, error: AppCommandError) -> None:
        if isinstance(error, MissingPermissions):
            await ModularUtil.send_response(interaction, message="Missing Permission", emoji="❌")
        else:
            await ModularUtil.send_response(interaction, message=f"Unknown error, {Exception(error)}", emoji="❓")

        return await super().cog_app_command_error(interaction, error)


@guild_only()
class Playground(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self.ctx_menu = ContextMenu(
            name="Avatar",
            callback=self._avatar
        )
        self._bot.tree.add_command(self.ctx_menu)
        super().__init__()

    async def _avatar(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.COLOR['success']), timestamp=ModularUtil.get_time())
        embed.set_footer(
            text=f'From {interaction.user.name} ', icon_url=interaction.user.display_avatar)
        embed.set_image(
            url=user.guild_avatar.url if user.guild_avatar is not None else user.avatar.url)
        embed.description = f"Showing avatar of <@{user.id}>"

        await ModularUtil.send_response(interaction, embed=embed)

    async def cog_app_command_error(self, interaction: Interaction, error: AppCommandError) -> None:
        await ModularUtil.send_response(interaction, message=f"Unknown error, {Exception(error)}", emoji="❓")

        return await super().cog_app_command_error(interaction, error)


@guild_only()
class Multimedia(commands.Cog, MusicPlayer):

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        super().__init__()

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        if not self._timeout_check.is_running():
            self._timeout_check.start()

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.command is not (self._queue):
            self._record_timestamp(guild_id=interaction.guild_id,
                                   interaction=interaction)

        return super().interaction_check(interaction)

    @command(name="join", description="Join an voice channel")
    @MusicPlayerBase._is_user_join_checker()
    async def _join(self, interaction: Interaction) -> None:
        await wait([
            create_task(self.join(interaction)),
            create_task(ModularUtil.send_response(
                interaction, message="Joined", emoji="✅", ephemeral=True))
        ])

    @command(name="leave", description="Leave the voice channel")
    @MusicPlayerBase._is_user_join_checker()
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    async def _leave(self, interaction: Interaction) -> None:
        await wait([
            create_task(self.leave(interaction)),
            create_task(ModularUtil.send_response(
                interaction, message="Succesfully Disconnected ", emoji="✅", ephemeral=True))
        ])

    @command(name="search", description="Search your track by query")
    @describe(query="Track keyword(You can pass through playlist to pick on it)",
              source="Get track from different source(Default is Youtube, Spotify will automatically convert into Youtube)",
              autoplay="Autoplay recomendation from you've been played(Soundcloud not supported)")
    @choices(autoplay=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)])
    @MusicPlayerBase._is_user_join_checker()
    @MusicPlayerBase._is_user_allowed()
    async def _search(self, interaction: Interaction, query: str, source: TrackType = TrackType.YOUTUBE, autoplay: Choice[int] = 0) -> None:
        await interaction.response.defer()
        convert_autoplay: bool = False
        view: View = View()
        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.COLOR['failed']))

        autoplay = Choice(
            name="None", value=None) if autoplay == 0 else autoplay

        if autoplay.value == None:
            convert_autoplay = None

        if autoplay.value == 1:
            convert_autoplay = True

        try:
            embed, view = await self.search(query=query, user=interaction.user, source=source, autoplay=convert_autoplay)
        except IndexError:
            embed.description = "❌ Track not found, check your keyword or source"

        await ModularUtil.send_response(interaction, embed=embed, view=view)

    @command(name="play", description="To play a track from Youtube/Soundcloud/Spotify")
    @describe(query="Youtube/Soundcloud/Spotify link or keyword",
              source="Get track from different source(Default is Youtube, Spotify will automatically convert into Youtube)",
              autoplay="Autoplay recomendation from you've been played(Soundcloud not supported)",
              force_play="Force to play the track(Previous queue still saved)",
              put_front="Put track on front. Will play after current track end")
    @choices(autoplay=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)],
        force_play=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)],
        put_front=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)])
    @MusicPlayerBase._is_user_join_checker()
    @MusicPlayerBase._is_user_allowed()
    async def _play(self, interaction: Interaction, query: str, source: TrackType = TrackType.YOUTUBE, autoplay: Choice[int] = 0, force_play: Choice[int] = 0, put_front: Choice[int] = 0) -> None:
        await interaction.response.defer()

        autoplay = Choice(
            name="None", value=None) if autoplay == 0 else autoplay
        force_play = Choice(
            name="None", value=None) if force_play == 0 else force_play
        put_front = Choice(
            name="None", value=None) if put_front == 0 else put_front

        convert_autoplay: bool = False
        convert_force_play: bool = False
        convert_put_front: bool = False
        track: Playlist | Playable | SpotifyTrack = None
        is_playlist = is_queued = False
        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.COLOR['failed']), description="❌ Track not found\nIf you're using link, check if it's supported or not")

        if autoplay.value == None:
            convert_autoplay = None

        if autoplay.value == 1:
            convert_autoplay = True

        if force_play.value == 1:
            convert_force_play = True

        if put_front.value == 1:
            convert_put_front = True

        try:
            track, is_playlist, is_queued = await self.play(interaction,
                                                            query=query,
                                                            source=source,
                                                            autoplay=convert_autoplay,
                                                            force_play=convert_force_play,
                                                            put_front=convert_put_front)

            embed = await self._play_response(interaction.user, track=track, is_playlist=is_playlist, is_queued=is_queued, is_put_front=convert_put_front or convert_force_play, is_autoplay=convert_autoplay, raw_uri=query)
        except IndexError:
            pass

        await ModularUtil.send_response(interaction, embed=embed)

    @command(name="queue", description="Show current player queue")
    @describe(is_history="Show player history instead queue")
    @choices(is_history=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)])
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    async def _queue(self, interaction: Interaction, is_history: Choice[int] = 0) -> None:
        await interaction.response.defer(ephemeral=True)

        is_history = Choice(
            name="None", value=None) if is_history == 0 else is_history

        convert_is_history: bool = False
        embed: Embed = Embed(description="📪 No tracks found", color=ModularUtil.convert_color(
            ModularBotConst.COLOR['failed']))
        view: View = None

        if is_history.value == 1:
            convert_is_history = True

        try:
            embed, view = await self.queue(interaction, is_history=convert_is_history)
        except QueueEmpty:
            pass

        await ModularUtil.send_response(interaction, embed=embed, view=view)

    @command(name="skip", description="Skip current track")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _skip(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        embed: Embed = Embed(
            description="⏯️ Skipped",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )

        await wait([
            create_task(self.skip(interaction)),
            create_task(ModularUtil.send_response(interaction, embed=embed))
        ])

    @command(name="jump", description="Jump on specific track(Put selected track into front)")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _jump(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        view: View = View()
        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.COLOR['failed']))

        try:
            embed, view = await self.jump(interaction)
        except IndexError:
            embed.description = "📪 Queue is empty"

        await create_task(ModularUtil.send_response(interaction, embed=embed, view=view))

    @command(name="previous", description="Play previous track(All queue still saved)")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _previous(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        embed: Embed = Embed(
            description="⏮️ Previous",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['failed'])
        )

        was_allowed: bool = await self.previous(interaction)

        if not was_allowed:
            embed.description = "📪 History is empty"

        await create_task(ModularUtil.send_response(interaction, embed=embed))

    @command(name="stop", description="Stop anything(This will reset player back to initial state)")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _stop(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        embed: Embed = Embed(
            description="⏹️ Stopped",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['failed'])
        )

        await wait([
            create_task(self.stop(interaction)),
            create_task(ModularUtil.send_response(interaction, embed=embed))
        ])

    @command(name="clear", description="Clear current queue(This will also disable Autoplay and any loop state)")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _clear(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        embed: Embed = Embed(
            description="✅ Cleared",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )

        self.clear(interaction)
        await ModularUtil.send_response(interaction, embed=embed)

    @command(name="shuffle", description="Shuffle current queue")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _shuffle(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        embed: Embed = Embed(
            description="🔀 Shuffled",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )

        self.shuffle(interaction)
        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(guild_id=interaction.guild_id))
        ])

    @command(name="now_playing", description="Show current playing track")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _now_playing(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        player: Player = None
        time: int = int()

        player, time = self.now_playing(interaction)

        embed: Embed = Embed(
            title="🎶 Now Playing",
            description=f"""**[{player.current.title}]({player.current.uri}) - {self._parseSec(player.current.duration)}** 
            \n** {str(timedelta(seconds=time)).split('.')[0]} left**""",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['play'])
        )

        await ModularUtil.send_response(interaction, embed=embed)

    @command(name="loop", description="Loop current track")
    @describe(is_queue="Loop current player queue, instead current track(History are included)")
    @choices(is_queue=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)])
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _loop(self, interaction: Interaction, is_queue: Choice[int] = 0) -> None:
        await interaction.response.defer()
        loop = False

        is_queue = Choice(
            name="None", value=None) if is_queue == 0 else is_queue

        convert_is_queue: bool = False
        embed: Embed = Embed(
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )

        if is_queue.value == 1:
            convert_is_queue = True

        loop = self.loop(interaction, is_queue=convert_is_queue)

        if not convert_is_queue:
            embed.description = "✅ Loop Track" if loop else "✅ Unloop Track"
        else:
            embed.description = "✅ Loop Queue" if loop else "✅ Unloop Queue"

        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(guild_id=interaction.guild_id))
        ])

    @command(name="pause", description="Pause current track")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _pause(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        embed: embed = Embed(
            description="⏸️ Paused",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )

        await wait([
            create_task(self.pause(interaction)),
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(guild_id=interaction.guild_id))
        ])

    @command(name="resume", description="Resume current track")
    @MusicPlayerBase._is_client_exist()
    @MusicPlayerBase._is_user_allowed()
    @MusicPlayerBase._is_playing()
    async def _resume(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(
            description="▶️ Resumed",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )

        res: bool = await self.resume(interaction)

        if not res:
            return await ModularUtil.send_response(interaction, message="Nothing is paused", emoji="📭")

        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(guild_id=interaction.guild_id))
        ])

    async def cog_app_command_error(self, interaction: Interaction, error: AppCommandError) -> None:
        if not isinstance(error, CheckFailure):
            await ModularUtil.send_response(interaction, message=f"Unknown error, {Exception(error)}", emoji="❓")

        return await super().cog_app_command_error(interaction, error)
