#!/usr/bin/env node

import logger from 'winston';
import _ from 'lodash';
import Bot from './bot';
import path from 'path';
import {BadBotConfigurationException} from './exceptions';
const config = require(path.join(__dirname, '../config.json'));

/* istanbul ignore next */
if (process.env.NODE_ENV === 'development') {
  logger.level = 'debug';
}

/**
 * Reads from the provided config file
 */
function createBots() {
  const bots = [];

  // The config file can be both an array and an object
  if (Array.isArray(config)) {
    config.forEach((cfg) => {
      const bot = new Bot(cfg);
      bot.connect();
      bots.push(bot);
    });
  } 
  else if (_.isObject(config)) {
    const bot = new Bot(config);
    bot.connect();
    bots.push(bot);
  } 
  else {
    throw new BadBotConfigurationException();
  }

}

createBots();

// import loki from 'lokijs';
// const db = new loki(path.join(__dirname, '../screenbot.db'));

// var standardCommands = db.addCollection('standardCommands', { 'unique': ['id'], 'indices': ['id', 'twitch', 'discord', 'irc'] });
// var customCommands = db.addCollection('customCommands', { 'unique': ['id'], 'indices': ['id', 'twitch', 'discord', 'irc'] });
// standardCommands.insert({
// 	'id': 0,
// 	'regex': '^!(sr|songrequest)\\s+(\\w+)\\s*$',
// 	'functionName': 'songrequest',
// 	'level': 0,
// 	'argsCount': 1,
// 	'argStartIndex': 1,
// 	'twitch': true,
// 	'discord': true,
// 	'irc': false
// });

// customCommands.insert({
// 	'id': 0,
// 	'regex': '^!420\\s*$',
// 	'level': 0,
// 	'message': 'test dd 123',
// 	'twitch': 'jambonlatex',
// 	'discord': '91280005803278336',
// 	'irc': 'irc.freenode.com#screenzone'
// });
// db.saveDatabase(() => { console.log('db saved.'); });
