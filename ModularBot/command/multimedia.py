from asyncio import wait, create_task

from discord import Interaction, Embed
from discord.ext import commands
from discord.app_commands import (
    Choice,
    CheckFailure,
    AppCommandError,
    describe,
    choices,
    command,
    guild_only
)
from discord.ui import View

from wavelink import Playable, Playlist, QueueEmpty, LavalinkLoadException

from ..util import ModularUtil
from ..player import (
    TrackPlayerDecorator,
    TrackPlayer,
    TrackType,
    FiltersTemplate
)
from config import ModularBotConst


@guild_only()
class Multimedia(commands.Cog, TrackPlayer):

    def __init__(self, bot: commands.Bot) -> None:
        self._bot = bot
        super().__init__()

    @command(name="join", description="Join an voice channel")
    @TrackPlayerDecorator.is_user_join_checker()
    async def _join(self, interaction: Interaction) -> None:
        await wait([
            create_task(self.join(interaction)),
            create_task(ModularUtil.send_response(
                interaction, message="Joined", emoji="✅", ephemeral=True))
        ])

    @command(name="leave", description="Leave the voice channel")
    @TrackPlayerDecorator.is_user_join_checker()
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    async def _leave(self, interaction: Interaction) -> None:
        await wait([
            create_task(self.leave(interaction)),
            create_task(ModularUtil.send_response(
                interaction, message="Succesfully Disconnected ", emoji="✅", ephemeral=True))
        ])

    @command(name="search", description="Search your track by query")
    @describe(query="YouTube/Soundcloud/Spotify link or keyword",
              source="Get track from different source(Default is YouTube, Spotify will automatically convert into YouTube/YouTubeMusic)",
              autoplay="Autoplay recomendation from you've been played(Soundcloud not supported, this will create autoplay queue which different with player queue)",
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
    @TrackPlayerDecorator.is_user_join_checker()
    @TrackPlayerDecorator.is_user_allowed()
    async def _search(self, interaction: Interaction, query: str, source: TrackType = TrackType.YOUTUBE,
                      autoplay: Choice[int] = 0, force_play: Choice[int] = 0, put_front: Choice[int] = 0) -> None:
        await interaction.response.defer()

        autoplay = Choice(
            name="None", value=None) if autoplay == 0 else autoplay

        view: View = None
        convert_autoplay: bool = False
        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.Color.FAILED))

        if isinstance(force_play, Choice):
            force_play = force_play.value

        if isinstance(put_front, Choice):
            put_front = put_front.value

        if autoplay.value is None:
            convert_autoplay = None

        elif autoplay.value == 1:
            convert_autoplay = True

        try:
            embed, view = await self.search(
                interaction,
                query=query,
                source=source,
                autoplay=convert_autoplay,
                force_play=bool(force_play),
                put_front=bool(put_front)
            )
        except IndexError:
            embed.description = "❌ Track not found, check your keyword or source"
        except LavalinkLoadException:
            embed.description = "💥 Something went wrong while loading track, try again"

        await ModularUtil.send_response(interaction, embed=embed, view=view)

    @command(name="play", description="To play a track from YouTube/Soundcloud/Spotify")
    @describe(query="YouTube/Soundcloud/Spotify link or keyword",
              source="Get track from different source(Default is YouTube, Spotify will automatically convert into YouTube/YouTubeMusic)",
              autoplay="Autoplay recomendation from you've been played(Soundcloud not supported, this will create autoplay queue which different with player queue)",
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
    @TrackPlayerDecorator.is_user_join_checker()
    @TrackPlayerDecorator.is_user_allowed()
    async def _play(self, interaction: Interaction, query: str, source: TrackType = TrackType.YOUTUBE,
                    autoplay: Choice[int] = 0, force_play: Choice[int] = 0, put_front: Choice[int] = 0) -> None:
        await interaction.response.defer()

        autoplay = Choice(
            name="None", value=None) if autoplay == 0 else autoplay

        convert_autoplay: bool = False
        track: Playlist | Playable = None
        is_playlist = is_queued = False
        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.Color.FAILED))

        if isinstance(force_play, Choice):
            force_play = force_play.value

        if isinstance(put_front, Choice):
            put_front = put_front.value

        if autoplay.value is None:
            convert_autoplay = None

        elif autoplay.value == 1:
            convert_autoplay = True

        try:
            track, is_playlist, is_queued = await self.play(
                interaction,
                query=query,
                source=source,
                autoplay=convert_autoplay,
                force_play=bool(force_play),
                put_front=bool(put_front)
            )

            embed = await self._play_response(
                interaction.user,
                track,
                is_playlist=is_playlist,
                is_queued=is_queued,
                is_put_front=bool(put_front) or bool(force_play),
                is_autoplay=convert_autoplay
            )
        except IndexError:
            embed.description = "❌ Track not found, check your keyword or source"
        except LavalinkLoadException:
            embed.description = "💥 Something went wrong while loading track, try again"

        await ModularUtil.send_response(interaction, embed=embed)

    @command(name="queue", description="Show current player queue")
    @describe(is_history="Show player history instead queue")
    @choices(is_history=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)])
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    async def _queue(self, interaction: Interaction, is_history: Choice[int] = 0) -> None:
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(description="📪 No tracks found", color=ModularUtil.convert_color(
            ModularBotConst.Color.FAILED))
        view: View = None

        if isinstance(is_history, Choice):
            is_history = is_history.value

        try:
            embed, view = await self.queue(interaction, is_history=bool(is_history))
        except QueueEmpty:
            pass

        await ModularUtil.send_response(interaction, embed=embed, view=view)

    @command(name="skip", description="Skip current track(prioritized player queue then autoplay queue)")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _skip(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        embed: Embed = Embed(
            description="⏯️ Skipped",
            color=ModularUtil.convert_color(ModularBotConst.Color.SUCCESS)
        )

        await wait([
            create_task(self.skip(interaction)),
            create_task(ModularUtil.send_response(interaction, embed=embed))
        ])

    @command(name="jump", description="Jump on specific track(put selected track into front)")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _jump(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        view: View = None
        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.Color.FAILED))

        try:
            embed, view = await self.jump(interaction)
        except IndexError:
            embed.description = "📪 Queue is empty"

        await create_task(ModularUtil.send_response(interaction, embed=embed, view=view))

    @command(name="previous", description="Play previous track")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _previous(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        was_allowed = was_on_loop = False

        embed: Embed = Embed(
            description="⏮️ Previous",
            color=ModularUtil.convert_color(ModularBotConst.Color.SUCCESS)
        )

        was_allowed, was_on_loop = await self.previous(interaction)

        if not was_allowed:
            embed.description = "📪 History is empty" if not was_on_loop else "🔁 Player is on loop"
            embed.color = ModularUtil.convert_color(
                ModularBotConst.Color.FAILED)

        await create_task(ModularUtil.send_response(interaction, embed=embed))

    @command(name="stop", description="Stop anything(this will reset player back to default)")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _stop(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        embed: Embed = Embed(
            description="⏹️ Stopped",
            color=ModularUtil.convert_color(ModularBotConst.Color.FAILED)
        )

        await wait([
            create_task(self.stop(interaction)),
            create_task(ModularUtil.send_response(interaction, embed=embed))
        ])

    @command(name="clear", description="Clear current queue(this will also disable Autoplay and any loop state)")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _clear(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        embed: Embed = Embed(
            description="✅ Cleared",
            color=ModularUtil.convert_color(ModularBotConst.Color.SUCCESS)
        )

        self.clear(interaction)
        await ModularUtil.send_response(interaction, embed=embed)

    @command(name="shuffle", description="Shuffle current queue")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _shuffle(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        embed: Embed = Embed(
            description="🔀 Shuffled",
            color=ModularUtil.convert_color(ModularBotConst.Color.SUCCESS)
        )

        self.shuffle(interaction)
        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(interaction=interaction))
        ])

    @command(name="now_playing", description="Show current playing track")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _now_playing(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        embed = self.now_playing(interaction)

        await ModularUtil.send_response(interaction, embed=embed)

    @command(name="lyrics", description="Get lyrics of the tracks(fetched from LyricFind)")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _lyrics(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        view: View = None
        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.Color.FAILED))

        embed, view = await self._lyrics_finder(interaction=interaction)

        await ModularUtil.send_response(interaction, embed=embed, view=view)

    @command(name="loop", description="Loop current Track/Playlist")
    @describe(is_queue="Loop current player queue, instead current track(if player queue empty, loop through history)")
    @choices(is_queue=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)])
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _loop(self, interaction: Interaction, is_queue: Choice[int] = 0) -> None:
        await interaction.response.defer()
        embed: Embed = Embed(
            color=ModularUtil.convert_color(ModularBotConst.Color.SUCCESS)
        )
        conv_is_queue: bool = False

        if isinstance(is_queue, Choice):
            conv_is_queue = bool(is_queue.value)

        loop: bool = self.loop(interaction, is_queue=bool(conv_is_queue))

        if conv_is_queue:
            embed.description = "✅ Loop Queue" if loop else "✅ Unloop Queue"

        else:
            embed.description = "✅ Loop Track" if loop else "✅ Unloop Track"

        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(interaction=interaction))
        ])

    @command(name="pause", description="Pause current track")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _pause(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(
            description="⏸️ Paused",
            color=ModularUtil.convert_color(ModularBotConst.Color.SUCCESS)
        )

        await self.pause(interaction)

        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(interaction=interaction))
        ])

    @command(name="resume", description="Resume current track")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _resume(self, interaction: Interaction) -> None:
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(
            description="▶️ Resumed",
            color=ModularUtil.convert_color(ModularBotConst.Color.SUCCESS)
        )

        await self.resume(interaction)

        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(interaction=interaction))
        ])

    @command(name="filters", description="List of filter that can be appllied(checkout '/filters_template' for easier use)")
    @describe(karaoke="Karaoke effect",
              rotation="Rotation effect(8D Audio)",
              tremolo="Tremolo effect(Electric guitar effect)",
              vibrato="Vibrato effect")
    @choices(karaoke=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)],
        rotation=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)],
        tremolo=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)],
        vibrato=[
        Choice(name='True', value=1),
        Choice(name='False', value=0)])
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _filters(self, interaction: Interaction, karaoke: Choice[int] = 0, rotation: Choice[int] = 0, tremolo: Choice[int] = 0, vibrato: Choice[int] = 0) -> None:
        await interaction.response.defer()
        conv_karak: bool = None
        conv_rotat: bool = None
        conv_tremo: bool = None
        conv_vibra: bool = None

        if isinstance(karaoke, Choice):
            conv_karak = bool(karaoke.value)

        if isinstance(rotation, Choice):
            conv_rotat = bool(rotation.value)

        if isinstance(tremolo, Choice):
            conv_tremo = bool(tremolo.value)

        if isinstance(vibrato, Choice):
            conv_vibra = bool(vibrato.value)

        embed: Embed = await self.filters(interaction, karaoke=conv_karak, rotation=conv_rotat, tremolo=conv_tremo, vibrato=conv_vibra)

        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(interaction=interaction))
        ])

    @command(name="filters_template", description="List of filters template that can be applied(by toggling this, will reset other filters)")
    @describe(effect="Toggle template filters")
    @TrackPlayerDecorator.is_client_exist()
    @TrackPlayerDecorator.is_user_allowed()
    @TrackPlayerDecorator.is_playing()
    async def _filters_template(self, interaction: Interaction, effect: FiltersTemplate) -> None:
        await interaction.response.defer()

        embed: Embed = await self.filters_template(interaction, effect=effect)

        await wait([
            create_task(ModularUtil.send_response(interaction, embed=embed)),
            create_task(self._update_player(interaction=interaction))
        ])

    async def cog_app_command_error(self, interaction: Interaction, error: AppCommandError) -> None:
        if not isinstance(error, CheckFailure):
            await ModularUtil.send_response(interaction, message=f"Unknown error, {Exception(error)}", emoji="❓")

        return await super().cog_app_command_error(interaction, error)
