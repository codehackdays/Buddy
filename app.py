from flask import Flask, request, Response
from redis import Redis
import flask
import json
import uuid

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())
redis = Redis(host='redis', port=6379)
root = "/api/1.0"


### Health Checks

# PING
@app.route('/')
def ping():
    count = redis.incr('hits')
    return 'Hello World! I have been seen {} times.\n'.format(count)