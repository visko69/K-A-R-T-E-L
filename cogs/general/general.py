import discord
from discord.ext import commands
from core.utils.chat_formatting import escape, italics, pagify
from random import randint
from random import choice
from enum import Enum
from urllib.parse import quote_plus
import datetime
import time
import aiohttp
import asyncio

settings = {"POLL_DURATION" : 60}


class RPS(Enum):
    rock     = "\N{MOYAI}"
    paper    = "\N{PAGE FACING UP}"
    scissors = "\N{BLACK SCISSORS}"


class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "rock":
            self.choice = RPS.rock
        elif argument == "paper":
            self.choice = RPS.paper
        elif argument == "scissors":
            self.choice = RPS.scissors
        else:
            raise


class General:
    """General commands."""

    def __init__(self, bot):
        self.bot = bot
        self.stopwatches = {}
        self.ball = [
            "As I see it, yes", "It is certain", "It is decidedly so",
            "Most likely", "Outlook good", "Signs point to yes",
            "Without a doubt", "Yes", "Yes – definitely", "You may rely on it",
            "Reply hazy, try again", "Ask again later",
            "Better not tell you now", "Cannot predict now",
            "Concentrate and ask again", "Don't count on it", "My reply is no",
            "My sources say no", "Outlook not so good", "Very doubtful"
        ]
        self.poll_sessions = []

    @commands.command(hidden=True)
    async def ping(self, ctx):
        """Pong."""
        await ctx.send("Pong.")

    @commands.command()
    async def choose(self, ctx, *choices):
        """Chooses between multiple choices.

        To denote multiple choices, you should use double quotes.
        """
        choices = [escape(c, mass_mentions=True) for c in choices]
        if len(choices) < 2:
            await ctx.send('Not enough choices to pick from.')
        else:
            await ctx.send(choice(choices))

    @commands.command()
    async def roll(self, ctx, number : int = 100):
        """Rolls random number (between 1 and user choice)

        Defaults to 100.
        """
        author = ctx.author
        if number > 1:
            n = randint(1, number)
            await ctx.send(
                "{} :game_die: {} :game_die:".format(author.mention, n)
            )
        else:
            await ctx.send("{} Maybe higher than 1? ;P".format(author.mention))

    @commands.command()
    async def flip(self, ctx, user: discord.Member=None):
        """Flips a coin... or a user.

        Defaults to coin.
        """
        if user != None:
            msg = ""
            if user.id == self.bot.user.id:
                user = ctx.author
                msg = "Nice try. You think this is funny?" +\
                    "How about *this* instead:\n\n"
            char = "abcdefghijklmnopqrstuvwxyz"
            tran = "ɐqɔpǝɟƃɥᴉɾʞlɯuodbɹsʇnʌʍxʎz"
            table = str.maketrans(char, tran)
            name = user.display_name.translate(table)
            char = char.upper()
            tran = "∀qƆpƎℲפHIſʞ˥WNOԀQᴚS┴∩ΛMX⅄Z"
            table = str.maketrans(char, tran)
            name = name.translate(table)
            await ctx.send(msg + "(╯°□°）╯︵ " + name[::-1])
        else:
            await ctx.send(
                "*flips a coin and... " + choice(["HEADS!*", "TAILS!*"])
            )

    @commands.command()
    async def rps(self, ctx, your_choice : RPSParser):
        """Play rock paper scissors"""
        author = ctx.author
        player_choice = your_choice.choice
        red_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
        cond = {
                (RPS.rock,     RPS.paper)    : False,
                (RPS.rock,     RPS.scissors) : True,
                (RPS.paper,    RPS.rock)     : True,
                (RPS.paper,    RPS.scissors) : False,
                (RPS.scissors, RPS.rock)     : False,
                (RPS.scissors, RPS.paper)    : True
               }

        if red_choice == player_choice:
            outcome = None # Tie
        else:
            outcome = cond[(player_choice, red_choice)]

        if outcome is True:
            await ctx.send("{} You win {}!".format(
                red_choice.value, author.mention
            ))
        elif outcome is False:
            await ctx.send("{} You lose {}!".format(
                red_choice.value, author.mention
            ))
        else:
            await ctx.send("{} We're square {}!".format(
                red_choice.value, author.mention
            ))

    @commands.command(name="8", aliases=["8ball"])
    async def _8ball(self, ctx, *, question : str):
        """Ask 8 ball a question

        Question must end with a question mark.
        """
        if question.endswith("?") and question != "?":
            await ctx.send("`" + choice(self.ball) + "`")
        else:
            await ctx.send("That doesn't look like a question.")

    @commands.command(aliases=["sw"])
    async def stopwatch(self, ctx):
        """Starts/stops stopwatch"""
        author = ctx.author
        if not author.id in self.stopwatches:
            self.stopwatches[author.id] = int(time.perf_counter())
            await ctx.send(author.mention + " Stopwatch started!")
        else:
            tmp = abs(self.stopwatches[author.id] - int(time.perf_counter()))
            tmp = str(datetime.timedelta(seconds=tmp))
            await ctx.send(author.mention + " Stopwatch stopped! Time: **" + tmp + "**")
            self.stopwatches.pop(author.id, None)

    @commands.command()
    async def lmgtfy(self, ctx, *, search_terms : str):
        """Creates a lmgtfy link"""
        search_terms = escape(search_terms.replace(" ", "+"), mass_mentions=True)
        await ctx.send("https://lmgtfy.com/?q={}".format(search_terms))

    @commands.command(hidden=True)
    @commands.guild_only()
    async def hug(self, ctx, user : discord.Member, intensity : int=1):
        """Because everyone likes hugs

        Up to 10 intensity levels."""
        name = italics(user.display_name)
        if intensity <= 0:
            msg = "(っ˘̩╭╮˘̩)っ" + name
        elif intensity <= 3:
            msg = "(っ´▽｀)っ" + name
        elif intensity <= 6:
            msg = "╰(*´︶`*)╯" + name
        elif intensity <= 9:
            msg = "(つ≧▽≦)つ" + name
        elif intensity >= 10:
            msg = "(づ￣ ³￣)づ{} ⊂(´・ω・｀⊂)".format(name)
        await ctx.send(msg)

    @commands.command()
    @commands.guild_only()
    async def userinfo(self, ctx, *, user: discord.Member=None):
        """Shows users's informations"""
        author = ctx.author
        guild = ctx.guild

        if not user:
            user = author

        roles = [x.name for x in user.roles if not x.is_everyone()]

        joined_at = self.fetch_joined_at(user, guild)
        since_created = (ctx.message.created_at - user.created_at).days
        since_joined = (ctx.message.created_at - joined_at).days
        user_joined = joined_at.strftime("%d %b %Y %H:%M")
        user_created = user.created_at.strftime("%d %b %Y %H:%M")
        member_number = sorted(guild.members,
                               key=lambda m: m.joined_at).index(user) + 1

        created_on = "{}\n({} days ago)".format(user_created, since_created)
        joined_on = "{}\n({} days ago)".format(user_joined, since_joined)

        game = "Chilling in {} status".format(user.status)

        if user.game and user.game.name and user.game.url:
            game = "Streaming: [{}]({})".format(user.game, user.game.url)
        elif user.game and user.game.name:
            game = "Playing {}".format(user.game)


        if roles:
            roles = sorted(user.roles)
            roles = ", ".join(roles)
        else:
            roles = "None"

        data = discord.Embed(description=game, colour=user.colour)
        data.add_field(name="Joined Discord on", value=created_on)
        data.add_field(name="Joined this guild on", value=joined_on)
        data.add_field(name="Roles", value=roles, inline=False)
        data.set_footer(text="Member #{} | User ID:{}"
                             "".format(member_number, user.id))

        name = str(user)
        name = " ~ ".join((name, user.nick)) if user.nick else name

        if user.avatar:
            data.set_author(name=name, url=user.avatar_url)
            data.set_thumbnail(url=user.avatar_url)
        else:
            data.set_author(name=name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission "
                           "to send this")

    @commands.command()
    @commands.guild_only()
    async def guildinfo(self, ctx):
        """Shows guild's informations"""
        guild = ctx.guild
        online = len([m.status for m in guild.members
                      if m.status == discord.Status.online or
                      m.status == discord.Status.idle])
        total_users = len(guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        passed = (ctx.message.created_at - guild.created_at).days
        created_at = ("Since {}. That's over {} days ago!"
                      "".format(guild.created_at.strftime("%d %b %Y %H:%M"),
                                passed))

        colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
        colour = randint(0, 0xFFFFFF)

        data = discord.Embed(
            description=created_at,
            colour=discord.Colour(value=colour))
        data.add_field(name="Region", value=str(guild.region))
        data.add_field(name="Users", value="{}/{}".format(online, total_users))
        data.add_field(name="Text Channels", value=text_channels)
        data.add_field(name="Voice Channels", value=voice_channels)
        data.add_field(name="Roles", value=len(guild.roles))
        data.add_field(name="Owner", value=str(guild.owner))
        data.set_footer(text="Guild ID: " + str(guild.id))

        if guild.icon_url:
            data.set_author(name=guild.name, url=guild.icon_url)
            data.set_thumbnail(url=guild.icon_url)
        else:
            data.set_author(name=guild.name)

        try:
            await ctx.send(embed=data)
        except discord.HTTPException:
            await ctx.send("I need the `Embed links` permission "
                            "to send this")

    @commands.command()
    async def urban(self, ctx, *, search_terms: str, definition_number: int=1):
        """Urban Dictionary search

        Definition number must be between 1 and 10"""
        def encode(s):
            return quote_plus(s, encoding='utf-8', errors='replace')

        # definition_number is just there to show up in the help
        # all this mess is to avoid forcing double quotes on the user

        search_terms = search_terms.split(" ")
        try:
            if len(search_terms) > 1:
                pos = int(search_terms[-1]) - 1
                search_terms = search_terms[:-1]
            else:
                pos = 0
            if pos not in range(0, 11): # API only provides the
                pos = 0                 # top 10 definitions
        except ValueError:
            pos = 0

        search_terms = {"term": "+".join([s for s in search_terms])}
        url = "http://api.urbandictionary.com/v0/define"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=search_terms) as r:
                    result = await r.json()
            item_list = result["list"]
            if item_list:
                definition = item_list[pos]['definition']
                example = item_list[pos]['example']
                defs = len(item_list)
                msg = ("**Definition #{} out of {}:\n**{}\n\n"
                       "**Example:\n**{}".format(pos+1, defs, definition,
                                                 example))
                msg = pagify(msg, ["\n"])
                for page in msg:
                    await ctx.send(page)
            else:
                await ctx.send("Your search terms gave no results.")
        except IndexError:
            await ctx.send("There is no definition #{}".format(pos+1))
        except:
            await ctx.send("Error.")

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx, *text):
        """Starts/stops a poll

        Usage example:
        poll Is this a poll?;Yes;No;Maybe
        poll stop"""
        message = ctx.message
        if len(text) == 1:
            if text[0].lower() == "stop":
                await self.endpoll(message)
                return
        if not self.getPollByChannel(message):
            check = " ".join(text).lower()
            if "@everyone" in check or "@here" in check:
                await ctx.send("Nice try.")
                return
            p = NewPoll(message, self)
            if p.valid:
                self.poll_sessions.append(p)
                await p.start()
            else:
                await ctx.send("poll question;option1;option2 (...)")
        else:
            await ctx.send("A poll is already ongoing in this channel.")

    async def endpoll(self, message):
        if self.getPollByChannel(message):
            p = self.getPollByChannel(message)
            if p.author == message.author.id: # or isMemberAdmin(message)
                await self.getPollByChannel(message).endPoll()
            else:
                await message.channel.send("Only admins and the author can stop the poll.")
        else:
            await message.channel.send("There's no poll ongoing in this channel.")

    def getPollByChannel(self, message):
        for poll in self.poll_sessions:
            if poll.channel == message.channel:
                return poll
        return False

    async def on_message(self, message):
        if message.author.id != self.bot.user.id:
            if self.getPollByChannel(message):
                self.getPollByChannel(message).checkAnswer(message)

    def fetch_joined_at(self, user, guild):
        """Just a special case for someone special :^)"""
        if user.id == 96130341705637888 and guild.id == 133049272517001216:
            return datetime.datetime(2016, 1, 10, 6, 8, 4, 443000)
        else:
            return user.joined_at

