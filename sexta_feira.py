import sys
import os
import math
import time
import json
import random
import psutil
import pygame
import webbrowser
import requests
import datetime
import numpy as np
import pyttsx3
import winsound
import speech_recognition as sr
from requests.exceptions import RequestException
from pygame.locals import DOUBLEBUF, OPENGL, NOFRAME, QUIT
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective

# Configurações
ASSISTANT_NAME = "Sexta-Feira"
VOICE_ID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_PT-BR_MARIA_11.0"
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"
OLLAMA_TIMEOUT = 15

# Inicializa engine de voz
engine = pyttsx3.init()
engine.setProperty('rate', 180)
engine.setProperty('volume', 0.9)

pygame.init()
pygame.mixer.init()

def show_pixel_sphere():
    display = (1280, 720)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL | NOFRAME)
    pygame.display.set_caption(f"{ASSISTANT_NAME} - Inicialização")
    
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -40)
    glClearColor(0.0, 0.0, 0.0, 0.0)

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
        theta = random.uniform(0, 2 * math.pi)  # Usando random do Python
        phi = random.uniform(0, math.pi)       # Usando random do Python
        x = radius * math.sin(phi) * math.cos(theta)
        y = radius * math.sin(phi) * math.sin(theta)
        z = radius * math.cos(phi)
        
        # CORREÇÃO AQUI: Substitua np.random.uniform por random.uniform
        particles.append({
            'initial_pos': np.array([random.uniform(-50, 50) for _ in range(3)]),
            'target_pos': np.array([x, y, z], dtype=np.float32),
            'current_pos': np.array([random.uniform(-50, 50) for _ in range(3)]),
            'color': (random.uniform(0.1, 0.3), random.uniform(0.4, 0.8), 1.0, 1.0),
            'size': random.uniform(1.2, 2.5),
            'speed': random.uniform(0.01, 0.05)
        })

    font = pygame.font.SysFont('Arial', 60)
    text_surface = font.render(ASSISTANT_NAME, True, (0, 200, 255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)

    start_time = time.time()
    rotation_angle = 0

    while time.time() - start_time < 9:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glRotatef(0.3, 0, 1, 0)
        rotation_angle += 0.3

        glBegin(GL_POINTS)
        for p in particles:
            direction = p['target_pos'] - p['current_pos']
            if np.linalg.norm(direction) > 0.1:
                p['current_pos'] += direction * p['speed']
            glColor4fv(p['color'])
            glVertex3fv(p['current_pos'])
        glEnd()

        # Texto fixo central
        glWindowPos2d(display[0]//2 - text_surface.get_width()//2, 
                     display[1]//2 - text_surface.get_height()//2)
        glDrawPixels(text_surface.get_width(), text_surface.get_height(), 
                    GL_RGBA, GL_UNSIGNED_BYTE, text_data)

        pygame.display.flip()
        pygame.time.wait(16)

    pygame.quit()
    pass

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
        except:
            return ""

def check_ollama_connection():
    try:
        return requests.get("http://localhost:11434/api/tags", timeout=5).status_code == 200
    except:
        return False

def chat_with_ollama(prompt):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"Você é {ASSISTANT_NAME}, assistente pessoal. Responda em português. Usuário: {prompt}\n{ASSISTANT_NAME}:",
        "stream": False,
        "options": {"temperature": 0.7}
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT)
        if response.status_code == 200:
            return response.json().get("response", "Sem resposta.")
        return f"Erro no Ollama: {response.status_code}"
    except Exception as e:
        return f"Erro de conexão: {str(e)}"

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
