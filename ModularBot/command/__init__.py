from asyncio import wait, create_task

from discord.ext import commands
from ..util import ModularUtil

from .administrator import Administrator
from .multimedia import Multimedia
from .playground import Playground


async def setup(bot: commands.Bot) -> None:
	await wait([
		create_task(bot.add_cog(Administrator(bot))),
		create_task(bot.add_cog(Multimedia(bot))),
		create_task(bot.add_cog(Playground(bot))),
	])

	ModularUtil.simple_log("Cog loaded")
