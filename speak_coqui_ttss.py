
"""
 speak-tts with coqui tts library
"""
from io import BytesIO, BufferedWriter
import subprocess
import torch
from TTS.api import TTS
from gtts import gTTS
from playsound3 import playsound
# Get device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

FILENAME ='output.wav'

#tts = TTS('tts_models/nl/css10/vits').to(device)
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(DEVICE)


TXT = "Waarschuwing!, Naderend Tjechisch schip, met tien knopen, op koers vijftien graden, type schip: Unknown, over vierentwintig minuten, kleinste afstand zeshonderddrieennegentig meter, nu op DRIE mijl van ons vandaan, in richting achtenzeventig."

def speak_gtts(txt):
  """
  speak
  :param txt: text to say
  """
  gtts = gTTS(txt, lang='nl')
  gtts.save('output.mp3')
  playsound('output.mp3')




def speak_tts(msg):
  """ TTS to a file, use a preset speaker """
  tts.tts_to_file(
    text=txt,
    language ='nl',
    speaker = 'Craig Gutsy',
    file_path=FILENAME
  )
  playsound(FILENAME)


def speak(msg):
  """
  Docstring for speak

  :param msg: Description
  """
  speak_gtts(msg)


if __name__ == '__main__':
  speak(TXT)

#print(TTS().list_models())
#print(tts.speakers)
"""
method) def tts_to_file(
    text: str,
    speaker: str | None = None,
    language: str | None = None,
    speaker_wav: str | PathLike[Any] | list[str | PathLike[Any]] | None = None,
    emotion: str | None = None,
    pipe_out: Any | None = None,
    file_path: str = "output.wav",
    split_sentences: bool = True,
    **kwargs: Any
) -> str
Convert text to speech.

Args
text : str
Input text to synthesize.

speaker : str, optional
Speaker name for multi-speaker. You can check whether loaded model is multi-speaker by tts.is_multi_speaker and list speakers by tts.speakers. Defaults to None.
"""
import torch
from TTS.api import TTS

# Get device
device = "cuda" if torch.cuda.is_available() else "cpu"
#tts = TTS('tts_models/nl/css10/vits').to(device)
tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(device)

#print(TTS().list_models())
print(tts.speakers)


# TTS to a file, use a preset speaker
tts.tts_to_file(
  text="Waarschuwing!, Naderend Tjechisch schip, met tien knopen, op koers vijftien graden, type schip: Unknown, over vierentwintig minuten, kleinste afstand zeshonderddrieennegentig meter, nu op DRIE mijl van ons vandaan, in richting achtenzeventig.",
  language ='nl',
  speaker = 'Craig Gutsy',
  file_path='output.mp2'
)

# Initialize TTS with the target model name
#tts = TTS("tts_models/de/thorsten/tacotron2-DDC").to(device)

# Run TTS
#tts.tts_to_file(text="Ich bin eine Testnachricht.", file_path="output.wav")

# List available 🐸TTS models
print(TTS().list_models())

# Init TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

# Run TTS
# ❗ Since this model is multi-lingual voice cloning model, we must set the target speaker_wav and language
# Text to speech list of amplitude values as output
wav = tts.tts(text="Hello world!", speaker_wav="./audio.wav", language="nl")
# Text to speech to a file
tts.tts_to_file(text="Hello world!", speaker_wav="./audio.wav", language="en", file_path="output.wav")