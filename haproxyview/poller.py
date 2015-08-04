import os
import json
from haproxystats import HaproxyStats
from threading import Thread
from time import sleep
from copy import deepcopy
from redis import StrictRedis

redis = StrictRedis()

class Poller(object):
    """
    """
    def __init__(self,server_list,user=None,password=None,interval=10):
        self.last_states = []
        self.interval = interval

        self.hs = HaproxyStats(server_list,user=user,user_pass=password)

        print('Starting poller with servers: \n%s' % '\n'.join(server_list))
        self._run_forever()

    def start(self):
        t = Thread(target=self._run_forever)
        t.daemon = True
        t.start()

    def _run_forever(self):
        while True:
            self.hs.update()
            current_states = [ s.stats for s in self.hs.servers ] 

            if current_states != self.last_states:
                redis.set('haproxyview_stats', json.dumps(current_states))
                redis.publish('haproxyview', 1)
                self.last_states = deepcopy(current_states) 
            
            sleep(self.interval)
