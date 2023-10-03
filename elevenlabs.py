import requests
import os
import io

CHUNK_SIZE = 1024
url = "https://api.elevenlabs.io/v1/text-to-speech/{}"

headers = {
  "Accept": "audio/mpeg",
  "Content-Type": "application/json",
  "xi-api-key": os.environ['ELEVEN_API_KEY']
}

data = {
  "text": "Hi! My name is Bella, nice to meet you!",
  "model_id": "eleven_monolingual_v1",
  "voice_settings": {
    "stability": 0.5,
    "similarity_boost": 0.5
  }
}

def text_to_speach(voiceid, text):
    response = requests.post(url.format(voiceid), json={
        "text": text,
        "model_id": "eleven_multilingual_v2", # "eleven_monolingual_v1",
    }, headers=headers)
    return io.BytesIO(response.content)
    # with open('output.mp3', 'wb') as f:
    #   for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
    #       if chunk:
    #           f.write(chunk)
    #   return open('output.mp3', 'rb')