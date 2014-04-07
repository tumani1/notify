# coding: utf-8

import os
import yaml

# Base path for project
BASE_PATH = os.path.dirname(__file__)

# Base path for project
LOG_PATH = os.path.join(BASE_PATH, 'logs')

# Current DB Driver
DB_DRIVER = "postgresql"

# Parse DB Config
DB_CONFIG = {}
with open(os.path.join(BASE_PATH, 'configs/database.yaml'), 'r') as file:
    DB_CONFIG = yaml.load(file, Loader=yaml.loader.BaseLoader)

# Parse AMQP Config
AMQP_CONFIG = {}
with open(os.path.join(BASE_PATH, 'configs/amqp.yaml'), 'r') as file:
    AMQP_CONFIG = yaml.load(file, Loader=yaml.loader.BaseLoader)

#Status
APP_USER_LOGINED = 1
APP_CONNECTED    = 2
APP_DISCONECTED  = 3

LIST_STATE = {
    APP_USER_LOGINED: 'Get login',
    APP_CONNECTED   : 'User connected',
    APP_DISCONECTED : 'User disconnected',
}
