""" write ais warn message to file ais_msg.txt"""

from os import path, getcwd, mkdir, sep
from datetime import datetime
from speech import speak

TRAINING_DATA_DIR = 'training_data'
SIMPLE_TEXT = False # No special words/characters in text

message_number = 0 # global message number

working_dir = getcwd()

if not path.exists(TRAINING_DATA_DIR):
    mkdir(TRAINING_DATA_DIR)


AUDIO_DATA_DIR  = TRAINING_DATA_DIR + sep + 'wavs'

if not path.exists(TRAINING_DATA_DIR + sep + 'wavs'):
    mkdir(TRAINING_DATA_DIR + sep + 'wavs')

FN = 'metadata.txt'

try:
    f = open(TRAINING_DATA_DIR + sep + FN, 'r', encoding="utf-8")
    for l in f.readlines():
        message_number += 1
        print(str(message_number),l, end='')
except FileNotFoundError as er:
    print(er)

# Generate filename if not provided


def add_msg(msg):
    """ add ais message to message file"""
    global message_number
    message_number += 1
    soundfile = 'audio' + str(message_number)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if SIMPLE_TEXT:
        out = soundfile + '|' + msg  + '\n'
    else:
        out = soundfile + '|' + msg + '|' + msg + '\n' # original and normalized text, TO DO: timestamp should be duration
    soundfile = soundfile + '.wav'

    with open(TRAINING_DATA_DIR + sep + FN, mode = 'a', encoding = "utf-8") as f:
        f.write(out)
        print(message_number,out, end='')
    speak(msg, AUDIO_DATA_DIR + sep + soundfile)


if __name__ == '__main__':
    add_msg('Eerste regel tekst')
    add_msg('Tweede regel tekst')