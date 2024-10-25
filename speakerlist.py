# ._. coding: utf-8

"""
 * voicevox_api_bridge.py
 * Copyright (c) 2024 UBinKitte
 *
 * Released under the MIT license.
 * see https://opensource.org/license/mit
 *
 * Don't forget, this script is just a API bridge for VOICEVOX.
 * visit https://github.com/VOICEVOX
 *
"""

from requests import get

from json import loads
from configparser import ConfigParser

config = ConfigParser()
config.read("./config.ini")

for speakers in loads(get(f"{config['VOICEVOX']['API']}/speakers").text):
    print(speakers["name"])
    for i in speakers["styles"]:
        print(f'- {i["name"]} = {i["id"]}')

    print()
