import discord
from collections import defaultdict
from discord.ext import commands
from .utils.dataIO import dataIO
import os


class Tell:
    """Stocke un message et le renvoie à la personne désirée

    lorsqu'elle se connectera."""

    def __init__(self, bot):
        self.bot = bot
        self.cacheFilePath = "data/tell/cache.json"
        cache = dataIO.load_json(self.cacheFilePath)
        self.cache = defaultdict(dict, cache)

    @commands.command(pass_context=True, no_pm=True)
    async def tell(self, ctx, user: discord.Member, *, message: str):
        """Stocke un message et le renvoie à la personne désirée

        lorsqu'elle se connectera."""
        server = ctx.message.server
        if str(user.status) != 'offline':
            await self.bot.say(user.mention + " n'est pas déconnecté, vous n'avez pas besoin de moi. ;)")
        else:
            if self.cache.get(server.id, None) is None:
                self.cache[server.id] = {'messages': []}
            self.cache[server.id]['messages'].append({'author': ctx.message.author.name, 'target': user.id, 'message': message, 'channel': ctx.message.channel.name})
            dataIO.save_json(self.cacheFilePath, self.cache)
            await self.bot.say('Le message a bien été enregistré. :smile:')

    async def member_join(self, member):
        """Called when a member is connected"""
        server = member.server
        if server.id in self.cache:
            for m in self.cache[server.id]['messages']:
                if m.target == member.id:
                    await self.bot.send_message(member, '{}, le membre {} t\'as envoyé un message dans le channel {} lors de ton absence : \n{}'.format(member.mention, m['author'], m['channel'], m['message']))


def check_folders():
    if not os.path.exists("data/tell"):
        print("Creating data/tell folder...")
        os.makedirs("data/tell")


def check_files():
    f = "data/tell/cache.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty cache.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    n = Tell(bot)
    bot.add_listener(n.member_join, "on_member_join")
    bot.add_cog(n)
