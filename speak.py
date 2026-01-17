"""
Docstring for speak
"""

import pyttsx3
engine = pyttsx3.init() # object creation

# RATE
rate = engine.getProperty('rate')   # getting details of current speaking rate
print ('rate:',rate)                        # printing current voice rate
engine.setProperty('rate', 100)     # setting up new voice rate

# VOLUME
volume = engine.getProperty('volume')   # getting to know current volume level (min=0 and max=1)
print ('volume:',volume)                          # printing current volume level
engine.setProperty('volume',1.0)        # setting up volume level  between 0 and 1

# VOICE
voices = engine.getProperty('voices')

for voice in voices:
    if 'dutch' in voice.name.lower() or 'nederlands' in voice.name.lower():
        print(voice.name)
        engine.setProperty('voice', voice.id)

voice = engine.getProperty('voice')
print(voice)

zin = "Ik ben een spraak synthesizer" +'mijn huidige snelheid is ' + str(rate) + 'en mijn volume is ' + str(volume) + "Ik ga deze zin hardop voorlezen en opslaan in een bestand"

engine.say(zin)
# Blocks while processing all the currently queued commands
engine.runAndWait()
engine.stop()

# Saving Voice to a file
# On Linux, make sure that 'espeak-ng' is installed
engine.save_to_file('Hello World', 'test.mp3')
engine.runAndWait()

