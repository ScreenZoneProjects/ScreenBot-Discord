const path    = require('path');
const express = require('express');
const Discord = require("discord.js");
const Loki    = require("lokijs");
const config  = require("./config.json");
const db      = new Loki("screenbot.db");
const client  = new Discord.Client();
const app     = express();

var guilds, commads;

db.loadDatabase({}, function () {
	console.log('Database is loaded.');
	guilds   = db.getCollection('guilds');
	commands = db.getCollection('commands');
});

var actions = {
	"DELETE_MESSAGES": function (msg, cmd) {
		var nb = parseInt(msg.content.replace(cmd.cmd, ''));
		msg.channel.bulkDelete(nb);
	},
	"SEND_ATTACHEMENT": function (msg, cmd) {
		msg.channel.sendFile(cmd.attachements[0], path.basename(cmd.attachements[0]));
	},
	"SEND_RANDOM_ATTACHEMENT": function (msg, cmd) {
		var rand = cmd.attachements[Math.floor(Math.random() * cmd.attachements.length)];
		msg.channel.sendFile(rand, path.basename(rand));
	},
	"CHANGE_BOT_NAME": function (msg, cmd) {
		var name = msg.content.replace(cmd.cmd, '').replace(' ', '');
		client.user.setUsername(name);
	}
};

var invitationURL = function () {
	return `https://discordapp.com/oauth2/authorize?client_id=${config.clientID}&scope=bot&permissions=9000`;
};

client.on('ready', () => {
  console.log(`Logged in as ${client.user.username}!`);
});

client.on('message', msg => {

	if (guilds === null || commands === null)
		return;

	if (msg.guild === null || msg.channel === null || msg.channel.type !== "text")
		return;

	var guildEntry = guilds.findOne({id: msg.guild.id, name: msg.guild.name});

	if (guildEntry) {
		var firstWord = msg.content.split(' ')[0];
		var cmdEntry = commands.findOne({'$and': [{'gid': guildEntry.id}, {'cmd': firstWord}] });
		if (cmdEntry) {
			if (!cmdEntry.args && msg.content !== cmdEntry.cmd)
				return;

			const memberRank = Math.max(...msg.guild.member(msg.author).roles.array().map(role=>role.position));
			if (memberRank < cmdEntry.rank)
				msg.reply(config.forbiddenCommandMessage);
			else 
			{
				if (typeof cmdEntry.action !== "undefined")
					actions[cmdEntry.action](msg, cmdEntry);
				else
					msg.channel.sendMessage(cmdEntry.message);
			}
			
		}
	}

});

client.on('disconnect', function () {
	console.log('Discord Client is disconnected, closing database...');
	db.close(function () { 
		console.log('Database is now closed.');
	});
});

// var guilds    = db.addCollection('guilds', {indices:["id"], unique: ["id"]});
// var commands  = db.addCollection('commands', {indices:["gid"]});
// var screenzoneGuild = guilds.insert({name: "Screenzone", id: "91280005803278336"});
// var aideCommand = commands.insert({
// 	"gid": "91280005803278336",
// 	"cmd": "!aide",
// 	"rank": 0,
// 	"message": "voici l'aide !",
// 	"args": false
// });

// db.saveDatabase(function () { console.log('db saved.'); });
// db.close(function () { console.log('db closed.') });

client.login(config.token);

app.use(express.static('public'));

app.get('/permission', function (req, res) {
	res.redirect(invitationURL());
});

app.post('/command', function (req, res) {

});

app.update('/command', function (req, res) {
	
});

app.delete('/command', function (req, res) {
	
});

app.listen(3000, function () {
  console.log('Example app listening on port 3000!');
});