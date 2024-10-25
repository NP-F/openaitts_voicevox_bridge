# ._. coding: utf-8

"""
 * openaitts2voicevox_bridge.py
 * Copyright (c) 2024 UBinKitte
 *
 * Released under the MIT license.
 * see https://opensource.org/license/mit
 *
 * Don't forget, this script is just a API bridge for VOICEVOX.
 * visit https://github.com/VOICEVOX
 *
"""

from fastapi import FastAPI, Response
from pydantic import BaseModel
from pydub import AudioSegment

from pathlib import Path
from configparser import ConfigParser
from contextlib import asynccontextmanager
from threading import Thread

from voicevox_api_bridge import ifrm, voicevox_api, voicevox_launch, split_sentences


config = ConfigParser()
config.read("./config.ini")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    ifrm(Path(__file__).parent / ".wav")
    ifrm(Path(__file__).parent / ".mp3")


app = FastAPI(lifespan=lifespan)


class SpeechRequest(BaseModel):
    model: str
    voice: str
    input: str
    # 要るならコメント外してくれ
    # response_format: str
    # speed: str


@app.get("/", name="迷子のご案内")
async def root():
    return {
        "message": f"You have got this message by a mistake! Check http://localhost:{config['SETTINGS']['PORT']}/docs"
    }


# エンドポイントはOpenAIのSpeechAPIに依って変えてくれ
@app.post("/v1/audio/speech", name="音声合成をする")
async def generate_speech(request: SpeechRequest):
    speech_file_path = Path(__file__).parent / ".wav"
    mp3_file_path = Path(__file__).parent / ".mp3"

    ifrm(speech_file_path)
    ifrm(mp3_file_path)

    sentences = split_sentences(request.input)
    combined_audio = AudioSegment.empty()

    for sentence in sentences:
        voice = voicevox_api(sentence, request.voice)
        temp_wav = Path(__file__).parent / f"{sentences.index(sentence)}.wav"

        with open(temp_wav, mode="wb") as f:
            f.write(voice.content)

        combined_audio += AudioSegment.from_wav(temp_wav)
        ifrm(temp_wav)

    combined_audio = combined_audio.set_frame_rate(
        int(config["SOUND"]["SAMPLING_RATE"])
    )
    combined_audio = combined_audio.set_sample_width(int(config["SOUND"]["BITDEPTH"]))
    combined_audio.export(mp3_file_path, format="mp3")

    if Path.exists(mp3_file_path):
        with open(mp3_file_path, "rb") as audio_file:
            audio_data = audio_file.read()

        return Response(content=audio_data, media_type="audio/mpeg")
    else:
        return {"error": "Failed to generate speech"}


if __name__ == "__main__":
    if config["VOICEVOX"]["AUTOLAUNCH"] == "true":
        Thread(target=voicevox_launch, name="voicevox", daemon=True).start()

    from uvicorn import run as uvirun

    uvirun(app, host=config["SETTINGS"]["HOST"], port=int(config["SETTINGS"]["PORT"]))
