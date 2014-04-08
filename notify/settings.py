# coding: utf-8

import os
import yaml

# Base path for project
BASE_PATH = os.path.dirname(__file__)

# Base path for logs folder
LOG_PATH = os.path.join(BASE_PATH, 'logs')

# Base path for configs folder
CONFIG_PATH = os.path.join(BASE_PATH, 'configs')

# Current DB Driver
DB_DRIVER = "postgresql"

# Parse DB Config
DB_CONFIG = {}
with open(os.path.join(CONFIG_PATH, 'database.yaml'), 'r') as file:
    DB_CONFIG = yaml.load(file, Loader=yaml.loader.BaseLoader)

# Parse AMQP Config
AMQP_CONFIG = {}
with open(os.path.join(CONFIG_PATH, 'amqp.yaml'), 'r') as file:
    AMQP_CONFIG = yaml.load(file, Loader=yaml.loader.BaseLoader)

    for k,v in AMQP_CONFIG.items():
        if 'spec_file' in v:
            AMQP_CONFIG[k]['spec_file'] = os.path.join(BASE_PATH, v['spec_file'])

#Status
APP_USER_LOGINED = 1
APP_CONNECTED    = 2
APP_DISCONECTED  = 3

LIST_STATE = {
    APP_USER_LOGINED: 'Get login',
    APP_CONNECTED   : 'User connected',
    APP_DISCONECTED : 'User disconnected',
}
