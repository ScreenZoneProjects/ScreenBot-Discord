import discord
from discord.ext import commands
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class SendImg:
    """My custom cog that does stuff!"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def sendimg(self, ctx, url=None):
        """Envoie une image..."""
        if url is None:
            await self.bot.send_cmd_help(ctx)
        elif url[:4] != "http":
            await self.bot.say("Vous devez donner un lien valide en argument.")
        else:
            fn = url.split('/')[-1]
            r = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            try:
                with urlopen(r) as imgfile:
                    await self.bot.upload(imgfile, filename=fn)
            except HTTPError:
                await self.bot.say("L'image est introuvable ! :cry:")


def check_folders():
    if not os.path.exists("data/sendimg"):
        print("Creating data/sendimg folder...")
        os.makedirs("data/sendimg")


def setup(bot):
    check_folders()
    bot.add_cog(SendImg(bot))
