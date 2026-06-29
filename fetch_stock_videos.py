import os
import json
import urllib.request
import urllib.parse
import sys

# Diretórios e caminhos
PUBLIC_DIR = os.path.abspath("public")
SCENES_CONFIG = "scenes.json"

def get_pexels_api_key():
    # Tenta carregar do arquivo .env local
    env_path = ".env"
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("PEXELS_API_KEY="):
                    return line.strip().split("=", 1)[1].replace('"', '').replace("'", "")
    # Tenta pegar das variáveis de ambiente globais do sistema
    return os.environ.get("PEXELS_API_KEY", "")

def download_video_clip(query, scene_index, api_key):
    print(f"Buscando clipe de vídeo para clipe '{query}' (Cena {scene_index})...")
    encoded_query = urllib.parse.quote(query)
    # Busca apenas vídeos verticais (portrait)
    url = f"https://api.pexels.com/v1/videos/search?query={encoded_query}&per_page=5&orientation=portrait"
    
    req = urllib.request.Request(url)
    req.add_header("Authorization", api_key)
    req.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            videos = data.get("videos", [])
            if not videos:
                print(f"Nenhum vídeo encontrado no Pexels para a busca: '{query}'")
                return False
            
            # Filtra os arquivos de vídeo para achar um arquivo MP4 adequado
            for video in videos:
                video_files = video.get("video_files", [])
                for f in video_files:
                    # Preferência por qualidade HD (1080p) ou SD vertical, formato mp4
                    if f.get("file_type") == "video/mp4" and f.get("link"):
                        link = f.get("link")
                        width = f.get("width", 0)
                        height = f.get("height", 0)
                        
                        # Verifica se é de fato vertical (altura > largura)
                        if height > width:
                            dest_path = os.path.join(PUBLIC_DIR, f"scene_{scene_index}.mp4")
                            print(f"Vídeo vertical encontrado! Dimensões: {width}x{height}. Baixando clipe...")
                            
                            # Faz o download do arquivo de vídeo
                            download_req = urllib.request.Request(
                                link, 
                                headers={"User-Agent": "Mozilla/5.0"}
                            )
                            with urllib.request.urlopen(download_req) as video_response:
                                with open(dest_path, "wb") as out_file:
                                    out_file.write(video_response.read())
                            print(f"Vídeo da Cena {scene_index} Salvo com sucesso em public/scene_{scene_index}.mp4")
                            return True
            print(f"Nenhum vídeo com formato vertical (9:16) adequado foi encontrado para a Cena {scene_index}.")
            return False
            
    except Exception as e:
        print(f"Erro ao buscar vídeo no Pexels para a Cena {scene_index}: {e}")
        return False

def main():
    api_key = get_pexels_api_key()
    if not api_key:
        print("AVISO: PEXELS_API_KEY não encontrada no arquivo .env ou variáveis de ambiente.")
        print("Pulei a busca no Pexels. O pipeline usará imagens IA de fallback.")
        return
        
    if not os.path.exists(SCENES_CONFIG):
        print(f"Erro: Roteiro {SCENES_CONFIG} não encontrado.")
        return
        
    with open(SCENES_CONFIG, "r", encoding="utf-8") as f:
        scenes = json.load(f)
        
    print("\n--- Buscando clipes de vídeo no Pexels ---")
    for i, scene in enumerate(scenes, 1):
        # Para o teste, se pexels_query estiver definido ou se forçarmos o tipo video
        visual_type = scene.get("visual_type", "image")
        query = scene.get("pexels_query", "")
        
        # Se não houver query específica, tenta extrair os primeiros termos do prompt visual
        if not query and scene.get("visual_prompt"):
            prompt = scene.get("visual_prompt")
            # Remove estilos comuns de IA para limpar o termo
            clean_prompt = prompt.replace("Cinematic raw photo, 8k, dark moody lighting, vertical 9:16, ", "")
            # Pega as primeiras 3 palavras significativas
            query = " ".join(clean_prompt.split()[:3]).replace(",", "").replace(".", "")
            
        # Forçamos busca se o tipo for video ou se tiver pexels_query
        if visual_type == "video" or query:
            success = download_video_clip(query, i, api_key)
            if not success:
                print(f"Aviso: Não foi possível obter vídeo para a cena {i}. Fallback para imagem ativado.")

if __name__ == "__main__":
    main()
