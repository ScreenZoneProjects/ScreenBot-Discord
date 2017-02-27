/**
 * An IRC bot, works as a middleman for all communication
 * @param {object} options - server, nickname, channelMapping, outgoingToken, incomingURL
 */
export class BadBotConfigurationException extends Error {
  constructor(message) {
    super(message);
    this.name = 'BadBotConfigurationException';
    this.message = message || 'The configuration file is invalid.';
  }
}

/**
 * An IRC bot, works as a middleman for all communication
 * @param {object} options - server, nickname, channelMapping, outgoingToken, incomingURL
 */
export class KeyNotFoundException extends Error {
	constructor(message) {
		this.name = 'KeyNotFoundException';
		this.message = message || 'The key was not found.';
	}
};

/**
 * An IRC bot, works as a middleman for all communication
 * @param {object} options - server, nickname, channelMapping, outgoingToken, incomingURL
 */
export class LangNotFoundException extends Error {
	constructor(message) {
		this.name = 'LangNotFoundException';
		this.message = message || 'The lang was not found.';
	}
};

/**
 * An IRC bot, works as a middleman for all communication
 * @param {object} options - server, nickname, channelMapping, outgoingToken, incomingURL
 */
export class BadInternationalizationConfigurationException extends Error {
	constructor(message) {
		this.name = 'BadInternationalizationConfigurationException';
		this.message = message || 'The configuration file is invalid.';
	}
};
