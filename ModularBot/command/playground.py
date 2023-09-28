from discord import Interaction, Embed, Member
from discord.ext import commands
from discord.app_commands import ContextMenu, AppCommandError, guild_only

from ..util import ModularUtil
from config import ModularBotConst


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
