import flask
import json
import uuid
import jwt
import smooch
from flask import Flask, request, Response
from redis import Redis
from smooch.rest import ApiException
from promise import Promise

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
redis = Redis(host='redis', port=6379)
root = "/api/1.0"

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

# PING
@app.route('/')
def ping():
    count = redis.incr('hits')
    return 'Hello World! I have been seen {} times.\n'.format(count)

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

def postCarousel(list, replies):
    message = smooch.MessagePost(role='appMaker', type='carousel')

    actions = []
    for reply in replies:
        actions.append(smooch.Action(type='postback', text=reply, payload=reply))

    items = []
    for item in list:
        items.append(smooch.MessageItem(title=item, actions=actions))

    message.items = items
    return message

def postList(list, replies):
    message = smooch.MessagePost(role='appMaker', type='list')

    actions = []
    for reply in replies:
        actions.append(smooch.Action(type='postback', text=reply, payload=reply))

    items = []
    for item in list:
        items.append(smooch.MessageItem(title=item, actions=actions))

    message.items = items
    return message

def parse_request_data(request_data):
    body = json.loads(request_data)

    # print(body['appUser'])
    user_id = body['appUser']['_id']

    for message in body['messages']:
        text = message['text']

        if text == "Hi":
            api_response = api_instance.post_message(APP_ID, user_id,
                postTextWithReplies("What do you want to chat about?", ['Jesus', 'Money', 'Rachel']))

        ### JESUS ###
        elif text == "Jesus":
            api_response = api_instance.post_message(APP_ID, user_id,
                postImage("http://www.truthandcharityforum.org/wp-content/uploads/2015/06/bible.jpg"))

        ### MONEY ###
        elif text == "Money":
            api_response = api_instance.post_message(APP_ID, user_id,
                postCarousel(['Plan Budget', 'Log Spending', 'Help Now'], ['Go']))

        elif text == "Plan Budget":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Are you happy to give your no?"))

        elif text == "Log Spending":
            api_response = api_instance.post_message(APP_ID, user_id,
                postText("Are you happy to give your no?"))

        elif text == "Help Now":
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

@app.route('/messages', methods=["POST"])
def handle_messages():
    # Delay bot response and return immediate response
    # to 'fix' facebook issue - https://chatbotsmagazine.com/listicle-of-things-missing-from-facebook-messenger-chatbot-platforms-documentation-d1d50922ef15
    Promise.resolve(parse_request_data(request.get_data()))
    return Response('ok', status=200)