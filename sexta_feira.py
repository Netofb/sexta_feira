import pygame
import sys
import time
import math
import speech_recognition as sr
import pyttsx3
import requests
from requests.exceptions import RequestException
import json
import webbrowser
import os
import subprocess
import psutil
import ctypes
import win32gui
import win32con
import win32api
import random
import winsound
import datetime
from pygame.locals import *
import numpy as np
import math
import time
from OpenGL.GL import *
from OpenGL.GLU import *

# Configurações do Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"
OLLAMA_TIMEOUT = 15

# Configurações do assistente
ASSISTANT_NAME = "Sexta-Feira"
VOICE_ID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PT-BR_MARIA_11.0"

# Inicializa engine de voz
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 0.9)

# Configurações do Windows
VOLUME_LEVEL = 50

# Inicialização do Pygame
pygame.init()
pygame.mixer.init()



def show_pixel_sphere():
    """Animação de abertura com esfera 3D de pixels e nome fixo do assistente"""
    pygame.init()
    display = (1280, 720)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | NOFRAME)  # NOFRAME: sem borda

    pygame.display.set_caption(f"{ASSISTANT_NAME} - Inicialização")
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -40)

    # Fundo preto (simula transparência)
    glClearColor(0.0, 0.0, 0.0, 0.0)

    # Som opcional
    pygame.mixer.init()
    try:
        pygame.mixer.music.load("sounds/quantum_startup.mp3")
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play()
    except:
        pass

    num_particles = 3000
    radius = 10
    particles = []

    for _ in range(num_particles):
        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)

        x = radius * math.sin(phi) * math.cos(theta)
        y = radius * math.sin(phi) * math.sin(theta)
        z = radius * math.cos(phi)

        particles.append({
            'initial_pos': np.array([random.uniform(-50, 50),
                                     random.uniform(-50, 50),
                                     random.uniform(-50, 50)], dtype=np.float32),
            'target_pos': np.array([x, y, z], dtype=np.float32),
            'current_pos': np.array([x, y, z], dtype=np.float32),
            'color': (random.uniform(0.1, 0.3), random.uniform(0.4, 0.8), 1.0, 1.0),
            'size': random.uniform(1.2, 2.5),
            'speed': random.uniform(0.01, 0.05)
        })

    # Texto do nome "Sexta-Feira" desde o início
    font = pygame.font.SysFont('Arial', 60)
    text_surface = font.render(ASSISTANT_NAME, True, (0, 200, 255, 255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)

    start_time = time.time()
    running = True
    rotation_angle = 0

    while running:
        current_time = time.time() - start_time
        if current_time > 9:
            break

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glRotatef(0.3, 0, 1, 0)
        rotation_angle += 0.3

        glPointSize(2.0)
        glBegin(GL_POINTS)
        for p in particles:
            direction = p['target_pos'] - p['current_pos']
            distance = np.linalg.norm(direction)
            if distance > 0.1:
                p['current_pos'] += direction * p['speed']

            glColor4fv(p['color'])
            glVertex3fv(p['current_pos'])
        glEnd()

        # Nome fixo desde o início
        glPushMatrix()
        glRotatef(-rotation_angle, 0, 1, 0)
        glRasterPos3d(-3, 0, 0)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(),
                     GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        glPopMatrix()

        pygame.display.flip()
        pygame.time.wait(16)

    pygame.quit()

    pass  # por brevidade, código omitido

def set_voice():
    try:
        voices = engine.getProperty('voices')
        for voice in voices:
            if "maria" in voice.id.lower():
                engine.setProperty('voice', voice.id)
                return
        engine.setProperty('voice', VOICE_ID)
    except Exception as e:
        print(f"Erro ao configurar voz: {str(e)}")

def speak(text, priority='normal'):
    print(f"{ASSISTANT_NAME.upper()}: {text}")
    try:
        set_voice()
        if priority == 'high':
            winsound.Beep(1000, 200)
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Erro na engine de voz: {str(e)}")

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("\nOuvindo...", end='', flush=True)
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            winsound.Beep(800, 100)
            audio = recognizer.listen(source, timeout=5)
            print("\r" + " " * 20 + "\r", end='')
            command = recognizer.recognize_google(audio, language="pt-BR")
            print(f"Você disse: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""  # Silenciosamente ignora
        except sr.RequestError:
            speak("Problema no serviço de voz. Verifique sua conexão.", 'high')
            return ""
        except Exception as e:
            print(f"Erro no reconhecimento: {str(e)}")
            return ""


def check_ollama_connection():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except RequestException:
        return False

def chat_with_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"""Você é {ASSISTANT_NAME}, assistente pessoal. 
        Responda em português brasileiro de forma concisa e profissional.
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
    if not command:
        return

    command = command.strip()
    print(f"Processando: {command}")

    if any(palavra in command for palavra in ["finalizar"]):
        speak("Encerrando sistemas. Até logo chefe!", 'high')
        sys.exit(0)

    elif "desligar computador" in command:
        speak("Iniciando desligamento em 60 segundos", 'high')
        os.system("shutdown /s /t 60")
        return

    elif "reiniciar computador" in command:
        speak("Preparando reinicialização em 60 segundos", 'high')
        os.system("shutdown /r /t 60")
        return

    elif "cancelar desligamento" in command:
        os.system("shutdown /a")
        speak("Sequência de desligamento cancelada", 'high')
        return

    elif "qual a boa de hoje" in command or "boa de hoje" in command:
        webbrowser.open("https://www.youtube.com/watch?v=f2D2hEFnHLU")
        speak("Olá chefe parabéns pelo seu trabalho, como vai seu dia?")
        return

    elif "encerrar abertura" in command:
        os.system("taskkill /f /im brave.exe")
        speak("encerrando abertura chefe")   
        return

    elif "abrir youtube" in command:
        webbrowser.open("https://www.youtube.com")
        speak("Acessando YouTube chefe")
        return

    elif "abrir google" in command:
        webbrowser.open("https://www.google.com")
        speak("Google ativado chefe")
        return

    elif "abrir steam" in command:
        os.system("start steam")
        speak("Steam ativado chefe")
        return

    elif "abrir notion" in command:
        os.system("start notion")
        speak("Notion disponível chefe")
        return

    elif "hora" in command:
        hora = datetime.datetime.now().strftime("%H:%M")
        speak(f"Relógio marca {hora} chefe")
        return

    elif "data" in command:
        data = datetime.datetime.now().strftime("%d/%m/%Y")
        speak(f"Hoje é dia {data} chefe")
        return

    elif "status do sistema" in command:
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        speak(f"Sistema operando com {cpu}% de CPU e {mem}% de memória")
        return

    elif any(palavra in command for palavra in ["quem é você", "seu nome", "qual seu nome"]):
        speak(f"Sou {ASSISTANT_NAME} a assistente pessoal do Chefe Fábio, estou Pronta para ajudar!")
        return

    elif "obrigado" in command or "valeu" in command:
        respostas = ["Sempre às ordens!", "De nada chefe!", "Disponha quando precisar!"]
        speak(random.choice(respostas))
        return

    # Consulta ao Ollama
    resposta = chat_with_ollama(command)
    speak(resposta)

def aguardar_ativacao():
    speak(f"Sistema iniciado. Diga 'ativar' para chamar a {ASSISTANT_NAME}.")
    while True:
        comando = listen()
        if "ativar" in comando:
            speak("Sistema ativado. Pode falar, chefe.", 'high')
            while True:
                comando_usuario = listen()
                if "stand by" in comando_usuario:
                    speak("Entrando em modo de espera, chefe.")
                    break
                execute_command(comando_usuario)

if __name__ == "__main__":
    show_pixel_sphere()
    aguardar_ativacao()
