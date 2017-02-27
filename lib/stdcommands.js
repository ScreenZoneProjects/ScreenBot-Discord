import logger from 'winston';

const StandardCommands = {
	'discord': {
		'songrequest': function (message, args) {
			logger.info('SongRequest received...');
			logger.log('debug', args);
		}
	}
};

export default StandardCommands;