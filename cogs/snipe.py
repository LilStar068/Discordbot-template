from math import floor
from discord import Color, Embed, TextChannel
from discord.ext import commands
from discord.ext.commands import BucketType
from discord.mentions import A

class NoMessagesToSnipe(commands.CommandError):
    def __init__(self):
        super().__init__("There aren't any recent message that have been deleted/edited!")

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.delete_snipes = {}
        self.edit_snipes = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        self.delete_snipes[message.channel] = message

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return

        self.edit_snipes[after.channel] = (before, after)

    @commands.group(name="snipe")
    @commands.cooldown(1, 10, BucketType.user)
    @commands.guild_only()
    @commands.bot_has_permissions(send_messages=True, read_messages=True)
    async def snipe_group(self, ctx):
        """Snipe a deleted message"""
        if ctx.invoked_subcommand is None:
            await ctx.send(commands.help(ctx.command))

    @snipe_group.command(name="delete")
    async def snipe_delete(self, ctx, channel:TextChannel = None):
        """Snipe a deleted message"""
        
        channel = channel or ctx.channel
        
        try:
            sniped_message = self.delete_snipes[channel]
            sniped_time = floor(sniped_message.created_at.timestamp())
        except KeyError:
            raise NoMessagesToSnipe()
        else:

            em = Embed(color=Color.red())
            em.title = "Snipe Deleted Message!"
            em.description = f"Message - `{sniped_message.content}`\n\nMessage Deleted By - {sniped_message.author.mention}\nMessage Deleted at - <t:{sniped_time}:F>"

            em.set_footer(
                text=f"Requested by - {ctx.author}",
                icon_url=ctx.author.avatar.url,
            )
            await ctx.reply(embed=em)

    @snipe_group.command(name="edit")
    async def snipe_edit(self, ctx, channel:TextChannel = None):
        """Snipes an edited message"""
        
        channel = channel or ctx.channel
        
        try:
            before, after = self.edit_snipes[channel]
        except KeyError:
            raise NoMessagesToSnipe()
        else:
            em = Embed(color=Color.red())
            em.title = "Snipe Edited Message!"
            em.description = f"Before - `{before.content}`\nAfter - `{after.content}`\n\nMessage Edited By - {after.author.mention}\nMessage Edited at - <t:{floor(after.edited_at.timestamp())}:F>"

            em.set_footer(
                text=f"Requested by - {ctx.author}",
                icon_url=ctx.author.avatar.url,
            )
            await ctx.reply(embed=em)

def setup(bot):
    bot.add_cog(Snipe(bot))