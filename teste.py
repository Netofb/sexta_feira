import pyttsx3
engine = pyttsx3.init()
engine.setProperty('voice', "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PT-BR_MARIA_11.0")
engine.say("Olá chefe, sou a Sexta-Feira. Como posso ajudar?")
engine.runAndWait()