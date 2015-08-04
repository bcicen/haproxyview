import os
import json
import yaml
from haproxystats import HaproxyStats
from threading import Thread
from time import sleep
from copy import deepcopy
from redis import StrictRedis

redis = StrictRedis()

class Poller(object):
    """
    """
    #defaults
    last_states = []
    user = None
    password = None
    interval = 5

    def __init__(self,config_file='config.yml'):
        with open(config_file) as of:
            config = yaml.load(of.read())

        if config.has_key('user'):
            user = config['user']
        if config.has_key('pass'):
            password = config['pass']
        if config.has_key('interval'):
            self.interval = config['interval']

        self.hs = HaproxyStats(config['servers'],user=user,user_pass=password)

        self._run_forever()

    def start(self):
        t = Thread(target=self._run_forever)
        t.daemon = True
        t.start()

    def _run_forever(self):
        print('poller started')
        while True:
            self.hs.update()
            current_states = [ s.stats for s in self.hs.servers ] 

            if current_states != self.last_states:
                redis.set('haproxyview_stats', json.dumps(current_states))
                redis.publish('haproxyview', 1)
                self.last_states = deepcopy(current_states) 
            
            sleep(self.interval)
