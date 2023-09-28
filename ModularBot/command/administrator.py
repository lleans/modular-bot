from discord import (
    Interaction,
    Embed,
    Member,
    Role,
    Message
)
from discord.ext import commands
from discord.app_commands import (
    ContextMenu,
    checks,
    AppCommandError,
    MissingPermissions,
    command,
    guild_only
)

from ..util import ModularUtil
from config import GuildRole, ModularBotConst


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
            embed.description = f"<@{user.name}> does not have role <@&{is_exist.name}>"

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
