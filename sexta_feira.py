import speech_recognition as sr
import pyttsx3
import requests
from requests.exceptions import RequestException
import json
import webbrowser
import sys
import time
import datetime
import os
import subprocess
import psutil
import ctypes
import win32gui
import win32con
import win32api
import random
import winsound

# Configurações do Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"
OLLAMA_TIMEOUT = 15

# Configurações do assistente
ASSISTANT_NAME = "Sexta-Feira"
VOICE_ID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PT-BR_MARIA_11.0"

# Inicializa engine de voz com configurações personalizadas
engine = pyttsx3.init()
engine.setProperty('rate', 190)  # Velocidade da fala (180 palavras por minuto)
engine.setProperty('volume', 0.9)  # Volume (0.0 a 1.0)

# Configurações específicas do Windows
VOLUME_LEVEL = 50  # Valor padrão para controle de volume (0-100)

def play_sound(sound_type):
    """Efeitos sonoros do sistema"""
    sounds = {
        'startup': lambda: winsound.PlaySound("SystemStart", winsound.SND_ALIAS),
        'error': lambda: winsound.PlaySound("SystemHand", winsound.SND_ALIAS),
        'success': lambda: winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS),
        'notification': lambda: winsound.Beep(1000, 200)
    }
    sounds.get(sound_type, lambda: None)()

def set_voice():
    """Configura a voz específica da Maria"""
    try:
        voices = engine.getProperty('voices')
        for voice in voices:
            if "maria" in voice.id.lower():
                engine.setProperty('voice', voice.id)
                print(f"Voz configurada: {voice.name}")
                return
        
        # Se não encontrar pelo nome, usa o ID diretamente
        engine.setProperty('voice', VOICE_ID)
    except Exception as e:
        print(f"Erro ao configurar voz: {str(e)}")

def speak(text, priority='normal'):
    """Faz a Sexta-Feira falar usando a voz da Maria"""
    print(f"{ASSISTANT_NAME.upper()}: {text}")
    try:
        set_voice()  # Garante que a voz está configurada
        
        if priority == 'high':
            play_sound('notification')
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Erro na engine de voz: {str(e)}")

def listen():
    """Ouve os comandos de voz do usuário"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nOuvindo...", end='', flush=True)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            play_sound('notification')
            audio = recognizer.listen(source, timeout=5)
            print("\r" + " " * 20 + "\r", end='')
            command = recognizer.recognize_google(audio, language="pt-BR")
            print(f"Você disse: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            speak("Desculpe chefe não entendi", 'high')
            return ""
        except sr.RequestError:
            speak("Problema no serviço de reconhecimento de voz", 'high')
            return ""
        except Exception as e:
            print(f"Erro no reconhecimento: {str(e)}")
            return ""

def check_ollama_connection():
    """Verifica conexão com o Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except RequestException:
        return False

