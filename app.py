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


def parse_request_data(request_data):
    body = json.loads(request_data)

    # print(body['appUser'])
    user_id = body['appUser']['_id']
    
    message_body_response = smooch.MessagePost(role='appMaker', type='text', text="Hello my friend!")

    # Generate api response
    # try:
    api_response = api_instance.post_message(APP_ID, user_id, message_body_response)

@app.route('/messages', methods=["POST"])
def handle_messages():
    # Delay bot response and return immediate response
    # to 'fix' facebook issue - https://chatbotsmagazine.com/listicle-of-things-missing-from-facebook-messenger-chatbot-platforms-documentation-d1d50922ef15
    Promise.resolve(parse_request_data(request.get_data()))
    return Response('ok', status=200)