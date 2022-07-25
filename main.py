# Imports
import requests, io, random
from os import environ
from vk_api import VkApi, VkUpload
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


try:
    # Get variables
    token = environ['TOKEN']
    group_id = environ['GROUP_ID']

    # Init VK session
    vk_session = VkApi(token=token)
    longpoll = VkBotLongPoll(vk_session, group_id)
    uploader = VkUpload(vk_session)
    vk = vk_session.get_api()

    # Set whitelist
    whitelist = set(vk.groups.getMembers(group_id=group_id)['items'])

# If no token or group_id
except KeyError:
    print("TOKEN or GROUP_ID not found in .env file or environment variables")
    exit(1)

# If no internet connection
except requests.exceptions.ConnectionError:
    print("No internet connection")
    exit(2)

# If other error
except Exception as e:
    print("Unknown exception:", e)
    exit(3)



# Triggers
source = 'https://nekos.life/api/v2/img/'
triggers = {
    'smug': {'хех'},
    'gasm': {'стыд', 'кринж'},
    'goose': {'гусь', '[id581996842|@doshik01010]'},
    'cuddle': {'погладить', 'няшиться'},
    'avatar': {'аватар', 'аватарка', 'ава'},
    'slap': {'ударить', 'пощечина', 'пощёчина', 'уебать'},
    'pat': {'молодец', 'молодца', 'молодцу'},
    'feed': {'кормить', 'покормить'},
    'fox_girl': {'foxgirl', 'лиса'},
    'neko': {'неко', 'кишка'},
    'hug': {'обнять', 'обняться'},
    'kiss': {'поцеловать', 'поцеловаться'},
    'tickle': {'щекотать', 'щекотаться'},
    'spank': {'отшлепать', 'отшлёпать'},
    'waifu': {'вайфу', 'тян', 'тянка'},
    'ngif': {'nekogif', 'некогиф', 'некогифка', 'неко гиф'}
}

def run(event):
    for name, variants in triggers.items():
        text = event.object.message['text'].lower()
        if text in variants or text == name:
            send(name, event.object.message['peer_id'])
            return


def send(name: str, peer_id: int) -> bool:
    """
    Method to send message. Automatically downloads Image / GIF and sends it

    @param str name: the string to add to URL
    @param int peer_id: peer_id of the chat

    @return bool: true if message was sent
    """
    url = requests.get(source + name).json()['url']
    raw = requests.get(url)

    att = ''

    # If GIF
    if url.endswith('.gif'):
        # Upload as document
        upload = uploader.document_message(io.BytesIO(raw.content),
                title = 'From @catgirlbot: ' + name,
                peer_id = peer_id)['doc']
        # Set attachment URL
        att = 'doc{owner_id}_{doc_id}'.format(owner_id=upload['owner_id'], doc_id=upload['id'])

    # If JPG, JPED or PNG
    elif url.split('.')[-1] in ['jpg', 'jpeg', 'png']:
        # Upload as image
        upload = uploader.photo_messages(io.BytesIO(raw.content),
                peer_id = peer_id)[0]
        # Set attachment URL
        att = 'photo{owner_id}_{photo_id}'.format(owner_id=upload['owner_id'], photo_id=upload['id'])


    # Send message
    vk.messages.send(
        peer_id = peer_id,
        attachment = att,
        random_id = get_random_id())


def main():
    # Listen for events
    print("Starting")
    for event in longpoll.listen():
        try:
            # If event is new message
            if event.type == VkBotEventType.MESSAGE_NEW:
                # If message is from whitelist
                if event.object.message['from_id'] in whitelist:
                    # Run triggers
                    run(event)

            # Else if new subscriber
            elif event.type == VkBotEventType.GROUP_JOIN:
                # Update whitelist
                whitelist.add(event.object.user_id)

            # Else if unsubscriber
            elif event.type == VkBotEventType.GROUP_LEAVE:
                # Update whitelist
                whitelist.remove(event.object.user_id)
        except Exception as e:
            print("Exception:", e)
            continue



if __name__ == "__main__":
    main()
