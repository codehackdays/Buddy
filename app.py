import flask
import json
import uuid
import jwt
import smooch
from flask import Flask, request, Response
from redis import Redis
from smooch.rest import ApiException
from promise import Promise
from persistence import Persistence

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
# redis = Redis(host='redis', port=6379)
db = Persistence()
redis = db.db
# redis.flushall()

# Load environment variables
with open('env-vars.json') as env_vars_json:
    data = json.load(env_vars_json)

APP_ID = data['SMOOCH_APP_ID']
KEY_ID = data['SMOOCH_KEY_ID']
SECRET = data['SMOOCH_SECRET']

def generate_jwt_token():
    token_bytes = jwt.encode({
            'scope': 'app'
        },
        SECRET,
        algorithm='HS256',
        headers={
            'kid': KEY_ID
        })
    return token_bytes.decode('utf-8')

# Configure API key authorization: jwt
smooch.configuration.api_key['Authorization'] = generate_jwt_token()
smooch.configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
api_instance = smooch.ConversationApi()
app_create_body = smooch.AppCreate() # AppCreate | Body for a createApp request.


### Health Checks


# IMAGES
def image(text):
    if text == "Christmas":
        return "http://img.ehowcdn.com/615x200/ehow/images/a06/11/et/small-christmas-gift-ideas-boyfriend-1.1-800x800.jpg"
    elif text == "Easter":
        return "http://www.beliefnet.com/columnists//deaconsbench/files/import/assets_c/2010/04/jesus-cross-thumb-400x528-12594.jpg"
    elif text == "Budgeting":
        return "https://www.aiadallas.org/media/uploads/event-images/budget_thumbnail.png"
    elif text == "Spending":
        return "http://thumbnails.billiondigital.com/297/151/1151297/1151253_small_checkboard.jpg"
    elif text == "Talk":
        return "https://rfclipart.com/image/thumbnail/22-f6-00/small-coffee-cup-Download-Free-Vector-File-EPS-677.jpg"
    else:
        return ""

# PING
@app.route('/')
def ping():
    # Pull all database data and log on screen
    all_messages = json.dumps([eval(redis.get(key).decode('utf8')) for key in redis.scan_iter("messages-*")])
    return Response(all_messages, status=200)

def postText(text):
    message = smooch.MessagePost(role='appMaker', type='text')
    message.text = text

    return message

def postTextWithReplies(text, replies):
    message = smooch.MessagePost(role='appMaker', type='text')
    message.text = text

    actions = []
    for reply in replies:
        actions.append(smooch.Action(type='reply', text=reply, payload=reply))

    message.actions = actions
    return message

def postImage(uri):
    message = smooch.MessagePost(role='appMaker', type='image')
    message.media_url = uri

    return message

def postFile(uri):
    message = smooch.MessagePost(role='appMaker', type='file')
    message.media_url = uri

    return message

def postCarousel(list):
    message = smooch.MessagePost(role='appMaker', type='carousel')

    items = []
    for item in list:
        actions = []
        actions.append(smooch.Action(type='postback', text=item, payload=item))

        part = smooch.MessageItem(title=item, actions=actions)
        part.media_url = image(item)
        part.size = 'compact'
        items.append(part)

    message.items = items
    return message

def postList(list):
    message = smooch.MessagePost(role='appMaker', type='list')

    items = []
    for item in list:
        actions = []
        actions.append(smooch.Action(type='postback', text=item, payload=item))

        part = smooch.MessageItem(title=item, actions=actions)
        items.append(part)

    message.items = items
    return message

# Request handling logic
def parse_request_data(request_data):
    body = json.loads(request_data)

    user_id = body['appUser']['_id']

    for message in body['messages']:
        text = message['text']

        if text == "Help":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Just say Hi, we can talk about Jesus or Money."))

        elif text == "Hello" or text == "Hey" or text == "Hi":
            api_response = api_instance.post_message(APP_ID, user_id,
                postTextWithReplies("What do you want to chat about?", ['Jesus', 'Money', 'Rachel']))

        ### JESUS ###
        elif text == "Jesus":
            api_response = api_instance.post_message(APP_ID, user_id,
                postCarousel(['Christmas', 'Easter', 'Talk']))

        elif text == "Christmas":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Are you happy to give your no?"))

        elif text == "Easter":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Are you happy to give your no?"))

        elif text == "Talk":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Are you happy to give your no?"))

        ### MONEY ###
        elif text == "Money":
            api_response = api_instance.post_message(APP_ID, user_id,
                postCarousel(['Budgeting', 'Spending', 'Talk']))

        elif text == "Budgeting":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Are you happy to give your no?"))

        elif text == "Spending":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Are you happy to give your no?"))

        elif text == "Talk":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Are you happy to give your no?"))

        ### RACHEL ###
        elif text == "Rachel":
            api_response = api_instance.post_message(APP_ID, user_id,
                postFile("http://rachelschallenge.org/media/media_press_kit/Code_of_ethics.pdf"))

        elif text == "":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Speachless"))

        else:
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("I haven't learned that one yet"))
    '''
    # Persist message to database
    author_id = body['messages'][0]['authorId']
    message = body['messages'][0]['text']
    persistence_data = None
    existing_author_info = None

    # if key exists then load its data
    if db.key_exists(author_id):
        existing_author_db_data = db.load_messages(author_id)
        existing_author_info = json.loads(existing_author_db_data)
        db.delete_messages(author_id) # remove key since its being retrieved and stored in memory
    
    # Update db key if pre-existing
    if isinstance(existing_author_info, (list)):
        existing_author_info.append(message) # Problem here as it overrites list
        persistence_data = json.dumps(existing_author_info)
        print(persistence_data)
        # perhaps delete that exists since we have retrieved its data in memory?
    else:
        persistence_data = json.dumps([message])
    
    # Then finally save...
    db.save_message(author_id, persistence_data)
    '''

@app.route('/messages', methods=["POST"])
def handle_messages():
    # print(request.get_json())
    # Delay bot response and return immediate response
    # to 'fix' facebook issue - https://chatbotsmagazine.com/listicle-of-things-missing-from-facebook-messenger-chatbot-platforms-documentation-d1d50922ef15
    Promise.resolve(parse_request_data(request.get_data()))
    return Response('ok', status=200)