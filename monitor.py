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

def get_video_id(url):
    import re
    # Procura por um padrão de dígitos após '/video/' na URL
    match = re.search(r'/video/(\d+)', url)
    if match:
        return match.group(1)
    # Suporte para URLs do formato alternativo do yt-dlp ou curtas, se aplicável
    return None

def is_link_processed(url):
    db_file = "processed_links.json"
    if not os.path.exists(db_file):
        return False
        
    video_id = get_video_id(url)
    if not video_id:
        return False
        
    try:
        with open(db_file, 'r', encoding='utf-8') as f:
            db = json.load(f)
            processed_list = db.get("processed", [])
            for item in processed_list:
                if item.get("video_id") == video_id or item.get("url") == url:
                    return True
    except Exception as e:
        print(f"Erro ao ler banco de dados de links: {e}")
    return False

def add_processed_link(url):
    db_file = "processed_links.json"
    video_id = get_video_id(url)
    if not video_id:
        return
        
    import datetime
    new_entry = {
        "url": url,
        "video_id": video_id,
        "processed_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    
    db = {"processed": []}
    if os.path.exists(db_file):
        try:
            with open(db_file, 'r', encoding='utf-8') as f:
                db = json.load(f)
        except Exception:
            pass
            
    if "processed" not in db:
        db["processed"] = []
        
    # Evita duplicar no próprio arquivo
    if not any(item.get("video_id") == video_id for item in db["processed"]):
        db["processed"].append(new_entry)
        try:
            with open(db_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2, ensure_ascii=False)
            print(f"URL de vídeo registrada no banco de dados: {url}")
        except Exception as e:
            print(f"Erro ao salvar banco de dados de links: {e}")

