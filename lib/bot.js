import discord from 'discord.js';
import tmi from 'tmi.js';
import logger from 'winston';
import {BadBotConfigurationException} from './exceptions';
import i18n from './i18n';
import loki from 'lokijs';
import path from 'path';
import StandardCommands from './stdcommands';

const REQUIRED_FIELDS = ['discordToken', 'defaultLanguage'];
const NICK_COLORS = ['light_blue', 'dark_blue', 'light_red', 'dark_red', 'light_green', 'dark_green', 'magenta', 'light_magenta', 'orange', 'yellow', 'cyan', 'light_cyan'];
const text = new i18n({
	'directoryPath': path.join(__dirname, '../i18n'), 
	'defaultLang': 'en-US'
});
var stdCommands, customCommands, channelsMappings;
const db = new loki(path.join(__dirname, '../screenbot.db'), {
	'autosave': true,
	'autoload': true,
	'autoloadCallback': () => { 
		stdCommands = db.getCollection('standardCommands');
		customCommands = db.getCollection('customCommands');
		channelsMappings = db.getCollection('channelsMappings');
	}
});

/**
 * The main Bot, works as a middleman for all communication on Twitch/Discord/IRC
 * @param {object} options - discordToken, defaultLanguage, twitchID, twitchURL
 */
class Bot {
	constructor(options) {

		REQUIRED_FIELDS.forEach((field) => {
			if (!options[field])
				throw new BadBotConfigurationException(`Missing configuration field ${field}`);
		});
		
		this.defaultLanguage = options.defaultLanguage;
		this.text = text;
		this.text.setLang(this.defaultLanguage);
		this.setupDiscord(options.discordToken);

		if (options.twitchID && options.twitchURL) {
			this.twitchID = options.twitchID;
			this.twitchURL = options.twitchURL;
			this.setupTwitch(options.twitchID);
		}
	}

	setupDiscord(token) {
		this.discordToken = token;
		this.discordClient = new discord.Client({ autoReconnect: true });

		this.discordClient.on('message', this.handleDiscordMessage);

		this.discordClient.on('ready', () => {
			logger.info('Discord Client is now connected via discord.js library.');
		});
	}

	handleDiscordMessage(message) {
		let currentGuild = message.guild;
		let currentChannel = message.channel;
		let stdcmdFound = false;
		let cuscmdFound = false;

		// invoke commands
		if (message.content[0] === '!' && stdCommands) {
			let stdcmds = stdCommands.find({'discord': true});
			
			for (let i = 0; i < stdcmds.length; i++) {
				let grps = message.content.match(stdcmds[i].regex);
				if (grps) {
					stdcmdFound = true;
					message.delete();
					StandardCommands.discord[stdcmds[i].functionName](message, grps.slice(1 + stdcmds[i].argStartIndex));
					break;
				}
			}
			if (!stdcmdFound && customCommands) {
				let cuscmds = customCommands.find({'discord': currentGuild.id});
				for (let i = 0; i < cuscmds.length; i++) {
					let grps = message.content.match(cuscmds[i].regex);
					if (grps) {
						cuscmdFound = true;
						message.delete();
						currentChannel.sendMessage(cuscmds[i].message);
						break;
					}
				}
			}
		}

		// invoke bridges
		if (!stdcmdFound && !cuscmdFound) {
			let mapping = channelsMappings.findOne({'$and': [{'guildId': currentGuild.id}, {'discord': currentChannel.name}]});
			if (mapping) {
				let msg = `[Discord ${currentGuild.name}#${currentChannel.name}]${message.author.username}: ${message.content}`;
				if (mapping.twitch !== '') {
					this.sendTwitchMessage(mapping.twitch, msg);
				}
				if (mapping.irc !== '') {
					this.sendIrcMessage(mapping.irc, msg);
				}
			}
		}
	}

	sendTwitchMessage(channel, message) {
		if (this.twitchClient)
			this.twitchClient.say(channel, message);
	}

	setupTwitch(clienId) {
		let tmiConfig = {
			'options': { 
				'clientId': clienId, 
				'debug': (process.env.NODE_ENV === 'development')
			},
			'connection': {
				'reconnect': true
			}
		};
		this.twitchClient = new tmi.client(tmiConfig);
		this.twitchClient.on("connected", (address, port) => {
			logger.info(`Twitch Client is now connected via tmi.js library on ${address}:${port}.`);
		});
		
	}

	connect() {
		this.discordClient.login(this.discordToken);
		if (this.twitchClient) {
			this.twitchClient.connect();
		}
	}
};

export default Bot;