import os
import sys
import yaml
from argparse import ArgumentParser

from version import version 
from app import HaproxyView, Poller 

#defaults
config = { 'user': None,
           'pass': None,
           'interval': 10 }

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
