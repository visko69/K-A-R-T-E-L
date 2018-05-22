from redbot.core import commands
from typing import Tuple


class CogOrCommand(commands.Converter):

    async def convert(self, ctx: commands.Context, arg: str) -> Tuple[str]:
        ret = ctx.bot.get_cog(arg)
        if ret:
            return "Cog", arg
        ret = ctx.bot.get_command(arg)
        if ret:
            return "Command", arg

        raise commands.BadArgument()


class RuleType(commands.Converter):

    async def convert(self, ctx: commands.Context, arg: str) -> str:
        if arg.lower() in (
            "allow", "whitelist", "allowed"
        ):
            return "allow"
        if arg.lower() in (
            "deny", "blacklist", "denied"
        ):
            return "deny"

        raise commands.BadArgument()