def chat_with_ollama(prompt):
    """Consulta o Ollama para respostas inteligentes"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"""Você é {ASSISTANT_NAME}, assistente pessoal feminina. 
        Responda em português brasileiro de forma educada e profissional.
        Contexto: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}
        
        Usuário: {prompt}
        {ASSISTANT_NAME}:""",
        "stream": False,
        "options": {"temperature": 0.7}
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        if response.status_code == 200:
            return response.json().get("response", "Sem resposta")
        return f"Erro no Ollama: {response.status_code}"
    except RequestException as e:
        return f"Erro de conexão: {str(e)}"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"

def execute_command(command):
    """Executa comandos específicos do Windows"""
    if not command:
        return
        
    command = command.strip()
    print(f"Processando: {command}")
    
    ################################## COMANDOS DE SISTEMA
    if any(palavra in command for palavra in ["desligar", "fechar", "encerrar"]):
        speak("Encerrando meus sistemas chefe, Até a proxima!", 'high')
        sys.exit(0)
        
    elif "desligar computador" in command:
        speak("Iniciando sequência de desligamento em 30 segundos", 'high')
        os.system("shutdown /s /t 30")
        return
        
    elif "reiniciar computador" in command:
        speak("Preparando para reinicialização em 30 segundos", 'high')
        os.system("shutdown /r /t 30")
        return
        
    elif "cancelar desligamento" in command:
        os.system("shutdown /a")
        speak("Sequência de desligamento cancelada", 'high')
        return
    ########################################## SAUDAÇÕES
    elif "sexta feira ta ai?" in command or "ta ai?" in command or "sexta feira ta" in command or "tá aí" in command or "tá" in command:
        speak("Estou sim chefe vamos começar o trabalho")
        webbrowser.open("https://www.youtube.com/watch?v=gvgrgWJqKz0")
        return    
    ################################################# CONTROLE DE APLICATIVOS
    elif "abrir youtube" in command or "youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Abrindo YouTube")
        return
        
    elif "abrir google" in command or "google" in command:
        webbrowser.open("https://www.google.com")
        speak("Acessando Google")
        return
        
    elif "abrir notepad" in command or "abrir bloco de notas" in command:
        os.system("start notepad")
        speak("Bloco de notas aberto")
        return

    ################################################################## INFORMAÇÕES
    elif "hora" in command:
        hora = datetime.datetime.now().strftime("%H:%M")
        speak(f"Agora são {hora}")
        return
        
    elif "data" in command:
        data = datetime.datetime.now().strftime("%d/%m/%Y")
        speak(f"Hoje é dia {data}")
        return
        
    elif "status do sistema" in command:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        speak(f"O sistema está usando {cpu}% da CPU e {mem}% da memória")
        return
        
    ############################ RESPOSTAS PERSONALIZADAS
    elif any(palavra in command for palavra in ["quem é você", "seu nome", "qual seu nome?"]):
        speak(f"Sou {ASSISTANT_NAME}, sua assistente pessoal. Como posso ajudar?")
        return
        
    elif "obrigado" in command or "valeu" in command:
        respostas = [
            "De nada, chefe!",
            "Fico feliz em ajudar!",
            "Às suas ordens!",
            "Disponha quando precisar!"
        ]
        speak(random.choice(respostas))
        return
        
    # CONSULTA AO OLLAMA PARA OUTROS COMANDOS
    resposta = chat_with_ollama(command)
    
    if resposta:
        speak(resposta)
    else:
        speak("Não consegui processar seu comando. Poderia reformular?", 'high')

def set_volume(level):
    """Controla o volume do sistema Windows"""
    try:
        val = int(65535 * level / 100)
        win32api.SendMessage(
            win32con.HWND_BROADCAST,
            win32con.WM_APPCOMMAND,
            0x30292,
            val * 0x10000
        )
    except Exception as e:
        print(f"Erro ao ajustar volume: {str(e)}")

def main():
    """Função principal de inicialização"""
    play_sound('startup')
    speak(f"Inicializando {ASSISTANT_NAME} sua assistente pessoal.", 'high')
    
    if not check_ollama_connection():
        speak("Atenção: Conexão com Ollama não disponível. Algumas funções estarão limitadas.", 'high')
    
    # Saudação de acordo com o horário
    hora = datetime.datetime.now().hour
    if 4 <= hora < 12:
        speak("Bom dia, chefe. Como posso ajudar?")
    elif 12 <= hora < 17:
        speak("Boa tarde, chefe. Em que posso ser útil?")
    else:
        speak("Boa noite, chefe. Quais são suas ordens?")
    
    # Loop principal
    while True:
        try:
            comando = listen()
            if comando:
                execute_command(comando)
        except KeyboardInterrupt:
            speak("Desligamento de emergência ativado chefe.", 'high')
            sys.exit(1)
        except Exception as e:
            print(f"Erro: {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    # Configura a voz antes de iniciar
    set_voice()
    main()