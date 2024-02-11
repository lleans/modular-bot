from discord import Interaction, Embed, Member
from discord.ext import commands
from discord.app_commands import ContextMenu, AppCommandError, guild_only

from ..util import ModularUtil
from config import ModularBotConst


@guild_only()
class Playground(commands.Cog):

    def __init__(self, bot: commands.Bot) -> None:
        self._bot: commands.Bot = bot
        self.ctx_avatar = ContextMenu(
            name="Avatar",
            callback=self._avatar
        )
        self._bot.tree.add_command(self.ctx_avatar)
        #TODO Got rate limited
        # self.ctx_banner = ContextMenu(
        #     name="Banner",
        #     callback=self._banner
        # )
        # self._bot.tree.add_command(self.ctx_banner)
        super().__init__()

    async def _avatar(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.Color.SUCCESS), timestamp=ModularUtil.get_time())
        embed.set_footer(
            text=f'From {interaction.user.display_name}', icon_url=interaction.user.display_avatar)
        embed.set_image(
            url=user.display_avatar.url)
        embed.description = f"Showing avatar of {user.mention}"

        await ModularUtil.send_response(interaction, embed=embed)

    async def _banner(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(color=ModularUtil.convert_color(
            ModularBotConst.Color.SUCCESS), timestamp=ModularUtil.get_time())
        embed.set_footer(
            text=f'From {interaction.user.display_name}', icon_url=interaction.user.display_avatar)
        embed.set_image(
            url=user.banner)
        embed.description = f"Showing banner of {user.mention}"

        await ModularUtil.send_response(interaction, embed=embed)

    async def cog_app_command_error(self, interaction: Interaction, error: AppCommandError) -> None:
        await ModularUtil.send_response(interaction, message=f"Unknown error, {Exception(error)}", emoji="❓")

        return await super().cog_app_command_error(interaction, error)
