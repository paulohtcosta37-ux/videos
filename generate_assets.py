import os
import json
import urllib.request
import urllib.parse
import re
import shutil
import subprocess
import random
import wave
import time
import asyncio
import edge_tts
from google import genai
from google.genai import types
from gradio_client import Client
from PIL import Image

# Adiciona o diretório do FFmpeg instalado ao PATH do processo
FFMPEG_BIN_DIR = r"C:\Users\PAULO\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin"
if os.path.exists(FFMPEG_BIN_DIR):
    os.environ["PATH"] = FFMPEG_BIN_DIR + os.pathsep + os.environ["PATH"]

# Configurações de diretórios
PUBLIC_DIR = os.path.abspath("public")
if not os.path.exists(PUBLIC_DIR):
    os.makedirs(PUBLIC_DIR)

AVATAR_PATH = os.path.join(PUBLIC_DIR, "avatar.jpg")
BG_MUSIC_PATH = os.path.join(PUBLIC_DIR, "background_music.mp3")
SCENES_CONFIG = "scenes.json"
SCENES_DATA_OUTPUT = os.path.join(PUBLIC_DIR, "scenes_data.json")

# Configurações do Google GenAI com a chave do usuário
API_KEY = "AIzaSyBW-NbQD-_KXNOgEUg3xIUaExKWFUlxOz0"
google_client = genai.Client(api_key=API_KEY)

# Voz de fallback para o edge-tts (Masculina profissional)
EDGE_VOICE = "pt-BR-AntonioNeural"

def download_url_to_file(url, filepath):
    req = urllib.request.Request(
        url, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    )
    with urllib.request.urlopen(req) as response:
        with open(filepath, 'wb') as out_file:
            out_file.write(response.read())

def generate_default_avatar():
    if os.path.exists(AVATAR_PATH):
        return
    print("Avatar padrão não encontrado. Gerando um novo via Pollinations...")
    prompt = "A realistic photo of a young woman named Laura, 25 years old, looking directly at the camera, neutral sad expression, warm studio light, high quality portrait"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=512&height=512&nologo=true&seed={random.randint(1, 100000)}"
    try:
        download_url_to_file(url, AVATAR_PATH)
        print("Avatar de Laura gerado com sucesso!")
    except Exception as e:
        print("Erro ao gerar avatar de Laura:", e)

def generate_default_bg_music():
    if os.path.exists(BG_MUSIC_PATH):
        return
    print("Tentando baixar música de fundo instrumental padrão (SoundHelix)...")
    url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"
    try:
        download_url_to_file(url, BG_MUSIC_PATH)
        print("Música de fundo baixada com sucesso!")
    except Exception as e:
        print("Erro ao baixar música de fundo, gerando silêncio de backup:", e)
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo",
            "-t", "180",
            "-q:a", "9",
            "-acodec", "libmp3lame",
            BG_MUSIC_PATH
        ]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("Música de fundo silenciosa de backup criada!")
        except Exception as e2:
            print("Erro ao criar silêncio de backup:", e2)

def download_scene_image(prompt, index):
    filename = f"image_{index}.jpg"
    filepath = os.path.join(PUBLIC_DIR, filename)
    
    # Verifica se já existe uma imagem real providenciada pelo usuário no diretório public/
    # (ex: scene_1.jpg, scene_1.png, scene_1.jpeg)
    for ext in [".jpg", ".jpeg", ".png"]:
        user_file = os.path.join(PUBLIC_DIR, f"scene_{index}{ext}")
        if os.path.exists(user_file):
            print(f"Imagem real do caso encontrada em {user_file}! Copiando e convertendo...")
            try:
                img = Image.open(user_file)
                img.convert("RGB").save(filepath, "JPEG", quality=95)
                return filename
            except Exception as e:
                print(f"Erro ao processar imagem real {user_file}: {e}. Continuando com FLUX...")
                
    print(f"Gerando imagem fotorrealista para a Cena {index} via FLUX.1-schnell no Hugging Face...")
    
    # Prompt aprimorado para realismo extremo cinematográfico de suspense
    styled_prompt = (
        f"{prompt}, raw photo, cinematic lighting, dark moody style, dramatic shadows, highly detailed textures, shot on 35mm lens, depth of field, photorealistic, 8k resolution, vertical 9:16"
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Conexão com o Space público do FLUX.1-schnell
            client = Client("black-forest-labs/FLUX.1-schnell")
            result = client.predict(
                prompt=styled_prompt,
                seed=random.randint(1, 1000000),
                randomize_seed=True,
                width=768,
                height=1360,
                num_inference_steps=4,
                api_name="/infer"
            )
            if result and len(result) > 0:
                temp_img_path = result[0]
                img = Image.open(temp_img_path)
                # Converte e salva como JPG de alta qualidade
                img.save(filepath, "JPEG", quality=95)
                print(f"Imagem da Cena {index} salva com sucesso em {filepath}")
                return filename
        except Exception as e:
            print(f"Tentativa {attempt + 1} falhou para a cena {index}: {e}")
            if attempt < max_retries - 1:
                time.sleep(3)
    
    # Fallback caso a API do FLUX falhe
    print("Usando fallback de imagem via Pollinations.ai...")
    pollinations_prompt = f"{prompt}, raw cinematic photo, realistic, 8k resolution, vertical 9:16"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(pollinations_prompt)}?width=1080&height=1920&nologo=true&seed={random.randint(1, 100000)}"
    try:
        download_url_to_file(url, filepath)
        print(f"Imagem do fallback Pollinations salva em {filepath}")
        return filename
    except Exception as e:
        print(f"Falha definitiva ao baixar imagem da cena {index}: {e}")
        return None

