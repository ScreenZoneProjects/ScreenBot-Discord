
import {BadInternationalizationConfigurationException, KeyNotFoundException, LangNotFoundException} from './exceptions';
import fs from 'fs';
import path from 'path';

const REQUIRED_FIELDS = ['directoryPath', 'defaultLang'];

/**
 * An Internationalization module bot, to translate bot commands and admin page
 * @param {object} options - directoryPath, defaultLang
 */
class i18n {
	constructor(options) {
		REQUIRED_FIELDS.forEach((field) => {
			if (!options[field])
				throw new BadInternationalizationConfigurationException(`Missing configuration field ${field}`);
		});

		this.directoryPath = options.directoryPath;
		this.defaultLang = options.defaultLang;
		this.currentLang = options.defaultLang;
		this.filesContent = {};

		this.refresh();
	}

	get(resourceKey) {
		if (resourceKey && resourceKey !== undefined) {
			if (!this.filesContent[this.currentLang][resourceKey])
				throw new KeyNotFoundException(`Missing i18n resource key ${resourceKey}`);
			return this.filesContent[this.currentLang][resourceKey];
		} else {
			return '';
		}
	}

	setLang(lang) {
		if (!lang || lang === undefined) {
			this.currentLang = this.defaultLang;
		}
		else {
			if (!this.filesContent[lang]) {
				if (fs.existsSync(path.join(this.directoryPath, lang + '.json'))) {
					this.filesContent[lang] = require(path.join(this.directoryPath, lang));
				}
				else {
					throw new LangNotFoundException();
				}

			}
			this.currentLang = lang;
		}
	}

	refresh() {
		this.filesContent = {};
		fs.readdirSync(this.directoryPath).map(f => path.join(this.directoryPath, f)).filter(p => path.extname(p) === '.json').forEach((p) => {
			this.filesContent[path.basename(p, '.json')] = require(p);
		});
	}
};

export default i18n;