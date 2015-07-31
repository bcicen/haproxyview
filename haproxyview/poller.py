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
    def __init__(self,config_file='config.yml'):
        with open(config_file) as of:
            config = yaml.load(of.read())

        self.last_states = ""
        user = None
        password = None
        
        if config.has_key('user'):
            user = config['user']
        if config.has_key('pass'):
            password = config['pass']

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
                redis.publish('haproxyview', json.dumps(current_states))
                self.last_states = deepcopy(current_states) 
            
            sleep(10)

    def _format(self):
        """
        Format stats, returning only the values we care about
        """
