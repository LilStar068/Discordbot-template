import os
import re
import dotenv
import discord
import aiohttp
import pyfiglet
import datetime
import humanize

from config import Config
from discord.ext import commands

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=Config().prefix,
            intents=discord.Intents.all(),
            token=Config().token,
            allowed_mentions=discord.AllowedMentions.all(),
            owner_ids=Config().owner_id,
            *args, 
            **kwargs,
        )
        self.session = aiohttp.ClientSession()
        self.uptime = datetime.datetime.now()
        self.config = Config()
        self.command_prefix = self.config.prefix
        self.prefix = self.config.prefix
        self.owner_ids = self.config.owner_id
        self.token = self.config.token

    dotenv.load_dotenv(".env")

    def loader(self):
        cogs = [
            f"cogs.{cog[:-3]}"
            for cog in os.listdir("cogs")
            if cog.endswith(".py") and not cog.startswith("_")
        ]
        for x in cogs:
            self.load_extension(x)
            print("loaded extension {}".format(x))
        self.load_extension("jishaku")
        print("loaded extension {}".format("jishaku"))

    def run(self) -> None:
        return super().run(self.token, reconnect=True)

    async def on_ready(self):
        global uptime
        uptime = datetime.datetime.now()
        cogs = [
            cog
            for cog in os.listdir("cogs")
            if cog.endswith(".py") and not cog.startswith("_")
        ]
        print(pyfiglet.figlet_format(self.user.name))
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print(f"Connected to: {len(self.guilds)} guilds")
        print(f"Connected to: {len(self.users)} users")
        print(f"Connected to: {len(cogs)} cogs")
        print(f"Connected to: {len([x for x in self.commands])} commands\n\n")
        self.loader()
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{len(self.guilds)} servers | {self.prefix}help"
            )
        )

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if not isinstance(error, commands.CommandOnCooldown):
            title = " ".join(
                re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__)
            )
            return await ctx.send(
                embed=discord.Embed(
                    title=title, description=str(error), color=discord.Color.red()
                )
            )

        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(color=discord.Color.red())
            embed.title = "Command On Cooldown"
            embed.description = (
                "This Command is on cooldown, try again after `{}`.".format(
                    humanize.naturaldelta(
                        datetime.timedelta(seconds=int(error.retry_after))
                    )
                )
            )
            return await ctx.send(embed=embed)

    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.lower() is (f"<@!{self.user.id}>", f"<@{self.user.id}>"):
            await message.channel.send(
                f"Hi, i am {self.bot.user} and my prefix is {self.command_prefix}"
            )

        await self.process_commands(message)
