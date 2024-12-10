import discord
from discord.ext import commands


class sonu111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Fun commands"""
  
    def help_custom(self):
		      emoji = '<:olympus_fun:1222785541930487868>'
		      label = "Fun Commands"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Fun__(self, ctx: commands.Context):
        """`/imagine` , `ship` , `mydog` , `chat` , `translate` , `howgay` , `lesbian` , `cute` , `intelligence`, `chutiya` , `horny` , `tharki` , `gif` , `iplookup` , `weather` , `hug` , `kiss` , `pat` , `cuddle` , `slap` , `tickle` , `spank` , `ngif` , `8ball` , `truth` , `dare`"""