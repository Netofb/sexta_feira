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

# Inicializa engine de voz
engine = pyttsx3.init()
engine.setProperty('rate', 200)
engine.setProperty('volume', 1.0)

# Configurações específicas do Windows
VOLUME_LEVEL = 50  # Valor padrão para controle de volume (0-100)

# Personalidade da Sexta-Feira
ASSISTANT_NAME = "Sexta-Feira"
ASSISTANT_VOICE_ID = 1  # Experimente alterar para mudar a voz (0 ou 1)

def play_sound(sound_type):
    """Efeitos sonoros característicos"""
    sounds = {
        'startup': lambda: winsound.PlaySound("SystemStart", winsound.SND_ALIAS),
        'error': lambda: winsound.PlaySound("SystemHand", winsound.SND_ALIAS),
        'success': lambda: winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS),
        'notification': lambda: winsound.Beep(1000, 200)
    }
    sounds.get(sound_type, lambda: None)()

def speak(text, priority='normal'):
    """Fala com a personalidade da Sexta-Feira"""
    print(f"{ASSISTANT_NAME.upper()}: {text}")
    try:
        # Configura voz feminina se disponível
        voices = engine.getProperty('voices')
        if len(voices) > ASSISTANT_VOICE_ID:
            engine.setProperty('voice', voices[ASSISTANT_VOICE_ID].id)
        
        if priority == 'high':
            play_sound('notification')
        
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Erro na engine de voz: {str(e)}")

def listen():
    """Ouve o usuário com o estilo da Sexta-Feira"""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nSexta-Feira está ouvindo...", end='', flush=True)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            play_sound('notification')
            audio = recognizer.listen(source, timeout=5)
            print("\r" + " " * 30 + "\r", end='')
            command = recognizer.recognize_google(audio, language="pt-BR")
            print(f"Você: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            speak("Interpretação falhou. Repita, por favor?", 'high')
            return ""
        except sr.RequestError:
            speak("Problema no serviço de voz. Verifique sua conexão.", 'high')
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
    """Consulta o Ollama com estilo da Sexta-Feira"""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"""Você é {ASSISTANT_NAME}, assistente pessoal. 
        Responda de forma inteligente e concisa em português, com personalidade marcante.
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
    """Executa comandos com a personalidade da Sexta-Feira"""
    if not command:
        return
        
    command = command.strip()
    print(f"Processando: {command}")
    
    # COMANDOS DE SISTEMA
    if any(palavra in command for palavra in ["desligar", "fechar", "encerrar"]):
        speak("Encerrando sistemas. Até breve!", 'high')
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
        speak("Sequência de desligamento abortada", 'high')
        return
        
    # CONTROLE DE APLICATIVOS
    elif "abrir youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Acessando YouTube")
        return
        
    elif "abrir google" in command:
        webbrowser.open("https://www.google.com")
        speak("Google ativado")
        return
        
    elif "abrir notepad" in command or "abrir bloco de notas" in command:
        os.system("start notepad")
        speak("Bloco de notas disponível")
        return
        
    # INFORMAÇÕES
    elif "hora" in command:
        hora = datetime.datetime.now().strftime("%H:%M")
        speak(f"Relógio marca {hora}")
        return
        
    elif "data" in command:
        data = datetime.datetime.now().strftime("%d/%m/%Y")
        speak(f"Hoje é dia {data}")
        return
        
    elif "status do sistema" in command:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        speak(f"Sistema operando com {cpu}% de CPU e {mem}% de memória utilizada")
        return
        
    # RESPOSTAS PERSONALIZADAS
    elif any(palavra in command for palavra in ["quem é você", "seu nome"]):
        speak(f"Sou {ASSISTANT_NAME}, sua assistente pessoal. Pronta para ajudar!")
        return
        
    elif "obrigado" in command or "valeu" in command:
        respostas = ["Sempre às ordens!", "De nada, chefe!", "Disponha quando precisar!"]
        speak(random.choice(respostas))
        return
        
    # CONSULTA AO OLLAMA PARA OUTROS COMANDOS
    play_sound('notification')
    resposta = chat_with_ollama(command)
    
    if resposta:
        speak(resposta)
    else:
        speak("Falha na análise. Reformule o comando.", 'high')

def set_volume(level):
    """Controle de volume com feedback tátil"""
    try:
        val = int(65535 * level / 100)
        win32api.SendMessage(
            win32con.HWND_BROADCAST,
            win32con.WM_APPCOMMAND,
            0x30292,
            val * 0x10000
        )
    except Exception as e:
        print(f"Erro no volume: {str(e)}")

def main():
    """Inicialização estilizada da Sexta-Feira"""
    play_sound('startup')
    speak(f"Sistemas {ASSISTANT_NAME} inicializando...", 'high')
    
    if not check_ollama_connection():
        speak("Atenção: Conexão limitada com Ollama", 'high')
    
    # Saudação personalizada
    saudacoes = [
        "Sistemas prontos para ação",
        "Operacional e online",
        "Tudo sob controle. Como posso ajudar?",
        "À sua disposição"
    ]
    
    hora = datetime.datetime.now().hour
    if 6 <= hora < 12:
        speak("Bom dia, chefe. " + random.choice(saudacoes))
    elif 12 <= hora < 18:
        speak("Boa tarde, chefe. " + random.choice(saudacoes))
    else:
        speak("Boa noite, chefe. " + random.choice(saudacoes))
    
    # Loop principal
    while True:
        try:
            comando = listen()
            if comando:
                execute_command(comando)
        except KeyboardInterrupt:
            speak("Interrupção de emergência detectada", 'high')
            sys.exit(1)
        except Exception as e:
            print(f"Erro: {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    main()