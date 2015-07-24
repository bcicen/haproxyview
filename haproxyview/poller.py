import os
import json
import yaml
from haproxystats import HaproxyStats
from threading import Thread
from time import sleep
from copy import deepcopy
from redis import StrictRedis

servers = [ 'lb-c.us-east-1.appcious.com:3212',
            'lb-c.ap-northeast-1.appcious.com:3212' ]
user = 'appcious_admin'
user_pass = 'Culotte-anton8058'

redis = StrictRedis()

class Poller(object):
    def __init__(self,config_file='config.yml'):
        with open(config_file) as of:
            config = yaml.load(of.read())

        self.last_states = ""

        self.hs = HaproxyStats(
                config['servers'],user=config['user'],user_pass=config['pass']
                )

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

            print current_states
            if current_states != self.last_states:
                redis.publish('haproxyview', json.dumps(current_states))
                self.last_states = deepcopy(current_states) 
            
            sleep(10)

    def _format(self):
        """
        Format stats, returning only the values we care about
        """

if __name__ == '__main__':
    p = Poller()
