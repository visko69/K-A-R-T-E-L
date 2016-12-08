from .dataIO import dataIO
from copy import deepcopy
import discord
import os
import argparse


default_path = "data/red/settings.json"


class Settings:

    def __init__(self, path=default_path):
        self.path = path
        self.check_folders()
        self.default_settings = {
            "TOKEN": None,
            "EMAIL": None,
            "PASSWORD": None,
            "OWNER": None,
            "PREFIXES": [],
            "default": {"ADMIN_ROLE": "Transistor",
                        "MOD_ROLE": "Process",
                        "PREFIXES": []},
            "LOGIN_TYPE": None}
        self.memory_only = False
        old_format = False

        if not dataIO.is_valid_json(self.path):
            self.bot_settings = deepcopy(self.default_settings)
            self.save_settings()
        else:
            current = dataIO.load_json(self.path)
            if current.keys() != self.default_settings.keys():
                for key in self.default_settings.keys():
                    if key not in current.keys():
                        if key == "TOKEN":
                            old_format = True
                        current[key] = self.default_settings[key]
                        print("Adding " + str(key) +
                              " field to red settings.json")
                dataIO.save_json(self.path, current)
            self.bot_settings = dataIO.load_json(self.path)

        if "default" not in self.bot_settings:
            self.update_old_settings_v1()

        if old_format:
            self.update_old_settings_v2()

        self.parse_cmd_arguments()

    def parse_cmd_arguments(self):
        parser = argparse.ArgumentParser(description="Red - Discord Bot")
        parser.add_argument("--email", help="Email login. Must provide a "
                                            "password too. Not using a bot "
                                            "account with a token is "
                                            "discouraged")
        parser.add_argument("--password", help="Password of the email login")
        parser.add_argument("--token", help="Login token")
        parser.add_argument("--owner", help="ID of the owner. Only who hosts "
                                            "Red should be owner, this has "
                                            "security implications")
        parser.add_argument("--prefix", "-p", action="append",
                            help="Global prefix. Can be multiple")
        parser.add_argument("--admin-role", help="Role seen as admin role by "
                                                 "Red")
        parser.add_argument("--mod-role", help="Role seen as mod role by Red")
        parser.add_argument("--no-prompt",
                            action="store_true",
                            help="Disables console inputs. Features requiring "
                                 "console interaction could be disabled as a "
                                 "result")
        parser.add_argument("--self-bot",
                            action='store_true',
                            help="Specifies if Red should log in as selfbot")
        parser.add_argument("--memory-only",
                            action="store_true",
                            help="Arguments passed and future edits to the "
                                 "settings will not be saved to disk")
        parser.add_argument("--debug",
                            action="store_true",
                            help="Enables debug mode")

        args = parser.parse_args()

        if args.email and args.password:
            self.email = args.email
            self.password = args.password
            self.token = None
            self.login_type = "email"
        if args.token:
            self.token = args.token
            self.email = None
            self.password = None
            self.login_type = "token"
        if args.owner:
            self.owner = args.owner
        if args.prefix:
            self.prefixes = sorted(args.prefix, reverse=True)
        if args.admin_role:
            self.default_admin = args.admin_role
        if args.mod_role:
            self.default_mod = args.mod_role

        self.no_prompt = args.no_prompt
        self.self_bot = args.self_bot
        self.memory_only = args.memory_only
        self.debug = args.debug

        self.save_settings()

    def check_folders(self):
        folders = ("data", os.path.dirname(self.path), "cogs", "cogs/utils")
        for folder in folders:
            if not os.path.exists(folder):
                print("Creating " + folder + " folder...")
                os.makedirs(folder)

    def save_settings(self):
        if not self.memory_only:
            dataIO.save_json(self.path, self.bot_settings)

    def update_old_settings_v1(self):
        # This converts the old settings format
        mod = self.bot_settings["MOD_ROLE"]
        admin = self.bot_settings["ADMIN_ROLE"]
        del self.bot_settings["MOD_ROLE"]
        del self.bot_settings["ADMIN_ROLE"]
        self.bot_settings["default"] = {"MOD_ROLE": mod,
                                        "ADMIN_ROLE": admin,
                                        "PREFIXES" : []}
        self.save_settings()

    def update_old_settings_v2(self):
        # The joys of backwards compatibility
        if self.email == "EmailHere":
            self.email = None
        if self.password == "":
            self.password = None
        if self.login_type == "token":
            self.token = self.email
            self.email = None
            self.password = None
        else:
            self.token = None
        if self.email is None and self.token is None:
            self.login_type = None
        self.save_settings()

    @property
    def owner(self):
        return self.bot_settings["OWNER"]

    @owner.setter
    def owner(self, value):
        self.bot_settings["OWNER"] = value

    @property
    def token(self):
        return self.bot_settings["TOKEN"]

    @token.setter
    def token(self, value):
        self.bot_settings["TOKEN"] = value

    @property
    def email(self):
        return self.bot_settings["EMAIL"]

    @email.setter
    def email(self, value):
        self.bot_settings["EMAIL"] = value

    @property
    def password(self):
        return self.bot_settings["PASSWORD"]

    @password.setter
    def password(self, value):
        self.bot_settings["PASSWORD"] = value

    @property
    def prefixes(self):
        return self.bot_settings["PREFIXES"]

    @prefixes.setter
    def prefixes(self, value):
        assert isinstance(value, list)
        self.bot_settings["PREFIXES"] = value

    @property
    def default_admin(self):
        if "default" not in self.bot_settings:
            self.update_old_settings()
        return self.bot_settings["default"].get("ADMIN_ROLE", "")

    @default_admin.setter
    def default_admin(self, value):
        if "default" not in self.bot_settings:
            self.update_old_settings()
        self.bot_settings["default"]["ADMIN_ROLE"] = value

    @property
    def default_mod(self):
        if "default" not in self.bot_settings:
            self.update_old_settings_v1()
        return self.bot_settings["default"].get("MOD_ROLE", "")

    @default_mod.setter
    def default_mod(self, value):
        if "default" not in self.bot_settings:
            self.update_old_settings_v1()
        self.bot_settings["default"]["MOD_ROLE"] = value

    @property
    def servers(self):
        ret = {}
        server_ids = list(
            filter(lambda x: str(x).isdigit(), self.bot_settings))
        for server in server_ids:
            ret.update({server: self.bot_settings[server]})
        return ret

    @property
    def login_type(self):
        return self.bot_settings["LOGIN_TYPE"]

    @login_type.setter
    def login_type(self, value):
        self.bot_settings["LOGIN_TYPE"] = value

    def get_server(self, server):
        if server is None:
            return self.bot_settings["default"].copy()
        assert isinstance(server, discord.Server)
        return self.bot_settings.get(server.id,
                                     self.bot_settings["default"]).copy()

    def get_server_admin(self, server):
        if server is None:
            return self.default_admin
        assert isinstance(server, discord.Server)
        if server.id not in self.bot_settings:
            return self.default_admin
        return self.bot_settings[server.id].get("ADMIN_ROLE", "")

    def set_server_admin(self, server, value):
        if server is None:
            return
        assert isinstance(server, discord.Server)
        if server.id not in self.bot_settings:
            self.add_server(server.id)
        self.bot_settings[server.id]["ADMIN_ROLE"] = value
        self.save_settings()

    def get_server_mod(self, server):
        if server is None:
            return self.default_mod
        assert isinstance(server, discord.Server)
        if server.id not in self.bot_settings:
            return self.default_mod
        return self.bot_settings[server.id].get("MOD_ROLE", "")

    def set_server_mod(self, server, value):
        if server is None:
            return
        assert isinstance(server, discord.Server)
        if server.id not in self.bot_settings:
            self.add_server(server.id)
        self.bot_settings[server.id]["MOD_ROLE"] = value
        self.save_settings()

    def get_server_prefixes(self, server):
        if server is None or server.id not in self.bot_settings:
            return self.prefixes
        return self.bot_settings[server.id].get("PREFIXES", [])

    def set_server_prefixes(self, server, prefixes):
        if server is None:
            return
        assert isinstance(server, discord.Server)
        if server.id not in self.bot_settings:
            self.add_server(server.id)
        self.bot_settings[server.id]["PREFIXES"] = prefixes
        self.save_settings()

    def get_prefixes(self, server):
        """Returns server's prefixes if set, otherwise global ones"""
        p = self.get_server_prefixes(server)
        return p if p else self.prefixes

    def add_server(self, sid):
        self.bot_settings[sid] = self.bot_settings["default"].copy()
        self.save_settings()
