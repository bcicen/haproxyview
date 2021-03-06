import os
import sys
import time
import json
import yaml

from time import sleep
from threading import Thread
from gevent.wsgi import WSGIServer
from argparse import ArgumentParser
from haproxystats import HAProxyServer
from flask import Flask, Response, redirect, request, url_for

version = '0.5'
#defaults
config = { 'user': None,
           'pass': None,
           'interval': 10,
           'verify_ssl': True }

class Poller(object):
    def __init__(self, config):
        print('Starting poller with servers:%s' % config['servers'])

        self.stats = []
        self.hs = []
        for server in config['servers']:
            self.hs.append(
                    HAProxyServer(server,
                        user=config['user'],
                        password=config['pass'],
                        verify_ssl=config['verify_ssl'])
                    )

    def start(self, interval=10):
        t = Thread(target=self._run_forever, args=(interval,))
        t.daemon = True
        t.start()

    def to_json(self):
        return json.dumps(self.stats)

    def _run_forever(self, interval):
        print('Starting HAProxy Poller')
        while True:
            newstats = []
            for h in self.hs:
                h.update()
                newstats.append(h.stats)
            self.stats = newstats
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

    poller = Poller(config)

    poller.start(config['interval'])

    haproxyview = HaproxyView(poller)
    haproxyview.serve()

if __name__ == '__main__':
    main()
