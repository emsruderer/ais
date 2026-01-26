"""
Dutch AIS talker
"""

# Import the required module for text
# to speech conversion
from gtts import gTTS
from playsound3 import playsound
import torch
from TTS.api import TTS

# Get device
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
tts = TTS('tts_models/nl/css10/vits').to(DEVICE)
FILENAME = 'output.wav'

#print(tts.speakers)
#tts = TTS('tts_models/multilingual/multi-dataset/xtts_v2').to(DEVICE)


spell_alphabet = {'A' : 'Alpha', 'B' :'Bravo', 'C': 'Charlie', 'D' : 'Delta', 'E': 'Echo', \
                  'F' : 'Foxtrot', 'G': 'Golf', 'H': 'Hotel',\
                  'I':'India', 'J': 'Juliett','K': 'Kilo', 'L': 'Lima', 'M': 'Mike',\
                  'N' : 'November', 'O': 'Oskar', 'P':'Papa',\
                  'Q': 'Quebec', 'R':'Romeo','S':'Sierra','T':'Tango','U':'Uniform',\
                  'V':'Victor','W':'Whiskey','X':'X-ray',\
                  'Y':'Yanke','Z':'Zoulou','0':'null','1':'één','2':'twee','3':'drie','4':'vier',\
                  '5':'vijf','6':'zes','7':'zeven','8':'acht','9':'negen'}

nl_number = [ "nul", " één", "twee", "drie","vier", "vijf", "zes", "zeven",\
              "acht", "negen", "tien",\
              "elf", "twaalf", "dertien", "veertien","vijftien","zestien", \
              "zeventien", "achttien", "negentien","twintig"]

nl_tientallen = ["","tien","twintig","dertig","veertig", "vijftig","zestig",\
                 "zeventig", "tachtig", "negentig","honderd"]

nl_hoderdtallen = ["honderd", "tweehonderd",]


def str_getal(number):
    """ convert number to spoken dutch text """
    number = abs(int(number)) # ensure positive integer
    if number == 0:
        return ""
    if number <= 20:
        return nl_number[number]
    if number < 100:
        if number % 10 == 0:
            return  nl_tientallen[number//10]
        return  nl_number[number%10] + "en" +nl_tientallen[number//10]
    if number < 3000:
        if number // 100 < 2:
            return "honderd" + str_getal(number%100)
        if number // 100 == 10:
            return "duizend " + str_getal(number%1000)
        return str_getal(number//100) + "honderd" +str_getal(number%100)
    if number < 10000:
        return nl_number[number//1000] + "duizend" + str_getal(number%1000)
    if number < 1000000:
        return str_getal(number//1000) + "duizend " + str_getal(number%1000)
    if number < 1000000000:
        return str_getal(number//1000000) + " miljoen " + str_getal(number%1000000)
    return "weet ik niet"

def str_number(number:float):
    """ convert number to spoken dutch text """
    if number < 0:
        return "min " + str_getal(-number)
    if number < 1.0:
        return "nul komma " + str_getal(int(number*10))
    return str_getal(int(number))


def spell_callsign(callsign: str):
    """ convert callsign to spoken text """
    cs = ' '
    for ch in callsign:
        #if ch in ['0','1','2'.'3','4','5'.'6','7','8','9']:
        cs += spell_alphabet[ch] + ' '
    return cs


def say_number(number : int):
    """ convert number to spoken dutch text """
    gTTS(text=str_number(number), lang='nl', slow=False).save("call.mp2")
    gTTS(text=str_number(number), lang='nl', slow=False).save("call.mp2")
    playsound("call.mp2")

# TTS to a file, use a preset speaker
def speak_tts(txt: str, filename = FILENAME):
    """ convert text to spoken dutch text """
    tts.tts_to_file(
        text= txt, #speaker = 'Craig Gutsy', language = 'nl',
        file_path=filename
        )
    playsound( filename)

# GTTs to a file
def speak_gtts(txt: str, filename = FILENAME):
    """
    speak
    :param txt: text to say
    """
    gtts = gTTS(txt, lang='nl')
    gtts.save(filename)
    playsound(filename)

# Main speak switcher function
def speak(msg: str, soundfile=FILENAME):
    """
    selection function for speech module
    :param msg: string to speak
    :type msg: str
    """
    speak_gtts(msg, soundfile )


if __name__ == "__main__":
    for k, v in spell_alphabet.items():
        print(k,v)
    print(spell_callsign('PC1234'))
    speak(str_number(0.5))
    speak(str_number(-3))
    speak("Een Nederlandse tekst")
    speak("AIS spraak bericht systeem gestart")
    speak("Schip naam " + 'mijn boot')
    speak("MMSI " + str_number(264030000))
    speak("Oproep teken " + spell_callsign('PC1234'))
    for i in range(9,13):
        speak(str_number(i))
    for i in range(19,22):
        speak(str_number(i))
    for i in range(199,203):
        speak( str_number(i))
    for i in range(999,1003):
        speak(str_number(i))
    for i in range(2995,3005):
        speak(str_number(i))
    #say_number(0)
    #say_number(244030153)
