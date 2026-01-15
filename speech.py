"""
Dutch AIS talker
"""

# Import the required module for text
# to speech conversion
from gtts import gTTS
from matplotlib import text
from playsound3 import playsound
import socket

spell_alphabet = {'A' : 'Alpha', 'B' :'Bravo', 'C': 'Charlie', 'D' : 'Delta', 'E': 'Echo', 'F' : 'Foxtrot', 'G': 'Golf', 'H': 'Hotel',
                  'I':'India', 'J': 'Juliett','K': 'Kilo', 'L': 'Lima', 'M': 'Mike', 'N' : 'November', 'O': 'Oskar', 'P':'Papa',
                  'Q': 'Quebec', 'R':'Romeo','S':'Sierra','T':'Tango','U':'Uniform','V':'Victor','W':'Whiskey','Y':'Yanke','Z':'Zoulou',
                   '0':'0','1':'1','2':'2','3':'3','4':'4','5':'5','6':'6','7':'7','8':'8','9':'9'}

nl_number = [ "", " één", "twee", "drie","vier", "vijf", "zes", "zeven", "acht", "negen", "tien",\
              "elf", "twaalf", "dertien", "veertien","vijftien","zestien", "zeventien", "achttien", "negentien","twintig"]

nl_tientallen = ["","tien","twintig","dertig","veertig", "vijftig","zestig", "zeventig", "tachtig", "negentig","honderd"]

nl_hoderdtallen = ["honderd", "tweehonderd",]

mmsi = 264030000
shipsname = 'mijnboot'
callsign = 'PC1234'



def str_number(number):
    """ convert number to spoken dutch text """
    number = abs(int(number)) # ensure positive integer
    if number == 0:
        return "nul"
    elif number <= 20:
        return nl_number[number]
    elif number < 100:
        #text_number = nl_number[number%10]
        if number % 10 == 0:
            return  nl_tientallen[number//10]
        else:
            return  nl_number[number%10] + "en" +nl_tientallen[number//10]
    elif number < 3000:
        if number // 100 < 2:
            return "honderd" + str_number(number%100)
        elif number // 100 == 10:
            return "duizend " + str_number(number%1000)
        else:
            return str_number(number//100) + "honderd" +str_number(number%100)
    elif number < 10000:
        return nl_number[number//1000] + "duizend" + str_number(number%1000)
    elif number < 1000000:
        return str_number(number//1000) + "duizend " + str_number(number%1000)
    elif number < 1000000000:
        return str_number(number//1000000) + " miljoen " + str_number(number%1000000)
    else:
        return "weet ik niet"

def spell_callsign(callsign):
    """ convert callsign to spoken text """
    cs = ' '
    for ch in callsign:
        cs += spell_alphabet[ch] + ' '
    return cs+', '


def say_number(number):
    """ convert number to spoken dutch text """
    gTTS(text=str_number(number), lang='nl', slow=False).save("call.mp2")
    gTTS(text=str_number(number), lang='nl', slow=False).save("call.mp2")
    playsound("call.mp2")

def speak(text: str):
    """ convert text to spoken dutch text """
    gTTS(text=text, lang='nl', slow=False).save("call.mp2")
    playsound("call.mp2")

if __name__ == "__main__":
    speak("AIS spraak bericht systeem gestart")
    speak("Schip naam " + shipsname)
    speak("MMSI " + str_number(mmsi))
    speak("Oproep teken " + spell_callsign(callsign))
    for number in range(9,13):
        speak(number=number)
    for i in range(19,22):
        speak(number=i)
    for i in range(199,203):
        speak(number=i)
    for i in range(999,1003):
        speak(number=i)
    for i in range(2995,3005):
        speak(number=i)
    say_number(0)
    say_number(244030153)
       #cp = subprocess.run(playsound("call.mp2"),capture_output = True)

