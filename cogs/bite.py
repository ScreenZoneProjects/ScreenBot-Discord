import discord
import random
from discord.ext import commands


class Bite:
    """Sans commentaire..."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def bite(self, *, user: discord.Member):
        """Détecte la longeur du pénis de l'utilisateur

        100% de précision."""
        state = random.getstate()
        random.seed(user.id)
        dong = "8{}D".format("=" * random.randint(0, 30))
        random.setstate(state)
        await self.bot.say(dong)


def setup(bot):
    bot.add_cog(Bite(bot))
