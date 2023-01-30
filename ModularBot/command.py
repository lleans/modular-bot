
from asyncio import wait, ensure_future
from random import shuffle
from datetime import timedelta
from typing import List

from discord import app_commands, Interaction, VoiceClient, Embed, Message, TextChannel
from discord.ext import commands
from wavelink.player import Player
from wavelink.tracks import YouTubePlaylist, YouTubeTrack, Track
from wavelink.pool import NodePool
from wavelink.abc import Playable

from .util import ModularUtil
from const import Expression, GuildRole, ModularBotConst


async def setup(bot: commands.Bot) -> None:
    await wait([
        bot.add_cog(Administrator(bot=bot)),
        bot.add_cog(Multimedia(bot=bot))
    ])

    print("Cog loaded")

async def _handling_error(interaction: Interaction, resp: str) -> None:
    if not interaction.response.is_done():
        await interaction.response.send_message(resp)
    else:
        await interaction.followup.send(resp)


class Administrator(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self._muted: str = "Muted"
        super().__init__()

    @app_commands.command(name='purge', description='To Purge message')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def _purge(self, interaction: Interaction, amount: int = 1) -> None:
        await interaction.response.defer(ephemeral=True)
        await interaction.channel.purge(limit=amount, check=lambda msg: not interaction.message)
        temp = await interaction.followup.send(f" ✅ **{amount}** pesan di hapus")
        await temp.delete(delay=3)

    async def cog_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await _handling_error(interaction=interaction, resp='❌ Missing Permission')
        else:
            await _handling_error(interaction=interaction, resp=f'❌ Uknown error, {Exception(error)}')

        return await super().cog_app_command_error(interaction, error)


class Multimedia(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot

        self._guild_message: dict = {}
        super().__init__()

    @staticmethod
    def parseSec(sec: int) -> str:
        sec: int = round(sec)
        m, s = divmod(sec, 60)
        h, m = divmod(m, 60)
        if sec > 3600:
            return f'{h:d}h {m:02d}m {s:02d}s'
        else:
            return f'{m:02d}m {s:02d}s'

    async def cog_app_command_error(self, interaction: Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await _handling_error(interaction=interaction, resp='❌ Missing Permission')
        else:
            await _handling_error(interaction=interaction, resp=f'❌ Uknown error, {Exception(error)}')

        return await super().cog_app_command_error(interaction, error)

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: Player, track: Track) -> None:
        channel: TextChannel = self.bot.get_channel(self._guild_message[player.guild.id]['channel'])
        embed = Embed(
            title="Now Playing",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['queue']),
            description=f"**[{track.title}]({track.uri}) - {self.parseSec(track.duration)}**"
        )
        message: Message = await channel.send(embed=embed)
        self._guild_message[player.guild.id]['message'] = message.id

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: Player, track: Track) -> None:
        channel: TextChannel = self.bot.get_channel(self.guild_id[player.guild.id])
        message: Message = await channel.fetch_message(self._guild_message[Interaction.guild_id]['message'])
        await message.delete()
        
        try:
            if player.loop is True:
                player.queue.put_at_front(track)
        except:
            if player.qloop is True and not player.loop:
                await player.queue.put_wait(track)

        if not player.queue.is_empty:
            next_track: Playable = player.queue.get()
            await player.play(next_track)

    @app_commands.command(name="join", description="Join an voice channel")
    async def _join(self, interaction: Interaction) -> None:
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ Cannot Join. \nPlease Join Voice channel first!!", ephemeral=True)

        voice_client: VoiceClient = interaction.user.guild.voice_client        
        channel: Player = interaction.user.voice.channel 
        if not voice_client:
            await wait([ensure_future(channel.connect(cls=Player)),
                interaction.response.send_message("✅ Joined")
            ])
        else:
            await interaction.response.send_message("❌ Cannot Join. \nThe bot is already connected to a voice channel!!", ephemeral=True)

    @app_commands.command(name="leave", description="Leave the voice channel")
    async def _leave(self, interaction: Interaction) -> None:
        voice_client: VoiceClient = interaction.user.guild.voice_client
        if voice_client:
            return await interaction.response.send_message("❌ Not joined a voice channel", ephemeral=True)

        await voice_client.disconnect()

        del self.guild_id[interaction.guild.id]
        await interaction.response.send_message("✅ Succesfully Disconnected ", ephemeral=True)

    @app_commands.command(name="play", description="To play a song from Youtube")
    async def _play(self, interaction: Interaction, query: str) -> None:
        await interaction.response.defer()
        if not interaction.user.voice:
            return await interaction.followup.send("❌ Cannot Join. \nPlease Join Voice channel first!!", ephemeral=True)

        if not interaction.user.guild.voice_client:
            voice_client: Player = await interaction.user.voice.channel.connect(cls=Player)
        else:
            voice_client: Player = interaction.user.guild.voice_client

        self._guild_message[interaction.guild_id]['channel'] = interaction.channel_id
        embed: Embed = Embed(color=ModularUtil.convert_color(ModularBotConst.COLOR['success']), timestamp=ModularUtil.get_time().strftime("%d %B %Y"))
        embed.set_footer(text=f'From {interaction.user} ', icon_url=interaction.user.display_avatar)

        if not query.startswith("http://"):
            search: Playable = await YouTubeTrack.search(query=query, return_first=True)
        
        if query.startswith("http://") and "playlist?" in query:
            playlist: List[YouTubePlaylist] = await YouTubePlaylist.search(query=query)
            for search in playlist.tracks:
                await voice_client.queue.put_wait(search)
            if not voice_client.is_playing():
                search: Playable = await voice_client.queue.get_wait()
                await voice_client.play(search)
                embed.description = f"✅ Queued - {len(playlist.tracks)} tracks from ** [{playlist.name}]({query})**"
                return await interaction.followup.send(embed=embed)
        else:
            search: Playable = await NodePool.get_node().get_tracks(YouTubeTrack, query)[0]
            

        search.info
        if voice_client.is_playing():
            await voice_client.queue.put_wait(item=search)
            embed.description = f"✅ Queued - **[{search.title}]({search.uri})**"
            return await interaction.followup.send(embed=embed)
        else:
            await voice_client.play(search)
            embed.description = f"🎶 Playing - **[{voice_client.source.title}]({search.uri})**"
            return await interaction.followup.send(embed=embed)

    @app_commands.command(name="queue", description="Song queue")
    async def _queue(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        player: Player = interaction.user.guild.voice_client
        queue: str = None
        embed: Embed = Embed(title="Queue", color=ModularUtil.convert_color(ModularBotConst.COLOR['queue']))
        
        try:
            for count, ele in enumerate(player.queue):
                if count == 10:
                    break

                try:
                    isClass = str(type(ele)).split(".")[0]
                    if isClass == "<class 'wavelink":
                        ele = await ele._search()
                except:
                    pass
                queue += f"{count+1}. **[{ele.info['title']}]({ele.info['uri']})** - {self.parseSec(ele.duration) }\n"
            if queue:
                embed.description = queue
                if player.queue.count > 10:
                    embed.description += f"\n and {len(player.queue) - 10} more..."
                 
                return await interaction.followup.send(embed=embed)
            else:
                embed.description = "No music queued"
                embed.color = ModularUtil.convert_color(ModularBotConst['failed'])
                
                return await interaction.followup.send(embed=embed)
        except:
            embed.description = "No music queued"
            embed.color = ModularUtil.convert_color(ModularBotConst['failed'])
            return await interaction.followup.send(embed=embed)

    @app_commands.command(name="skip", description="Skip a song")
    async def _skip(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        if interaction.guild.voice_client.channel != interaction.user.voice.channel and not interaction.user.voice:
            return await interaction.response.send_message("❌ Can't do that. \nPlease join the same Voice Channel with bot!!", ephemeral=True)

        embed: Embed = Embed(
            description="⏯️ Skipped",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['failed'])
        )

        voice_client: Player = interaction.user.guild.voice_client
        if interaction.user.guild.voice_client:
            if not voice_client.is_playing():
                return await interaction.followup.send("Nothing is playing")

            if voice_client.queue.is_empty:
                await voice_client.stop()

            await voice_client.seek(voice_client.track.length * 1000)

            if voice_client.is_paused():
                await voice_client.resume()

            return await interaction.followup.send(embed=embed)
        else:
            return await interaction.followup.send("The bot is not connected to a voice channel")

    @app_commands.command(name="clear", description="Clear queue")
    async def _clear(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        if interaction.guild.voice_client.channel != interaction.user.voice.channel and not interaction.user.voice:
            return await interaction.response.send_message("❌ Can't do that. \nPlease join the same Voice Channel with bot!!", ephemeral=True)

        embed: Embed = Embed(
            description="❌ Cannot clear. \nPlease make sure to have a queue list",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['failed'])
        )
        if interaction.user.guild.voice_client:
            player: Player = interaction.user.guild.voice_client
            if not player.queue.is_empty:
                player.queue.clear()
                embed.description = "✅ Cleared"
                embed.color = ModularUtil.convert_color(ModularBotConst.COLOR['success'])

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="shuffle", description="Shuffle song")
    async def _shuffle(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        if interaction.guild.voice_client.channel != interaction.user.voice.channel and not interaction.user.voice:
            return await interaction.response.send_message("❌ Can't do that. \nPlease join the same Voice Channel with bot!!", ephemeral=True)

        embed: Embed = Embed(
            description="🔀 Shuffled",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )
        voice_client: Player = interaction.user.guild.voice_client
        if not interaction.user.guild.voice_client:
            return await interaction.followup.send("The bot is not connected to a voice channel", ephemeral=True)

        if not voice_client.queue.is_empty:
            shuffle(voice_client.queue._queue)
            return await interaction.followup.send(embed=embed)
        else:
            return await interaction.followup.send("Queue is empty")
    
    @app_commands.command(name="np", description="Now playing song")
    async def _now_playing(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        if not interaction.user.guild.voice_client:
            return await interaction.followup.send("The bot is not connected to a voice channel", ephemeral=True)
        
        voice_client: Player = interaction.user.guild.voice_client
        if voice_client.is_playing():
            pos: int = voice_client.position
            duration: int = voice_client.source.duration
            time: int = duration - pos

            embed: Embed = Embed(
                title="Now Playing",
                description=f"""**[{voice_client.source.title}]({voice_client.source.info['uri']}) - {self.parseSec(voice_client.source.duration)}** 
                \n** {str(timedelta(seconds=time)).split('.')[0]} left**""",
                color=ModularUtil.convert_color(ModularBotConst.COLOR['play'])
            )

            return await interaction.followup.send(embed=embed)
        else:
            return await interaction.followup.send("Nothing is playing")

    @app_commands.command(name="loop", description="Loop current track")
    async def _loop(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        if interaction.guild.voice_client.channel != interaction.user.voice.channel and not interaction.user.voice:
            return await interaction.response.send_message("❌ Can't do that. \nPlease join the same Voice Channel with bot!!", ephemeral=True)

        embed: Embed = Embed(
            description="❌ Cannot loop. \nPlease make sure to have a music playing",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['failed'])
        )

        if interaction.user.guild.voice_client:
            player: Player = interaction.user.guild.voice_client
            if not player.is_playing:
                return await interaction.followup.send(embed=embed)

            if hasattr(player, 'loop'):
                player.loop = not player.loop
            else:
                player.loop = True
            
            embed.description = "✅ Loop Track" if player.loop else "✅ Unloop Track"
            embed.color = ModularUtil.convert_color(ModularBotConst.COLOR['success'])

        await interaction.followup.send(embed=embed)      

    @app_commands.command(name="pause", description="Pause song")
    async def _pause(self, interaction: Interaction) -> None:
        await interaction.response.defer()

        embed: embed = Embed(
            description="⏸️ Paused",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )
        voice_client: Player = interaction.user.guild.voice_client
        if not interaction.user.guild.voice_client:
            return await interaction.followup.send("The bot is not connected to a voice channel", ephemeral=True)

        if voice_client.is_playing() and not voice_client.is_paused():
            return await wait([ensure_future(voice_client.pause()),
                ensure_future(interaction.followup.send(embed=embed))
            ])
        else:
            return await interaction.followup.send("Nothing is playing")
            

    @app_commands.command(name="resume", description="Resume song")
    async def _resume(self, interaction: Interaction) -> None:
        await interaction.response.defer()
        if interaction.guild.voice_client.channel != interaction.user.voice.channel and not interaction.user.voice:
            return await interaction.response.send_message("❌ Can't do that. \nPlease join the same Voice Channel with bot!!", ephemeral=True)

        embed: Embed = Embed(
            description="▶️ Resumed",
            color=ModularUtil.convert_color(ModularBotConst.COLOR['success'])
        )
        voice_client: Player = interaction.user.guild.voice_client
        if not interaction.user.guild.voice_client:
            return await interaction.followup.send("The bot is not connected to a voice channel", ephemeral=True)

        if voice_client.is_paused():
            return await wait([ensure_future(voice_client.resume()),
                ensure_future(interaction.followup.send(embed=embed))
            ])
        else:
            return await interaction.followup.send("Nothing is paused")
