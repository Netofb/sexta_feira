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

def show_jarvis_loading(duration=3):
    """Animação de loading futurista estilo J.A.R.V.I.S."""
    width, height = 800, 400
    screen = pygame.display.set_mode((width, height), pygame.NOFRAME)
    pygame.display.set_caption(f"{ASSISTANT_NAME} - Inicialização")
    
    bg_color = (2, 4, 15)
    primary_color = (0, 200, 255)
    secondary_color = (0, 120, 200)
    pulse_color = (0, 255, 255)
    text_color = (150, 230, 255)
    
    try:
        font_large = pygame.font.Font(None, 52)
        font_medium = pygame.font.Font(None, 28)
    except:
        font_large = pygame.font.SysFont('consolas', 52)
        font_medium = pygame.font.SysFont('consolas', 28)
    
    try:
        pygame.mixer.music.load("startup_sound.mp3")
        pygame.mixer.music.play()
    except:
        pass

    start_time = time.time()
    center_x, center_y = width // 2, height // 2
    radius = 110

    particles = []  # Lista de partículas
    running = True

    while running:
        current_time = time.time() - start_time
        progress = min(1.0, current_time / duration)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        screen.fill(bg_color)

        # === Fundo com linhas circulares ===
        for i in range(0, 360, 15):
            angle = math.radians(i)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            pygame.draw.line(screen, (0, 80, 120), (center_x, center_y), (x, y), 1)

        # === Anel de progresso com camada dupla ===
        progress_angle = -math.pi/2 + 2 * math.pi * progress
        pygame.draw.circle(screen, (0, 80, 100), (center_x, center_y), radius + 15, 1)
        pygame.draw.arc(screen, primary_color,
                        (center_x - radius, center_y - radius, radius * 2, radius * 2),
                        -math.pi/2, progress_angle, 6)

        pygame.draw.arc(screen, secondary_color,
                        (center_x - radius - 10, center_y - radius - 10, (radius + 10) * 2, (radius + 10) * 2),
                        -math.pi/2, progress_angle, 2)

        # === Partículas circulando ===
        if progress < 1:
            for _ in range(2):
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0.5, 1.5)
                particles.append({
                    'angle': angle,
                    'radius': radius,
                    'speed': speed,
                    'size': random.randint(2, 4)
                })

        new_particles = []
        for p in particles:
            p['angle'] += p['speed'] * 0.01
            x = center_x + p['radius'] * math.cos(p['angle'])
            y = center_y + p['radius'] * math.sin(p['angle'])
            pygame.draw.circle(screen, pulse_color, (int(x), int(y)), p['size'])
            if 0 < x < width and 0 < y < height:
                new_particles.append(p)
        particles = new_particles

        # === Núcleo pulsante ===
        pulse = int(10 + 5 * math.sin(current_time * 5))
        pygame.draw.circle(screen, pulse_color, (center_x, center_y), pulse)

        # === Nome do assistente ===
        text = font_large.render(ASSISTANT_NAME.upper(), True, primary_color)
        screen.blit(text, (center_x - text.get_width() // 2, center_y - 140))

        # === Status ===
        status = font_medium.render(f"Inicializando... {int(progress * 100)}%", True, text_color)
        screen.blit(status, (center_x - status.get_width() // 2, center_y + radius + 40))

        pygame.display.flip()

        if progress >= 1.0:
            time.sleep(0.5)
            running = False

        time.sleep(0.016)  # 60 FPS
    
    pygame.quit()



def set_voice():
    """Configura a voz da Maria"""
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
    """Faz a Sexta-Feira falar"""
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
    """Ouve os comandos de voz"""
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
            speak("Não consegui entender chefe. Repita por favor", 'high')
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
    """Consulta o Ollama"""
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
    """Executa comandos"""
    if not command:
        return
        
    command = command.strip()
    print(f"Processando: {command}")
    
    # COMANDOS DE SISTEMA
    if any(palavra in command for palavra in ["finalizar"]):
        speak("Encerrando sistemas. Até logo chefe!", 'high')
        sys.exit(0)

    elif "desligar computador" in command:
        speak("Iniciando desligamento em 30 segundos", 'high')
        os.system("shutdown /s /t 30")
        return
        
    elif "reiniciar computador" in command:
        speak("Preparando reinicialização em 30 segundos", 'high')
        os.system("shutdown /r /t 30")
        return
        
    elif "cancelar desligamento" in command:
        os.system("shutdown /a")
        speak("Sequência de desligamento cancelada", 'high')
        return
        
    # CONTROLE DE APLICATIVOS

    elif "qual a boa de hoje" in command:
        webbrowser.open("https://www.youtube.com/watch?v=f2D2hEFnHLU")
        speak("Olá chefe parabéns pelo seu trabalho, como vai seu dia?")
        return
    
    elif "encerrar" in command:
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
        
    # INFORMAÇÕES
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
        
    # RESPOSTAS PERSONALIZADAS
    elif any(palavra in command for palavra in ["quem é você", "seu nome", "qual seu nome"]):
        speak(f"Sou {ASSISTANT_NAME} à assistente pessoal do Chefe Fábio, Pronta para ajudar!")
        return
        
    elif "obrigado" in command or "valeu" in command:
        respostas = ["Sempre às ordens!", "De nada chefe!", "Disponha quando precisar!"]
        speak(random.choice(respostas))
        return
        
    # CONSULTA AO OLLAMA
    resposta = chat_with_ollama(command)
    
    if resposta:
        speak(resposta)
    else:
        speak("Falha na análise. Reformule o comando.", 'high')

def set_volume(level):
    """Controla o volume do sistema"""
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
    """Função principal"""
    # Mostra tela de loading
    show_jarvis_loading()
    
    # Configurações iniciais
    set_voice()
    
    if not check_ollama_connection():
        speak("Atenção: Conexão com Ollama não disponível. Funcionalidades limitadas.", 'high')
    
    # Saudação
    hora = datetime.datetime.now().hour
    if 6 <= hora < 12:
        speak("Bom dia, chefe. Sistemas operacionais normais.")
    elif 12 <= hora < 18:
        speak("Boa tarde, chefe. Todos os sistemas online.")
    else:
        speak("Boa noite, chefe. Pronta para auxiliar.")
    
    # Loop principal
    while True:
        try:
            comando = listen()
            if comando:
                execute_command(comando)
        except KeyboardInterrupt:
            speak("Desligamento de emergência ativado.", 'high')
            sys.exit(1)
        except Exception as e:
            print(f"Erro: {str(e)}")
            time.sleep(1)

if __name__ == "__main__":
    main()


    