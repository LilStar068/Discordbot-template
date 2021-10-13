import discord
import psutil

from utility import http, embeds
from io import BytesIO
from discord.ext import commands


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def avatar(self, ctx, *, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        user = user or ctx.author
        await ctx.send(f"Avatar to **{user.name}**\n{user.avatar.with_size(1024)}")

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx):
        """ Get all roles in current server """
        allroles = ""

        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            allroles += f"[{str(num).zfill(2)}] {role.id}\t{role.name}\t[ Users: {len(role.members)} ]\r\n"

        data = BytesIO(allroles.encode("utf-8"))
        await ctx.send(content=f"Roles in **{ctx.guild.name}**", file=discord.File(data, filename="roles.yml"))

    @commands.command()
    @commands.guild_only()
    async def joinedat(self, ctx, *, user: discord.Member = None):
        """ Check when a user joined the current server """
        user = user or ctx.author

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar)
        embed.description = f"**{user}** joined **{ctx.guild.name}**\n{discord.utils.format_dt(user.joined_at)}"
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def mods(self, ctx):
        """ Check which mods are online on current guild """
        message = ""
        all_status = {
            "online": {"users": [], "emoji": "🟢"},
            "idle": {"users": [], "emoji": "🟡"},
            "dnd": {"users": [], "emoji": "🔴"},
            "offline": {"users": [], "emoji": "⚫"}
        }

        for user in ctx.guild.members:
            user_perm = ctx.channel.permissions_for(user)
            if user_perm.kick_members or user_perm.ban_members:
                if not user.bot:
                    all_status[str(user.status)]["users"].append(f"**{user}**")

        for g in all_status:
            if all_status[g]["users"]:
                message += f"{all_status[g]['emoji']} {', '.join(all_status[g]['users'])}\n"

        await ctx.send(f"Mods in **{ctx.guild.name}**\n{message}")

    @commands.group()
    @commands.guild_only()
    async def server(self, ctx):
        """ Check info about current server """
        if ctx.invoked_subcommand is None:
            find_bots = sum(1 for member in ctx.guild.members if member.bot)

            embed = discord.Embed()

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner.with_format("png").with_size(1024))

            embed.add_field(name="Server Name", value=ctx.guild.name, inline=True)
            embed.add_field(name="Server ID", value=ctx.guild.id, inline=True)
            embed.add_field(name="Members", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="Bots", value=find_bots, inline=True)
            embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
            embed.add_field(name="Region", value=ctx.guild.region, inline=True)
            embed.add_field(name="Created", value=discord.utils.format_dt(ctx.guild.created_at), inline=True)
            await ctx.send(content=f"ℹ information about **{ctx.guild.name}**", embed=embed)

    @server.command(name="avatar", aliases=["icon"])
    async def server_avatar(self, ctx):
        """ Get the current server icon """
        if not ctx.guild.icon:
            return await ctx.send("This server does not have a avatar...")
        await ctx.send(f"Avatar of **{ctx.guild.name}**\n{ctx.guild.icon}")

    @server.command(name="banner")
    async def server_banner(self, ctx):
        """ Get the current banner image """
        if not ctx.guild.banner:
            return await ctx.send("This server does not have a banner...")
        await ctx.send(f"Banner of **{ctx.guild.name}**\n{ctx.guild.banner.with_format('png')}")

    @commands.command()
    @commands.guild_only()
    async def user(self, ctx, *, user: discord.Member = None):
        """ Get user information """
        user = user or ctx.author

        show_roles = ", ".join(
            [f"<@&{x.id}>" for x in sorted(user.roles, key=lambda x: x.position, reverse=True) if x.id != ctx.guild.default_role.id]
        ) if len(user.roles) > 1 else "None"

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar)

        embed.add_field(name="Full name", value=user, inline=True)
        embed.add_field(name="Nickname", value=user.nick if hasattr(user, "nick") else "None", inline=True)
        embed.add_field(name="Account created", value=discord.utils.format_dt(user.created_at), inline=True)
        embed.add_field(name="Joined this server", value=discord.utils.format_dt(user.joined_at), inline=True)
        embed.add_field(name="Roles", value=show_roles, inline=False)

        await ctx.send(content=f"ℹ About **{user.id}**", embed=embed)


    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def about(self, ctx):
        ram = self.process.memory_full_info().rss / 1024 ** 2
        cpu_usage = round(psutil.cpu_percent() / psutil.cpu_count(), 1)
        em = embeds.emebd(title=f"About {self.bot.user.name} ℹ")
        em.add_field(name="Basic Info", value="_ _", inline=False)
        em.add_field(name="Servers", value=len([x for x in self.bot.guilds]))
        em.add_field(name="Commands", value=len([x for x in self.bot.commands]))
        em.add_field(name="users", value=len([x for x in self.bot.users]))
        em.add_field(name="Adcanced Info", inline=False)
        em.add_field(name="CPU Usage", value="{} %".format(cpu_usage))
        em.add_field(name="RAM Usage", value="{} MB".format(ram))
        em.add_field(name="Ping", value=round(self.bot.latency * 1000, 1))
        await ctx.send(embed=em)


    @commands.command(slash_command=True)
    async def covid(self, ctx, *, country: str):
        """Get a country's covid statistic."""
        async with ctx.channel.typing():
            r = await http.get(
                f"https://disease.sh/v3/covid-19/countries/{country.lower()}",
                res_method="json",
            )

            if "message" in r:
                return await ctx.send(f"The API returned an error:\n{r['message']}")

            json_data = [
                ("Total Cases", r["cases"]),
                ("Total Deaths", r["deaths"]),
                ("Total Recover", r["recovered"]),
                ("Total Active Cases", r["active"]),
                ("Total Critical Condition", r["critical"]),
                ("New Cases Today", r["todayCases"]),
                ("New Deaths Today", r["todayDeaths"]),
                ("New Recovery Today", r["todayRecovered"]),
            ]

            embed = discord.Embed(
                description=f"**COVID-19** statistics in :flag_{r['countryInfo']['iso2'].lower()}: "
                f"**{country.capitalize()}** *({r['countryInfo']['iso3']})*\n\n"
                f"The information provided was last updated <t:{int(r['updated'] / 1000)}:R>\n",
                color=0x011076,
            )
            embed.set_footer(
                icon_url=ctx.author.avatar.url,
                text=f"Requested by {ctx.author} | Wear your mask and stay safe!",
            )

            for name, value in json_data:
                embed.add_field(name=name, value=f"{value:,}" if isinstance(value, int) else value)

            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Information(bot))