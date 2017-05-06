import discord
from discord.ext import commands
import requests
from .utils.dataIO import dataIO
from collections import defaultdict
import os
import json


class Game:
    """Trouver les infos d'un jeu sur ScreenScraper."""

    def __init__(self, bot):
        self.bot = bot
        settings = dataIO.load_json("data/game/settings.json")
        self.settings = defaultdict(dict, settings)
        self.params = {}
        self.params['output'] = 'json'
        self.params['devid'] = self.settings['devid']
        self.params['devpassword'] = self.settings['devpassword']
        self.params['ssid'] = self.settings['ssid']
        self.params['sspassword'] = self.settings['sspassword']
        self.params['devsoftware'] = 'discordbot1'

    @commands.command()
    async def game(self, *, nom_du_jeu: str):
        """Trouver les infos d'un jeu sur ScreenScraper."""
        params = self.params
        params['devsoftware'] = self.bot.user.name
        params['romnom'] = nom_du_jeu.replace(' ', '%20')
        r = requests.get('https://www.screenscraper.fr/api/jeuInfos.php', params=params)
        # print(r.url, r.status_code, r.text)
        if r.status_code == 200:
            try:
                jeu = r.json()["response"]['jeu']
                embed = discord.Embed(title='ID: {}'.format(jeu['id']), url='https://www.screenscraper.fr/gameinfos.php?gameid={}'.format(jeu["id"]), description=jeu.get("systemenom", 'Système inconnu'), color=0x80C901)
                embed.set_author(name=jeu["nom"])
                ws = jeu.get("medias", None).get('media_wheels', None)
                if ws is not None:
                    thumb = list(ws.values())[0]
                    if thumb[0] == 'h':
                        embed.set_thumbnail(url=thumb)
                embed.add_field(name="Editeur", value=jeu.get("editeur", "Inconnu"), inline=True)
                embed.add_field(name="Développeur", value=jeu.get("developpeur", 'Inconnu'), inline=True)
                date = jeu.get("dates", {'date_wor': 'Inconnu'}).get("date_wor", 'Inconnu')
                if date == 'Inconnu':
                    date = jeu.get("dates", {'date_eu': 'Inconnu'}).get("date_eu", 'Inconnu')
                    if date == 'Inconnu':
                        date = jeu.get("dates", {'date_fr': 'Inconnu'}).get("date_fr", 'Inconnu')
                embed.add_field(name="Année", value=date, inline=True)
                synopsis = jeu.get("synopsis", {'synopsis_fr': 'Inconnu'}).get("synopsis_fr", 'Inconnu')
                if synopsis == 'Inconnu':
                    synopsis = jeu.get("synopsis", {'synopsis_en': 'Inconnu'}).get("synopsis_en", 'Inconnu')
                if len(synopsis) > 300:
                    synopsis = synopsis[:297] + "..."
                embed.add_field(name="Synopsis", value=synopsis.replace('\n', '').replace('\r', ''), inline=False)
                embed.set_footer(text="powered by ScreenScraper.fr", icon_url='http://www.screenzone.fr/forum/images/icons_forum/screenscraper.png')
                await self.bot.say(embed=embed)
            except KeyError:
                await self.bot.say("Un problème est survenu lors de la récolte d'information.")
            except json.decoder.JSONDecodeError:
                await self.bot.say(r.text)
        else:
            await self.bot.say("Un problème est survenu lors de la connexion à ScreenScraper, réessayez ultérieurement.")


def check_folders():
    if not os.path.exists("data/game"):
        print("Creating data/game folder...")
        os.makedirs("data/game")


def check_files():
    f = "data/game/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty settings.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    bot.add_cog(Game(bot))
