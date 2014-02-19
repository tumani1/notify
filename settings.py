# coding: utf-8

import os
import yaml

# Base path for project
BASE_PATH = os.path.dirname(__file__)

# Base path for project
LOG_PATH = os.path.join(BASE_PATH, 'logs')

# Parse DB Config
DB_CONFIG = {}
with open(os.path.join(BASE_PATH, 'configs/database.yaml'), 'r') as file:
    DB_CONFIG = yaml.load(file, Loader=yaml.loader.BaseLoader)

# Parse AMQP Config
AMQP_CONFIG = {}
with open(os.path.join(BASE_PATH, 'configs/amqp.yaml'), 'r') as file:
    AMQP_CONFIG = yaml.load(file, Loader=yaml.loader.BaseLoader)

    if len(AMQP_CONFIG.keys()):
        for key in AMQP_CONFIG.keys():
            if 'port' in AMQP_CONFIG[key]:
                AMQP_CONFIG[key]['port'] = int(AMQP_CONFIG[key]['port'])


#Status
APP_USER_LOGINED = 1
APP_CONNECTED    = 2
APP_DISCONECTED  = 3

LIST_STATE = {
    APP_USER_LOGINED: "Get login",
    APP_CONNECTED   : "User connected",
    APP_DISCONECTED : "User disconnected",
}
