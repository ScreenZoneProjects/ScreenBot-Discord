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
