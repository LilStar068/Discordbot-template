from datetime import datetime

from discord import Color, Embed
from discord.ext import commands
from discord.ext.commands import BucketType


class NoSnipeableMessage(commands.CommandError):
    def __init__(self):
        super().__init__(
            "There aren't any recent message that have been deleted/edited!"
        )


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
    async def _snipe(self, ctx):
        """Snipe a deleted message"""
        if ctx.invoked_subcommand is None:
            try:
                sniped_message = self.delete_snipes[ctx.channel]
            except KeyError:
                raise NoSnipeableMessage()
            else:
                result = Embed(
                    color=Color.red(),
                    description=sniped_message.content,
                    timestamp=sniped_message.created_at,
                )
                result.set_author(
                    name=sniped_message.author.display_name,
                    icon_url=sniped_message.author.avatar_url,
                )
                await ctx.reply(embed=result)


def setup(bot):
    bot.add_cog(Snipe(bot))
