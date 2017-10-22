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

# PING
@app.route('/')
def ping():
    count = redis.incr('hits')
    # return 'Hello World! I have been seen {} times.\n'.format(count)
    all_messages = json.dumps([
        # eval(redis.get(key).decode('utf8')) for key in redis.scan_iter("messages-*")
        redis.get(key).decode('utf8') for key in redis.scan_iter("messages-*")
    ])
    return Response(all_messages, status=200)

# Component Types
def postText(body):
    return smooch.MessagePost(role='appMaker', type='text', text=body)

def postImage(uri):
    return smooch.MessagePost(role='appMaker', type='image', media_url=uri)

def postFile(uri):
    return smooch.MessagePost(role='appMaker', type='file', media_url=uri)

def postLocation(mapLat, mapLong):
    return smooch.MessagePost(role='appMaker', type='location', lat=mapLat, long=mapLong)

def postCarousel(body):
    return smooch.MessagePost(role='appMaker', type='carousel', items=body)

def postList(body):
    return smooch.MessagePost(role='appMaker', type='list', items=body)

# Request handling logic
def parse_request_data(request_data):
    body = json.loads(request_data)

    user_id = body['appUser']['_id']

    # Persist message to database
    author_id = body['messages'][0]['authorId']
    message = body['messages'][0]['text']
    persistence_data = None
    existing_author_info = None

    try:
        existing_author_db_data = db.load_messages(author_id)
        existing_author_info = json.load(existing_author_db_data)
    except:
        print('Problem parsing db data')
    
    # Update db key if preexisting
    if isinstance(existing_author_info, (list)):
        existing_author_info.append(message)
        persistence_data = json.dumps(existing_author_info)
    else:
        persistence_data = json.dumps(message)
    
    db.save_message(author_id, persistence_data)

    # Generate api response
    api_response = api_instance.post_message(APP_ID, user_id, postText("Hi mate"))
    # api_response = api_instance.post_message(APP_ID, user_id, postImage("http://www.truthandcharityforum.org/wp-content/uploads/2015/06/bible.jpg"))
    # api_response = api_instance.post_message(APP_ID, user_id, postFile("http://rachelschallenge.org/media/media_press_kit/Code_of_ethics.pdf"))

@app.route('/messages', methods=["POST"])
def handle_messages():
    print(request.get_json())
    # Delay bot response and return immediate response
    # to 'fix' facebook issue - https://chatbotsmagazine.com/listicle-of-things-missing-from-facebook-messenger-chatbot-platforms-documentation-d1d50922ef15
    Promise.resolve(parse_request_data(request.get_data()))
    return Response('ok', status=200)