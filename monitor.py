import os
import json
import subprocess

HISTORY_FILE = "history.json"
TIKTOK_CHANNELS = [
    "canaldoedu_",
    "historiasreaisofc2",
    "jeffin.reddit",
    "quattronews",
    "httsthaa",
    "mariahheeusi"
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def check_tiktok_channel(username):
    print(f"Buscando o post mais recente do canal: @{username}...")
    try:
        # Pede apenas os metadados do último vídeo do canal usando o yt-dlp
        cmd = [
            "py", "-m", "yt_dlp", 
            "--playlist-end", "1", 
            "--dump-json", 
            f"https://www.tiktok.com/@{username}"
        ]
        # Se estiver rodando no Linux (GitHub Actions), roda 'python -m yt_dlp'
        if os.name != 'nt':
            cmd[0] = "python"
            
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        if result.stdout:
            data = json.loads(result.stdout.strip())
            return data.get("webpage_url"), data.get("id"), data.get("title")
    except Exception as e:
        print(f"Erro ao verificar canal @{username}: {e}")
    return None, None, None

def download_video(video_url, output_path):
    print(f"Baixando vídeo do link: {video_url}...")
    cmd = [
        "py", "-m", "yt_dlp",
        "--format", "mp4",
        "-o", output_path,
        video_url
    ]
    if os.name != 'nt':
        cmd[0] = "python"
    try:
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Erro ao baixar vídeo: {e}")
        return False
