import discord
from discord.ext import commands
from discord.ext.commands.errors import BadArgument


class Plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, _, plural = format_spec.partition("|")
        plural = plural or f"{singular}s"
        if abs(v) != 1:
            return f"{v} {plural}"
        return f"{v} {singular}"


def check_role(ctx, member):
    attr = getattr(member, "top_role", None)
    if attr:
        if ctx.author.top_role.position >= member.top_role.position:
            raise BadArgument("You cannot ban a member if a higher role than you.")


def actionmsg(user, action):
    return f"Successfully! {action} {user}"


class Moderation(commands.Cog):

    description = "Moderation commands, (Only work for moderators)"

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        """Kicks a user from the current server."""
        check_role(ctx, member)

        try:
            e = discord.Embed(description=(actionmsg(member.name, "kicked")))
            await member.kick(reason=reason)
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        """Bans a user from the current server."""
        check_role(ctx, (ctx.guild.get_member(member)))

        try:
            u = await self.bot.fetch_user(member)
            e = discord.Embed(description=(actionmsg(u.name, "banned")))
            e.color = discord.Color.red()
            await ctx.guild.ban(discord.Object(id=member), reason=reason)
            await ctx.send(embed=e)
        except Exception as e:
            await ctx.send(e)

    @commands.command(slash_command=True)
    @commands.has_guild_permissions(kick_members=True)
    async def mute(
        self, ctx, *, member: discord.Member = None, reason: str = "Not Specified"
    ):
        """Mute someone in the server. (Require kick permission)"""
        role = discord.utils.get(ctx.guild.roles, name="Muted")

        if member == ctx.guild.owner:
            em = discord.Embed(
                title="Server Owner",
                description=f"{ctx.author.mention}, you cannot mute the servers owner!",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=em)

        if not role:
            await ctx.guild.create_role(name="Muted")

        if member.top_role > ctx.author.top_role:
            em = discord.Embed(
                title="Member Has Higher Role",
                description=f"{ctx.author.mention}, {member.mention} has a higher role than you so you cannot mute them",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=em)

        if member == ctx.author:
            em = discord.Embed(
                title="Cannot Mute!",
                description=f"{ctx.author.mention}, you cannot mute yourself!",
                color=discord.Color.red(),
            )

        for channel in ctx.guild.channels:
            await channel.set_permissions(
                role,
                speak=False,
                send_messages=False,
                read_message_history=True,
                read_messages=False,
            )

        else:
            embed = discord.Embed(
                title="Muted",
                description=f"{member.mention} was muted because\nReason:{reason}",
                colour=discord.Colour.light_gray(),
            )
            await ctx.send(embed=embed)
            await member.add_roles(role, reason=reason)

    @commands.command(slash_command=True)
    @commands.has_guild_permissions(kick_members=True)
    async def unmute(
        self, ctx, *, member: discord.Member = None, reason: str = "Not Specified"
    ):
        """Unmute someone in the server. (Require kick permission)"""
        role = discord.utils.get(ctx.guild.roles, name="Muted")

        if member == ctx.guild.owner:
            em = discord.Embed(
                title="Server Owner",
                description=f"{ctx.author.mention}, you cannot unmute the servers owner as they cannot be muted!",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=em)

        if not role:
            await ctx.guild.create_role(name="Muted")

        if "Muted" not in member.roles:
            em = discord.Embed(
                title="Not Muted",
                description=f"{member.mention} has not been muted!",
                color=discord.Color.red(),
            )
            await ctx.send(embed=em)

        if member.top_role > ctx.author.top_role:
            em = discord.Embed(
                title="Member Has Higher Role",
                description=f"{ctx.author.mention}, {member.mention} has a higher role than you so you cannot unmute them",
                color=discord.Color.red(),
            )
            return await ctx.send(embed=em)

        else:
            em = discord.Embed(
                title="Unmuted",
                description=f"{member.mention} was succesfully unmuted!",
                color=discord.Color.green(),
            )
            await member.remove_roles(role, reason=reason)

    @commands.command(slash_command=True, aliases=["clear"])
    @commands.has_permissions(kick_members=True)
    async def purge(self, ctx, amount=11):
        """Purge spammed messages in the server. (Require kick permission)"""
        amount = amount + 1
        if amount > 101:
            await ctx.send(
                "Are you crazy?! Deleting over 100 messages?! Try only 100 messages per time in case you might "
                "accidentally delete important things."
            )
        else:
            await ctx.channel.purge(limit=int(amount))
            await ctx.send(f"Purged {amount} messages sucessfully.", delete_after=3)

    @commands.command(slash_command=True)
    @commands.has_permissions(ban_members=True)
    async def massban(self, ctx, members: commands.Greedy[discord.Member], reason):
        """Ban alot of people at the same time in the server. (Require ban permission)"""
        failed = 0

        confirm = await ctx.prompt(
            f"This will ban {Plural(len(members)):member} members, are you sure you want to do this?"
        )
        if confirm is True:
            for member in members:
                try:
                    await ctx.guild.ban(discord.Object(id=int(member)), reason=reason)
                except (discord.Forbidden, discord.HTTPException):
                    failed += 1
            await ctx.reply(
                f"Successfully Banned {len(members)-failed}/{len(members)} members."
            )
        else:
            await ctx.reply("Cancelled the process.")


def setup(bot):
    bot.add_cog(Moderation(bot))
