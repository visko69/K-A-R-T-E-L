import re
from datetime import timedelta

from redbot.core.commands import BadArgument

TIME_RE = re.compile(
    r"((?P<days>\d+?)\s?(d(ays?)?))?\s?((?P<hours>\d+?)\s?(hours?|hrs|hr?))?\s?((?P<minutes>\d+?)\s?(minutes?|mins?|m))?\s?((?P<seconds>\d+?)\s?(seconds?|secs?|s))?\s?",
    re.I,
)


def timedelta_converter(argument: str) -> timedelta:
    """
    Convert to a :class:`datetime.timedelta` class.

    The converter supports seconds, minutes, hours and days.

    Time can be attached to the unit (only use the first letter) or not
    (then use the full word).

    .. admonition:: Example

        *   ``50s`` = ``50 seconds`` -> :class:`datetime.timedelta(seconds=50)`
        *   ``12m`` = ``12 minutes`` -> :class:`datetime.timedelta(seconds=720)`
        *   ``4h`` = ``4 hours`` -> :class:`datetime.timedelta(seconds=14400)`
        *   ``1d`` = ``1 day`` -> :class:`datetime.timedelta(days=1)`

        Using the converter with a command:

        .. code-block:: python3

            @commands.command()
            async def timer(self, ctx, time: commands.timedelta_converter):
                await asyncio.sleep(time.total_seconds())
                await ctx.send("Time's up!")

        Using the converter manually:

        .. code-block:: python3

            async def convert_time(ctx: Context, text: str) -> datetime.timedelta:
                time = commands.timedelta_converter(text)
                return time

    Arguments
    ---------
    argument: str
        The string you want to convert.

    Returns
    -------
    datetime.timedelta
        The :class:`datetime.timedelta` object.

    Raises
    ------
    ~discord.ext.commands.BadArgument
        No time was found from the given string.
    """

    matches = TIME_RE.match(argument)
    params = {k: int(v) for k, v in matches.groupdict().items() if None not in (k, v)}
    if not params:
        raise BadArgument("No time could be found.")
    time = timedelta(**params)
    return time
