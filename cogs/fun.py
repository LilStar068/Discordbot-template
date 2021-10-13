import datetime
import discord
import random
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def meme(self, ctx):
        async with self.bot.session.get(f"https://www.reddit.com/r/dankmemes/top.json") as response:
            j = await response.json()
        data = j["data"][random.randint(1, 10)]["data"]
        image_url = data["url"]
        title = data["title"]
        em = discord.Embed(description=f"""[**{title}**]({image_url})""", color=ctx.author.color)
        em.set_image(url=image_url)
        em.set_footer(icon_url=ctx.author.avatar_url, text=f"Requested by {ctx.author}")
        await ctx.send(embed=em)

    @commands.command(name="8ball")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def _8ball(self, ctx, question: str = None):
        asnwers = [
            "As I see it, yes.",
            "Yes.",
            "Positive",
            "From my point of view, yes",
            "Convinced.",
            "Most Likley.",
            "Chances High",
            "No.",
            "Negative.",
            "Not Convinced.",
            "Perhaps.",
            "Not Sure",
            "Maybe",
            "I cannot predict now.",
            "Im to lazy to predict.",
            "I am tired. *proceeds with sleeping*",
        ]
        em = discord.Embed(title="8ball 🎱", color=discord.Color.blue())
        em.add_field(name="Question-", value=question, inline=False)
        em.add_field(name="Answer-", value=random.choice(asnwers))
        em.set_footer(
            icon_url=ctx.author.avatar.url,
            text=f"Requested by- {ctx.author} | Do NOT take this seroiusly its jut fun.",
        )
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def invite(self, ctx):
        f"""Invite {self.bot.user.name} to your server!"""
        invite_link = f"https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands"
        em = discord.Embed(title=f"Invite {self.bot.user.name} To Your Server!", description=f"I Am currently in {len(self.bot.guilds)}", url=invite_link)
        em.set_thumbnail(url=self.bot.avatar.url)

    @commands.command()
    async def uptime(self, ctx):
        delta_uptime = datetime.datetime.now() - self.bot.uptime
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        e = discord.Embed(title="Uptime", description=f"My Uptime is - `{days}` Days, `{hours}` Hours, `{minutes}` Minutes, `{seconds}` Seconds,", color=discord.Color.green())
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Fun(bot))
