import discord
from discord.ext import commands

class sonu1111111111(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    """Games commands"""
  
    def help_custom(self):
		      emoji = '<:olympus_games:1222786029166264350>'
		      label = "Games Commands"
		      description = ""
		      return emoji, label, description

    @commands.group()
    async def __Games__(self, ctx: commands.Context):
        """`blackjack` , `chess` , `tic-tac-toe` , `country-guesser` , `rps` , `lights-out` , `wordle` , `2048` , `memory-game` , `number-slider` , `battleship` , `connect-four` , `slots`"""