from discord import (
    Interaction,
    Embed,
    Member,
    Role,
    Message,
    Guild
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
            name="Add Server Access",
            callback=self._add_access
        ))
        self._bot.tree.add_command(ContextMenu(
            name="Add Magician",
            callback=self._add_magician
        ))
        self._bot.tree.add_command(ContextMenu(
            name="Revoke Server Access",
            callback=self._revoke_access
        ))
        self._bot.tree.add_command(ContextMenu(
            name="Revoke Magician",
            callback=self._revoke_magician
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
    async def _add_magician(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)\

        embed: Embed = Embed(timestamp=ModularUtil.get_time(), color=ModularUtil.convert_color(
            ModularBotConst.COLOR['success']))
        embed.set_footer(
            text=f'From {interaction.user.name} ', icon_url=interaction.user.display_avatar)
        guild: Guild = self._bot._guild
        role: Role = guild.get_role(GuildRole.MAGICIAN)
        is_exist: Role = user.get_role(GuildRole.MAGICIAN)

        if not is_exist:
            await user.add_roles(role)
            embed.description = f"Succesfully added <@&{role.id}> to user <@{user.id}>"

        else:
            embed.color = ModularUtil.convert_color(
                ModularBotConst.COLOR['failed'])
            embed.description = f"User <@{user.id}> already had role <@&{role.id}>"

        await ModularUtil.send_response(interaction, embed=embed)

    @checks.has_permissions(administrator=True)
    async def _add_access(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(timestamp=ModularUtil.get_time(), color=ModularUtil.convert_color(
            ModularBotConst.COLOR['success']))
        embed.set_footer(
            text=f'From {interaction.user.name} ', icon_url=interaction.user.display_avatar)
        guild: Guild = self._bot._guild
        role: Role = guild.get_role(GuildRole.THE_MUSKETEER)
        is_exist: Role = user.get_role(GuildRole.THE_MUSKETEER)

        if not is_exist:
            await user.add_roles(role)
            embed.description = f"Succesfully added <@&{role.id}> to user <@{user.id}>"

        else:
            embed.color = ModularUtil.convert_color(
                ModularBotConst.COLOR['failed'])
            embed.description = f"User <@{user.id}> already had role <@&{role.id}>"

        await ModularUtil.send_response(interaction, embed=embed)

    @checks.has_permissions(administrator=True)
    async def _revoke_magician(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(timestamp=ModularUtil.get_time(), color=ModularUtil.convert_color(
            ModularBotConst.COLOR['success']))
        embed.set_footer(
            text=f'From {interaction.user.name} ', icon_url=interaction.user.display_avatar)
        is_exist: Role = user.get_role(GuildRole.MAGICIAN)

        if is_exist:
            await user.remove_roles(is_exist)
            embed.description = f"Succesfully revoke <@&{GuildRole.MAGICIAN}> from user <@{user.id}>"
        else:
            embed.color = ModularUtil.convert_color(
                ModularBotConst.COLOR['failed'])
            embed.description = f"<@{user.id}> does not have role <@&{GuildRole.MAGICIAN}>"

        await ModularUtil.send_response(interaction, embed=embed)

    @checks.has_permissions(administrator=True)
    async def _revoke_access(self, interaction: Interaction, user: Member):
        await interaction.response.defer(ephemeral=True)

        embed: Embed = Embed(timestamp=ModularUtil.get_time(), color=ModularUtil.convert_color(
            ModularBotConst.COLOR['success']))
        embed.set_footer(
            text=f'From {interaction.user.name} ', icon_url=interaction.user.display_avatar)
        is_exist: Role = user.get_role(GuildRole.THE_MUSKETEER)

        if is_exist:
            await user.remove_roles(is_exist)
            embed.description = f"Succesfully revoke <@&{GuildRole.THE_MUSKETEER}> from <@{user.id}>"

        else:
            embed.color = ModularUtil.convert_color(
                ModularBotConst.COLOR['failed'])
            embed.description = f"<@{user.id}> does not have role <@&{GuildRole.THE_MUSKETEER}>"

        await ModularUtil.send_response(interaction, embed=embed)

    async def cog_app_command_error(self, interaction: Interaction, error: AppCommandError) -> None:
        if isinstance(error, MissingPermissions):
            await ModularUtil.send_response(interaction, message="You don't have Permission to do this", emoji="❌")

        else:
            await ModularUtil.send_response(interaction, message=f"Unknown error, {Exception(error)}", emoji="❓")

        return await super().cog_app_command_error(interaction, error)
