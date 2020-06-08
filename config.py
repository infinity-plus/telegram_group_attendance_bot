#!/usr/bin/python3

import os

class Config:
    bot_api = os.environ.get("bot_api", None) 

