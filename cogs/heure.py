import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone, exceptions


class Heure:
    """Donne l'heure locale à la timezone donnée."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def heure(self, pays: str, *, ville: str):
        """Donne l'heure locale à la timezone donnée."""
        try:
            loc = timezone('{}/{}'.format(pays, ville.replace(' ', '_')))
            loctime = datetime.now(loc)
            await self.bot.say('Il est ' + loctime.strftime('%H:%M') + ' à ' + ville.replace('_', ' '))
        except exceptions.UnknownTimeZoneError:
            await self.bot.say('La ville ne correspond à aucune Timezone, désolé. :cry:')


def setup(bot):
    bot.add_cog(Heure(bot))
