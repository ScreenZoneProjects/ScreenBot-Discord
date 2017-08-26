#!/bin/sh
echo "{\n\t\"EMAIL\":null,\n\t\"OWNER\":\"${OWNER_ID}\",\n\t\"PASSWORD\":null,\n\t\"PREFIXES\":[\"${COMMAND_PREFIX}\"],\n\t\"TOKEN\":\"${DISCORD_TOKEN}\",\n\t\"default\":\n\t{\n\t\t\"ADMIN_ROLE\":\"${ADMINS_NAME}\",\n\t\t\"MOD_ROLE\":\"${MODS_NAME}\",\n\t\t\"PREFIXES\":[]\n\t}\n}\n" > data/red/settings.json
python3 launcher.py --start $*
