import time
import json

from time import sleep
from threading import Thread
from gevent.wsgi import WSGIServer
from haproxystats import HaproxyStats
from flask import Flask, Response, redirect, request, url_for

from version import version


class Poller(object):
    def __init__(self, server_list, user, password):
        self.stats = []
        self.hs = HaproxyStats(server_list,user=user,user_pass=password)

    def start(self, interval=10):
        t = Thread(target=self._run_forever, args=(interval,))
        t.daemon = True
        t.start()

    def to_json(self):
        return json.dumps(self.stats)

    def _run_forever(self, interval):
        print('Starting HAProxy Poller')
        while True:
            self.hs.update()
            self.stats = [ s.stats for s in self.hs.servers ] 
            sleep(interval)

class HaproxyView(object):
    """
    HaproxyView web app
    params:
      - poller(obj): Instantiated Poller object
    """
    def __init__(self, poller):
        self.app = Flask('haproxyview')
        self.app.config['poller'] = poller

        @self.app.route('/')
        def index():
            return redirect(url_for('static', filename='index.html'))

        @self.app.route('/stats')
        def stats():
            return self.app.config['poller'].to_json()

    def serve(self, listen_port=8000):
        print('Starting HaproxyView v%s' % version)
        http_server = WSGIServer(('', listen_port), self.app)
        http_server.serve_forever()
