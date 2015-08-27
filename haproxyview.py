import os
import sys
import time
import json
import yaml

from time import sleep
from threading import Thread
from gevent.wsgi import WSGIServer
from argparse import ArgumentParser
from haproxystats import HaproxyStats
from flask import Flask, Response, redirect, request, url_for

version = '0.5'
#defaults
config = { 'user': None,
           'pass': None,
           'interval': 10 }

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

def main():
    parser = ArgumentParser(description='haproxyview %s' % (version))
    parser.add_argument('-c',
                        dest='config_path',
                        help='Path to config file',
                        default='config.yml')

    args = parser.parse_args()
    config_path = os.path.expanduser(args.config_path)

    with open(config_path) as of:
        config.update(yaml.load(of.read()))

    print(config['servers'])
    poller = Poller(config['servers'], config['user'], config['pass'])
    poller.start(config['interval'])

    haproxyview = HaproxyView(poller)
    haproxyview.serve()

if __name__ == '__main__':
    main()
