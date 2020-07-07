import logging
import re
from typing import Final, List, Set, Pattern
from urllib.parse import urlparse

import discord

from redbot.core import Config

from ...audio_dataclasses import Query
from ..abc import MixinMeta
from ..cog_utils import CompositeMetaClass

log = logging.getLogger("red.cogs.Audio.cog.Utilities.validation")

_RE_YT_LIST_PLAYLIST: Final[Pattern] = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com|youtu\.?be)(/playlist\?).*(list=)(.*)(&|$)"
)


class ValidationUtilities(MixinMeta, metaclass=CompositeMetaClass):
    def match_url(self, url: str) -> bool:
        try:
            query_url = urlparse(url)
            return all([query_url.scheme, query_url.netloc, query_url.path])
        except Exception:
            return False

    def match_yt_playlist(self, url: str) -> bool:
        if _RE_YT_LIST_PLAYLIST.match(url):
            return True
        return False

    def is_url_allowed(self, url: str) -> bool:
        valid_tld = [
            "youtube.com",
            "youtu.be",
            "soundcloud.com",
            "bandcamp.com",
            "vimeo.com",
            "beam.pro",
            "mixer.com",
            "twitch.tv",
            "spotify.com",
            "localtracks",
        ]
        query_url = urlparse(url)
        url_domain = ".".join(query_url.netloc.split(".")[-2:])
        if not query_url.netloc:
            url_domain = ".".join(query_url.path.split("/")[0].split(".")[-2:])
        return True if url_domain in valid_tld else False

    def is_vc_full(self, channel: discord.VoiceChannel) -> bool:
        return not (channel.user_limit == 0 or channel.user_limit > len(channel.members))

    async def is_query_allowed(
        self, config: Config, guild: discord.Guild, query: str, query_obj: Query = None
    ) -> bool:
        """Checks if the query is allowed in this server or globally"""

        query = query.lower().strip()
        if query_obj is not None:
            query = query_obj.lavalink_query.replace("ytsearch:", "youtubesearch").replace(
                "scsearch:", "soundcloudsearch"
            )
        global_allowlist = set(await config.url_keyword_allowlist())
        global_allowlist = [i.lower() for i in global_allowlist]
        if global_allowlist:
            return any(i in query for i in global_allowlist)
        global_denylist = set(await config.url_keyword_denylist())
        global_denylist = [i.lower() for i in global_denylist]
        if any(i in query for i in global_denylist):
            return False
        if guild is not None:
            allowlist_unique: Set[str] = set(await config.guild(guild).url_keyword_allowlist())
            allowlist: List[str] = [i.lower() for i in allowlist_unique]
            if allowlist:
                return any(i in query for i in allowlist)
            denylist_unique: Set[str] = set(await config.guild(guild).url_keyword_denylist())
            denylist: List[str] = [i.lower() for i in denylist_unique]
            return not any(i in query for i in denylist)
        return True