class NewPoll():
    def __init__(self, message, main):
        self.channel = message.channel
        self.author = message.author.id
        self.client = main.bot
        self.poll_sessions = main.poll_sessions
        msg = message.content[6:]
        msg = msg.split(";")
        if len(msg) < 2: # Needs at least one question and 2 choices
            self.valid = False
            return None
        else:
            self.valid = True
        self.already_voted = []
        self.question = msg[0]
        msg.remove(self.question)
        self.answers = {}
        i = 1
        for i, answer in enumerate(msg, 1): # {id : {answer, votes}}
            self.answers[i] = {"ANSWER" : answer, "VOTES" : 0}

    async def start(self):
        msg = "**POLL STARTED!**\n\n{}\n\n".format(self.question)
        for id, data in self.answers.items():
            msg += "{}. *{}*\n".format(id, data["ANSWER"])
        msg += "\nType the number to vote!"
        await self.channel.send(msg)
        await asyncio.sleep(settings["POLL_DURATION"])
        if self.valid:
            await self.endPoll()

    async def endPoll(self):
        self.valid = False
        msg = "**POLL ENDED!**\n\n{}\n\n".format(self.question)
        for data in self.answers.values():
            msg += "*{}* - {} votes\n".format(data["ANSWER"], str(data["VOTES"]))
        await self.channel.send(msg)
        self.poll_sessions.remove(self)

    def checkAnswer(self, message):
        try:
            i = int(message.content)
            if i in self.answers.keys():
                if message.author.id not in self.already_voted:
                    data = self.answers[i]
                    data["VOTES"] += 1
                    self.answers[i] = data
                    self.already_voted.append(message.author.id)
        except ValueError:
            pass
