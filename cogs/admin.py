import os
import sys
import time
import datetime

from discord.ext import commands
from utility import default, embeds


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shutdown(self, ctx):
        em = embeds.embed(
            title="Stopping Now...",
            description=default.timestamp(datetime.datetime.now()),
        )
        await ctx.send(emebd=em)
        time.sleep(1)
        sys.exit(0)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        def restarter():
            python = sys.executable
            os.execl(python, python, *sys.argv)

        em = embeds.embed(
            title="Bot rebooting",
            description=default.timestamp(datetime.datetime.now()),
        )
        await ctx.send(embed=em)
        restarter()


def setup(bot):
    bot.add_cog(Admin(bot))
