import discord
from discord.ext import commands
try:
    from bs4 import BeautifulSoup
    soupAvailable = True
except:
    soupAvailable = False
import aiohttp


class Stats:
    """Statitistiques ScreeZone et ScreenScraper."""

    def __init__(self, bot):
        self.bot = bot
        self.url = "https://www.screenscraper.fr/htmlinc_compteurs.html"

    @commands.command()
    async def stats_ss(self):
        """Statitistiques à propos de ScreenScraper."""
        async with aiohttp.get(self.url) as response:
            soupObject = BeautifulSoup(await response.text(), "html.parser")
            table = soupObject.find('table')
            embed = discord.Embed(title='https://www.screenscraper.fr', url='https://www.screenscraper.fr', description='Rendez-vous sur le site pour plus d\'infos', color=0x80C901)
            embed.set_author(name='SCREENSCRAPER')
            for tr in table.find_all('tr'):
                embed.add_field(name=tr.find(class_='sstext').get_text()[:-2], value=tr.find(class_='sstats').get_text(), inline=True)
            embed.set_footer(text="powered by ScreenScraper.fr", icon_url='http://www.screenzone.fr/forum/images/icons_forum/screenscraper.png')
            await self.bot.say(embed=embed)


def setup(bot):
    if soupAvailable:
        bot.add_cog(Stats(bot))
    else:
        raise RuntimeError("You need to run `pip3 install beautifulsoup4`")
