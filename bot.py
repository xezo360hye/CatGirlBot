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

from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotEventType
from threading import Thread
from random import choice, random
import requests, io

class CatGirlBot():
    def __init__(self, config, vk, longpoll, uploader):
        self.config = config
        self.vk = vk
        self.longpoll = longpoll
        self.uploader = uploader
        self.users = {}
        self.chats = {}

    def locked(self, event) -> bool:
        """
        Check if user has not reached the limit of messages set in config
        """
        if event.object.message['peer_id'] >= 2000000000:
            user_id = event.object.message['from_id']
            chat_id = event.object.message['peer_id'] - 2000000000
            if chat_id not in self.chats:
                self.chats[chat_id] = {user_id: 1}
                return not self.config['chats']['allow_unauthorized']

            if not user_id in chats[chat_id]:
                self.chats[chat_id][user_id] = 1
                return not self.config['chats']['allow_unauthorized']

            authorized = 'authorized' if chat_id in self.config['chats']['authorized'] else 'unauthorized'
            if self.chats[chat_id][user_id] >= self.config['chats'][authorized]['limit']:
                return True

            self.chats[chat_id][user_id] += 1
            return False
        else:
            user_id = event.object.message['from_id']
            if not user_id in self.users:
                self.users[user_id] = 1
                return not self.config['users']['allow_unauthorized']

            authorized = 'authorized' if user_id in self.config['users']['authorized'] else 'unauthorized'
            if self.users[user_id] >= self.config['users'][authorized]['limit']:
                return True

            self.users[user_id] += 1
            return False

    def upload(self, name: str, peer_id: int) -> str:
        """
        Method to send message. Automatically downloads Image / GIF and sends it

        :param name: Type of image to get (will be added after /api/v2/img)
        :param peer_id: peer ID of the user or chat to send message to

        :return: VK attachment string
        """
        url = requests.get(self.config['images']['base_url'] + name).json()['url']

        # If GIF then send as document
        if url.endswith('.gif'):
            filetype = 'doc'
            upload = self.uploader.document_message(
                io.BytesIO(requests.get(url).content),
                title = 'From @catgirlbot: ' + name,
                peer_id = peer_id)['doc']

        # If JPG, JPED or PNG then send as photo
        elif url.endswith(('.jpg', '.jpeg', '.png')):
            filetype = 'photo'
            upload = self.uploader.photo_messages(
                io.BytesIO(requests.get(url).content),
                peer_id = peer_id)[0]

        # Else send error message
        else:
            print("Unknown filetype:", url)
            return None

        return '{filetype}{owner_id}_{file_id}'.format(filetype=filetype, owner_id=upload['owner_id'], file_id=upload['id'])

    def send(self, peer_id: int, message_id: int, name: str) -> int:
        """
        Reply to user with message

        :param peer_id: peer ID of the user or chat to send message to
        :param message_id: message ID to reply to

        :return: message ID of the sent message
        """
        attachment = self.upload(name=name, peer_id=peer_id)
        if not attachment:
            message = self.config['messages']['upload_failed']
        elif random() < self.config['messages']['success_chance']:
            message = choice(self.config['messages']['success'])
        else:
            message = ''

        return self.vk.messages.send(
            peer_id = peer_id,
            reply_to = message_id,
            random_id = get_random_id(),
            attachment = self.upload(name, peer_id),
            message=message.format(
                name=name,
                base_url=self.config["images"]["base_url"],
                peer_id=peer_id,
                message_id=message_id))

    def process(self, event) -> bool:
        """
        Process an incoming message event

        :param event: Event object

        :return: True if bot replied to the message, False otherwise
        """
        for name, variants in self.config['images']['triggers'].items():
            text = event.object.message['text'].lower()
            if text in variants or text == '/' + name:
                if not self.locked(event):
                    self.send(event.object.message['peer_id'], event.object.message['id'], name)

    def start(self) -> None:
        while True:
            try:
                for event in self.longpoll.listen():
                    if event.type == VkBotEventType.MESSAGE_NEW:
                        Thread(target=self.process, args=(event,)).start()
            except KeyboardInterrupt:
                print("C-C signal received. T-T")
                break
            except Exception as e:
                print("Exception:", e)
                continue


            #  # Else if new subscriber
            #  elif event.type == VkBotEventType.GROUP_JOIN:
            #      # Update whitelist
            #      whitelist.add(event.object.user_id)
            #
            #  # Else if unsubscriber
            #  elif event.type == VkBotEventType.GROUP_LEAVE:
            #      # Update whitelist
            #      whitelist.remove(event.object.user_id)
