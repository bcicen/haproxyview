import os
import sys
import yaml
from argparse import ArgumentParser
from version import __version__
from poller import Poller

#defaults
config = { 'user': None,
           'pass': None,
           'interval': 5 }

if __name__ == '__main__':
    parser = ArgumentParser(description='haproxyview %s' % (__version__))
    parser.add_argument('-c',
                        dest='config_file',
                        help='Path to config file (default: ./config.yml)',
                        default='config.yml')

    args = parser.parse_args()
    config_file = os.path.expanduser(args.config_file)

    with open(config_file) as of:
        config.update(yaml.load(of.read()))

    p = Poller(
            config['servers'],
            user=config['user'],
            password=config['pass'],
            interval=config['interval']
            )
