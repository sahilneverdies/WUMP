import discord
from discord.ext import commands


class sonuMusic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Music commands"""

    def help_custom(self):
              emoji = '<:olympus_music:1251052387775283263>'
              label = "Music Commands"
              description = ""
              return emoji, label, description

    @commands.group()
    async def __Music__(self, ctx: commands.Context):
        """`play` , `search` , `loop` , `autoplay` , `nowplaying` , `shuffle` , `stop` , `skip` , `seek` , `join` , `disconnect` , `replay` , `queue` , `clearqueue` , `pause` , `resume` , `volume` , `filter` , `filter enable` , `filter disable`"""