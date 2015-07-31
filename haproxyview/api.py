import itertools
import time
from flask import Flask, Response, redirect, request, url_for
from __init__ import __version__ as version
from redis import StrictRedis

app = Flask('haproxyview')

redis = StrictRedis()

@app.route('/')
def index():
    if request.headers.get('accept') == 'text/event-stream':
        def events():
            pubsub = redis.pubsub(ignore_subscribe_messages=True)
            pubsub.subscribe('haproxyview')
            for e in pubsub.listen():
                yield('data: %s\n\n' % e['data'])

        return Response(events(), content_type='text/event-stream')
    return redirect(url_for('static', filename='index.html'))

@app.route('/stats')
def stats():
    return redis.get('haproxyview_stats')

if __name__ == "__main__":
    app.logger.info('Starting HAProxyView v%s' % version)
    app.run(host='localhost', port=5000)