def get_audio_duration(filepath):
    # Mede a duração de qualquer arquivo de áudio (wav, mp3, etc.) usando o ffprobe
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", filepath
        ]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return float(result.stdout.strip())
    except Exception as e:
        print(f"Erro ao medir duração com ffprobe para {filepath}: {e}")
        return 0.0

def generate_gemini_audio(text, index):
    audio_filename = f"audio_{index}.wav"
    audio_path = os.path.join(PUBLIC_DIR, audio_filename)
    temp_pcm_path = os.path.join(PUBLIC_DIR, f"temp_{index}.pcm")
    
    print(f"Gerando áudio via Gemini TTS para a Cena {index}...")
    
    try:
        response = google_client.models.generate_content(
            model="gemini-3.1-flash-tts-preview",
            contents=text,
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Puck"  # Voz masculina do Thiago Santos
                        )
                    )
                )
            )
        )
        
        audio_bytes = None
        if response.candidates and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    audio_bytes = part.inline_data.data
                    break
        
        if audio_bytes:
            # Salva temporariamente os bytes de PCM bruto
            with open(temp_pcm_path, 'wb') as f:
                f.write(audio_bytes)
            
            # Converte de PCM bruto (s16le, 24kHz, mono) para WAV real com cabeçalho RIFF via ffmpeg
            cmd_convert = [
                "ffmpeg", "-y",
                "-f", "s16le",
                "-ar", "24000",
                "-ac", "1",
                "-i", temp_pcm_path,
                audio_path
            ]
            subprocess.run(cmd_convert, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Remove o PCM temporário
            if os.path.exists(temp_pcm_path):
                os.remove(temp_pcm_path)
            
            duration = get_audio_duration(audio_path)
            print(f"Áudio da Cena {index} gerado com sucesso via Gemini ({round(duration, 2)}s).")
            return audio_filename, duration
    except Exception as e:
        print(f"Aviso: Falha ou cota excedida ao gerar áudio via Gemini na Cena {index}: {e}")
        if os.path.exists(temp_pcm_path):
            try:
                os.remove(temp_pcm_path)
            except:
                pass
        
    # Fallback automático e transparente para o Edge TTS
    print(f"Ativando fallback de áudio via Edge TTS (ilimitado) para a Cena {index}...")
    fallback_filename = f"audio_{index}.mp3"
    fallback_path = os.path.join(PUBLIC_DIR, fallback_filename)
    
    async def amain():
        communicate = edge_tts.Communicate(text, EDGE_VOICE)
        await communicate.save(fallback_path)
        
    try:
        asyncio.run(amain())
        duration = get_audio_duration(fallback_path)
        print(f"Áudio da Cena {index} gerado com sucesso via Edge TTS ({round(duration, 2)}s).")
        return fallback_filename, duration
    except Exception as e_fallback:
        print(f"Falha definitiva ao gerar áudio para a cena {index}: {e_fallback}")
        return None, None

def generate_subtitles_proportional(text, duration):
    words = text.split()
    if not words:
        return []
        
    total_chars = sum(len(w) for w in words)
    words_data = []
    current_time = 0.0
    
    for i, word in enumerate(words):
        word_len = len(word)
        word_duration = (word_len / total_chars) * duration
        
        # Garante duração mínima de legibilidade para cada palavra (150ms)
        word_duration = max(0.15, word_duration)
        end_time = current_time + word_duration
        
        # Na última palavra, arredondamos exatamente para o fim do áudio
        if i == len(words) - 1:
            end_time = duration
            
        clean_word = word.replace('"', '').replace("'", "")
        words_data.append({
            "text": clean_word,
            "start": round(current_time, 3),
            "end": round(end_time, 3)
        })
        current_time = end_time
        
    return words_data

def main():
    import sys
    if not os.path.exists(SCENES_CONFIG):
        print(f"Erro: Arquivo '{SCENES_CONFIG}' não encontrado. Por favor, forneça o roteiro primeiro.")
        return

    # Executa a busca automática de vídeos do Pexels
    if os.path.exists("fetch_stock_videos.py"):
        try:
            print("Executando busca e download de vídeos do Pexels...")
            subprocess.run([sys.executable, "fetch_stock_videos.py"], check=True)
        except Exception as e:
            print(f"Aviso: Falha ao rodar busca de vídeos do Pexels: {e}")

    generate_default_avatar()
    generate_default_bg_music()

    with open(SCENES_CONFIG, 'r', encoding='utf-8') as f:
        config = json.load(f)

    scenes_data = []

    for i, scene in enumerate(config, 1):
        print(f"\n=== Processando Cena {i} ===")
        scene_type = scene.get("type", "animation")
        narration = scene.get("narration", "")
        visual_prompt = scene.get("visual_prompt", "")
        
        # Gera áudio via Gemini/Edge com conversão PCM correta
        audio_file, duration = generate_gemini_audio(narration, i)
        if not audio_file:
            print(f"Falha ao gerar áudio para a cena {i}.")
            continue
            
        subtitles = generate_subtitles_proportional(narration, duration)
        
        # Verifica se existe um vídeo real do caso fornecido pelo usuário no diretório public/
        video_file = None
        for ext in [".mp4", ".webm", ".mov"]:
            user_video = os.path.join(PUBLIC_DIR, f"scene_{i}{ext}")
            if os.path.exists(user_video):
                video_file = f"scene_{i}{ext}"
                print(f"Trecho de vídeo real do caso encontrado em {user_video}! Usando para a cena {i}.")
                break
                
        scene_entry = {
            "scene_number": i,
            "type": scene_type,
            "audio_src": audio_file,
            "duration_in_seconds": duration,
            "duration_in_frames": int(duration * 30), # 30 fps
            "subtitles": subtitles
        }
        
        if video_file:
            scene_entry["video_src"] = video_file
        else:
            image_file = download_scene_image(visual_prompt, i)
            if not image_file:
                image_file = "avatar.jpg"
            scene_entry["image_src"] = image_file
            
        scenes_data.append(scene_entry)

    # 5. Garante duração mínima de 1 minuto (60 segundos)
    total_duration = sum(s["duration_in_seconds"] for s in scenes_data)
    print(f"\nDuração total original estimada: {round(total_duration, 2)} segundos.")
    
    if total_duration < 60.0:
        deficit = 60.0 - total_duration
        if deficit > 0 and len(scenes_data) > 0:
            extra_per_scene = deficit / len(scenes_data)
            print(f"Aviso: O vídeo está com {round(total_duration, 2)}s (menos do que o mínimo de 60s).")
            print(f"Estendendo proporcionalmente as cenas em +{round(extra_per_scene, 2)}s cada para atingir 60s...")
            for s in scenes_data:
                s["duration_in_seconds"] += extra_per_scene
                s["duration_in_frames"] = int(s["duration_in_seconds"] * 30)
                # Estende a exibição da última palavra da legenda para cobrir o fim da cena
                if s.get("subtitles") and len(s["subtitles"]) > 0:
                    s["subtitles"][-1]["end"] = round(s["duration_in_seconds"], 3)
            total_duration = sum(s["duration_in_seconds"] for s in scenes_data)
            print(f"Nova duração total ajustada: {round(total_duration, 2)}s")

    # Escreve o arquivo final de dados do vídeo
    final_data = {"scenes": scenes_data}
    with open(SCENES_DATA_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
        
    print(f"\nGeração de ativos concluída! Dados salvos em {SCENES_DATA_OUTPUT}")

if __name__ == "__main__":
    main()
