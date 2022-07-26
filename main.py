# Copyright 2022 Tkachenko Andrii <xezo360hye@gmail.com>
#
# This file is part of CatGirlBot.
#
# CatGirlBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# CatGirlBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CatGirlBot. If not, see <http://www.gnu.org/licenses/>.

# Imports
import yaml
from vk_api import VkApi, VkUpload
from vk_api.bot_longpoll import VkBotLongPoll
from bot import CatGirlBot

def load_config(filename: str = 'config.yaml') -> dict:
    """
    Load YAML configuration file
    """
    with open(filename, 'r') as f:
        return yaml.safe_load(f)

def init_vk(bot: dict) -> tuple:
    vk_session = VkApi(token=bot['token'])
    longpoll = VkBotLongPoll(vk_session, bot['group_id'])
    uploader = VkUpload(vk_session)
    vk = vk_session.get_api()

    return vk, longpoll, uploader

# Set whitelist
#  whitelist = set(vk.groups.getMembers(group_id=group_id)['items'])


def main():
    print("Loading config")
    config = load_config()

    print("Initializing VK session")
    vk, longpoll, uploader = init_vk(config['bot'])

    print("Starting bot")
    bot = CatGirlBot(config, vk, longpoll, uploader)
    bot.start()



if __name__ == "__main__":
    main()
