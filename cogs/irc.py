import discord
from discord.ext import commands
from .utils.dataIO import dataIO
from collections import defaultdict
from .utils import checks
import os
from .utils.chat_formatting import escape_mass_mentions
import asyncio


class ModuleNotFound(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class IrcError(Exception):
    pass


try:
    import bottom
except:
    raise ModuleNotFound("irc is not installed. Do 'pip3 install bottom --upgrade' to use this cog.")


class IrcBot:
    def __init__(self, discordChannel, host, port, ircChannel, nickname, discordBot):
        self.discordChannel = discordChannel
        self.host = host
        self.port = port
        self.ircChannel = ircChannel
        self.nickname = nickname
        self.discordBot = discordBot
        self.ircclient = bottom.Client(host=host, port=port, ssl=False)
        self.ircclient.on('CLIENT_CONNECT', self.connect)
        self.ircclient.on('PING', self.keepalive)
        self.ircclient.on('PRIVMSG', self.on_message)
        self.loop = asyncio.get_event_loop()
        self.task = self.loop.create_task(self.ircclient.connect())
        # self.loop.run_forever()

    async def connect(self, **kwargs):
        self.ircclient.send('NICK', nick=self.nickname)
        self.ircclient.send('USER', user=self.nickname, realname='IRC-Discord Bot')
        done, pending = await asyncio.wait(
            [self.ircclient.wait("RPL_ENDOFMOTD"),
             self.ircclient.wait("ERR_NOMOTD")],
            loop=self.ircclient.loop,
            return_when=asyncio.FIRST_COMPLETED
        )
        for future in pending:
            future.cancel()
        self.ircclient.send('JOIN', channel=self.ircChannel)

    def say(self, message):
        self.ircclient.send("PRIVMSG", target=self.ircChannel, message=message)

    def keepalive(self, message, **kwargs):
        self.ircclient.send('PONG', message=message)

    async def on_message(self, nick, target, message, **kwargs):
        if message[0] != '!':
            await self.discordBot.send_message(self.discordChannel, '**{}:** {}'.format(nick, message))

    def close(self):
        self.ircclient.send('QUIT')
        self.task.cancel()

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def get_channel(self):
        return self.ircChannel

    def get_discord_channel(self):
        return self.discordChannel


class Irc:
    """IRC

    Make the link between Discord and your IRC server"""

    def __init__(self, bot):
        self.bot = bot
        self.ircbots = []
        self.listeners = []
        settings = dataIO.load_json("data/irc/settings.json")
        self.settings = defaultdict(dict, settings)
        self.messages = {
            "link_added": "Le lien de channels IRC & Discord a bien été ajouté !",
            "link_started": "Le lien de channels IRC & Discord a bien été demarré !",
            "link_stopped": "Le lien de channels IRC & Discord a bien été stoppé !",
            "link_edited": "Le lien de channels IRC & Discord a bien été édité !",
            "link_deleted": "Le lien de channels IRC & Discord a bien été supprimé !",
            "currently_active_link": "Le lien est actif en ce moment utilisez la commande [p]irc stop avant d'éditer ! :fire:",
            "link_already_active": "Le lien est deja actif ! :fire:",
            "link_already_inactive": "Le lien est deja inactif ! :fire:",
            "discord_channel_not_found": "Le channel Discord n'existe pas sur ce serveur. :fire:",
            "link_not_found": "Le lien n'existe pas dans mes paramètres. :fire:",
            "none_link": "Il n'existe aucun lien sur ce serveur. :fire:"
        }
        self.bot.add_listener(self.check_messages, 'on_message')

    def start_irc(self, channel, irc_props):
        """Start the IRC client and register events"""
        h = irc_props["host"]
        p = int(irc_props["port"])
        ircchannel = irc_props["channel"]
        if ircchannel[0] != '#':
            ircchannel = '#' + ircchannel
        self.ircbots.append(IrcBot(channel, h, p, ircchannel, self.bot.user.name, self.bot))

    def stop_irc(self, channel, irc_props):
        """Stop the IRC client and register events"""
        h = irc_props["host"]
        p = int(irc_props["port"])
        ircchannel = irc_props["channel"]
        if ircchannel[0] != '#':
            ircchannel = '#' + ircchannel
        for b in self.ircbots:
            if b.get_host() == h and b.get_port() == p and b.get_channel() == ircchannel:
                b.close()
                self.ircbots.remove(b)
                del b
                break

    async def check_messages(self, message):
        """Check if messages need to be transfered"""
        if message.server is not None and len(message.content) > 0 and message.content[0] != '.' and message.author.bot is False:
            servSetting = self.settings.get(message.server.id, None)
            if servSetting is not None:
                link = servSetting.get(message.channel.id, None)
                if link is not None and link.get("active", False) is not False:
                    for b in self.ircbots:
                        if b.get_discord_channel().id == message.channel.id:
                            b.say('[Discord] {} : {}'.format(message.author.name, message.content))
                            break

    @commands.group(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_server=True)
    async def ircset(self, ctx):
        """IRC settings"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @ircset.command(pass_context=True)
    async def add(self, ctx, discord_channel: str, host: str, port: int, channel: str):
        """Add a new link between a Discord channel and a IRC channel."""
        discord_channel = escape_mass_mentions(discord_channel)
        host = escape_mass_mentions(host)
        port = int(port)
        channel = escape_mass_mentions(channel)
        if channel[0] != '#':
            channel = '#' + channel
        serverChannels = ctx.message.server.channels
        dcf = False
        for sc in serverChannels:
            if sc.name == discord_channel:
                dcf = True
                self.settings[ctx.message.server.id][sc.id] = {"host": host, "port": port, "channel": channel, "active": False}
                dataIO.save_json("data/irc/settings.json", self.settings)
                await self.bot.say(self.messages["link_added"])
                break
        if dcf is False:
            await self.bot.say(self.messages["discord_channel_not_found"])

    @ircset.command(pass_context=True)
    async def edit(self, ctx, discord_channel: str, host: str, port: int, channel: str):
        """Edit a registered channels link."""
        discord_channel = escape_mass_mentions(discord_channel)
        host = escape_mass_mentions(host)
        port = int(port)
        channel = escape_mass_mentions(channel)
        serverChannels = ctx.message.server.channels
        dcf = False
        lf = False
        for sc in serverChannels:
            if sc.name == discord_channel:
                dcf = True
                if self.settings.get(ctx.message.server.id, None) is not None:
                    if self.settings[ctx.message.server.id].get(sc.id, None) is not None:
                        lf = True
                        if self.settings[ctx.message.server.id][sc.id].get("active", False) is True:
                            await self.bot.say(self.messages["currently_active_link"])
                        else:
                            self.settings[ctx.message.server.id][sc.id] = {"host": host, "port": port, "channel": channel, "active": False}
                            dataIO.save_json("data/irc/settings.json", self.settings)
                            await self.bot.say(self.messages["link_edited"])
                        break
        if dcf is False:
            await self.bot.say(self.messages["discord_channel_not_found"])
        if lf is False:
            await self.bot.say(self.messages["link_not_found"])

    @ircset.command(pass_context=True)
    async def delete(self, ctx, discord_channel: str):
        """Delete a link"""
        discord_channel = escape_mass_mentions(discord_channel)
        serverChannels = ctx.message.server.channels
        dcf = False
        lf = False
        for sc in serverChannels:
            if sc.name == discord_channel:
                dcf = True
                if self.settings.get(ctx.message.server.id, None) is not None:
                    if self.settings[ctx.message.server.id].get(sc.id, None) is not None:
                        lf = True
                        del self.settings[ctx.message.server.id][sc.id]
                        dataIO.save_json("data/irc/settings.json", self.settings)
                        await self.bot.say(self.messages["link_deleted"])
        if dcf is False:
            await self.bot.say(self.messages["discord_channel_not_found"])
        if lf is False:
            await self.bot.say(self.messages["link_not_found"])

    @ircset.command(pass_context=True)
    async def list(self, ctx):
        """List all registered channels links"""
        serv = ctx.message.server
        serverCns = serv.channels
        cns = self.settings.get(serv.id, None)
        if cns is None or cns == {}:
            await self.bot.say(self.messages['none_link'])
        else:
            msg = '```\nListe de lien(s) IRC/Discord sur le serveur {}: \n'.format(serv.name)
            for c, val in cns.items():
                for scn in serverCns:
                    if scn.id == c:
                        msg += "--> {} : {} | {} | {}\n".format(scn.name, val['host'], val['port'], val['channel'])
                        break
            msg += '```'
            await self.bot.say(msg)

    @commands.group(pass_context=True, no_pm=True)
    @checks.mod_or_permissions(manage_server=True)
    async def irc(self, ctx):
        """IRC module"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @irc.command(pass_context=True)
    async def start(self, ctx, discord_channel):
        """Start the link between 2 added channels"""
        serv = ctx.message.server
        serverChannels = serv.channels
        dcf = False
        lf = False
        for sc in serverChannels:
            if sc.name == discord_channel:
                dcf = True
                if self.settings.get(ctx.message.server.id, None) is not None:
                    link = self.settings[ctx.message.server.id].get(sc.id, None)
                    if link is not None:
                        lf = True
                        if link.get("active", False) is False:
                            self.start_irc(sc, self.settings[ctx.message.server.id][sc.id])
                            link["active"] = True
                            dataIO.save_json("data/irc/settings.json", self.settings)
                            await self.bot.say(self.messages["link_started"])
                        else:
                            await self.bot.say(self.messages["link_already_active"])
                        break
        if dcf is False:
            await self.bot.say(self.messages["discord_channel_not_found"])
        if lf is False:
            await self.bot.say(self.messages["link_not_found"])

    @irc.command(pass_context=True)
    async def stop(self, ctx, discord_channel):
        """Stop the link between 2 added channels"""
        serv = ctx.message.server
        serverChannels = serv.channels
        dcf = False
        lf = False
        for sc in serverChannels:
            if sc.name == discord_channel:
                dcf = True
                if self.settings.get(ctx.message.server.id, None) is not None:
                    link = self.settings[ctx.message.server.id].get(sc.id, None)
                    if link is not None:
                        lf = True
                        if link.get("active", False) is True:
                            self.stop_irc(sc, self.settings[ctx.message.server.id][sc.id])
                            link["active"] = False
                            dataIO.save_json("data/irc/settings.json", self.settings)
                            await self.bot.say(self.messages["link_stopped"])
                        else:
                            await self.bot.say(self.messages["link_already_inactive"])
                        break
        if dcf is False:
            await self.bot.say(self.messages["discord_channel_not_found"])
        if lf is False:
            await self.bot.say(self.messages["link_not_found"])


def check_folders():
    if not os.path.exists("data/irc"):
        print("Creating data/irc folder...")
        os.makedirs("data/irc")


def check_files():
    f = "data/irc/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty settings.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    n = Irc(bot)
    bot.add_cog(n)
