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

from requests import post

from logging import basicConfig, error, info
from os import remove
from os.path import exists
from subprocess import call
from json import dumps
from configparser import ConfigParser
from re import split

config = ConfigParser()
config.read("./config.ini")

voice_map = {
    "alloy": config["ALTID"]["ALLOY"],
    "echo": config["ALTID"]["ECHO"],
    "fable": config["ALTID"]["FABLE"],
    "onyx": config["ALTID"]["ONYX"],
    "nova": config["ALTID"]["NOVA"],
    "shimmer": config["ALTID"]["SHIMMER"],
}

basicConfig(level=0, format="%(levelname)s: %(message)s")


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def split_sentences(text):
    # あまりにも長い文章が来たら諦めろ
    sentences = split(r"(。)", text)
    return [
        "".join(sentences[i : i + int(config["SETTINGS"]["PARSERATE"])])
        for i in range(0, len(sentences), int(config["SETTINGS"]["PARSERATE"]))
    ]


def voicevox_launch():
    try:
        call([f"{config['VOICEVOX']['PATH']}"])
    except:
        error("")
        error(f"Cannot launch VOICEVOX. Check {config['VOICEVOX']['PATH']} exists.")
        error("")


def voicevox_api_runner(input, voice):
    query = post(
        f"{config['VOICEVOX']['API']}/audio_query",
        params={"text": input, "speaker": voice},
    )
    return post(
        f"{config['VOICEVOX']['API']}/synthesis",
        params={"speaker": voice},
        data=dumps(query.json()),
    )


def voicevox_api(input, voice):
    return voicevox_api_runner(
        input,
        (
            voice_map.get(voice, config["ALTID"]["DEFAULT_SPEAKER"])
            if not is_int(voice)
            else voice
        ),
    )


def ifrm(path):
    # 何が来るかわかんねえのでos.path.existsで
    if exists(path):
        remove(path)


def warn():
    info("This is not main file. You have to use openwebui2voicevox_api_bridge.py")


if __name__ == "__main__":
    warn()
