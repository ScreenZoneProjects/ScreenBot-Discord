import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone, exceptions
from geopy import geocoders
from tzwhere import tzwhere


class Heure:
    """Donne l'heure locale à la ville donnée."""

    def __init__(self, bot):
        self.bot = bot
        self.g = geocoders.GoogleV3()
        self.w = tzwhere.tzwhere()

    @commands.command()
    async def heure(self, *, ville: str):
        """Donne l'heure locale à la ville donnée."""
        try:
            place, (lat, lng) = self.g.geocode(ville)
            loc = timezone(self.w.tzNameAt(lat, lng))
            loctime = datetime.now(loc)
            await self.bot.say('Il est ' + loctime.strftime('%H:%M') + ' à ' + ville.replace('_', ' '))
        except exceptions.UnknownTimeZoneError:
            await self.bot.say('La ville n\'a pas été trouvée, désolé. :cry:')


def setup(bot):
    bot.add_cog(Heure(bot))
