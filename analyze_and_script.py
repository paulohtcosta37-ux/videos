import os
import time
import json
from google import genai
from google.genai import types

def analyze_video_with_gemini(video_path):
    API_KEY = os.environ.get("GEMINI_API_KEY")
    if not API_KEY:
        # Tenta carregar de fallback local se houver para testes
        API_KEY = "AIzaSyBW-NbQD-_KXNOgEUg3xIUaExKWFUlxOz0"

    client = genai.Client(api_key=API_KEY)
    
    print("Fazendo upload do vídeo do TikTok para a API do Gemini...")
    uploaded_file = client.files.upload(file=video_path)
    print(f"Upload concluído! ID: {uploaded_file.name}")
    
    # Aguarda o vídeo terminar de ser processado no servidor do Google
    print("Aguardando processamento do vídeo no servidor do Google...")
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(5)
        uploaded_file = client.files.get(name=uploaded_file.name)
    
    if uploaded_file.state.name == "FAILED":
        print("Erro: Processamento do vídeo falhou no Gemini.")
        return False

    print("Vídeo processado! Iniciando análise e roteirização...")
    
    prompt = (
        "Analise de forma completa o vídeo do TikTok fornecido. Faça as seguintes tarefas:\n"
        "1. Transcreva toda a fala do vídeo original (em português).\n"
        "2. Crie um roteiro totalmente novo e otimizado com base nessa história, reescrevendo a narração para ser original e com tom viral.\n"
        "3. Divida o roteiro em cenas sequenciais curtas (formato scenes.json), definindo o type de cada cena (presenter para cenas faladas da Laura, ou animation para imagens de apoio fotorrealistas) e criando prompts visuais fotorrealistas ultra-detalhados no visual_prompt.\n"
        "4. Crie uma legenda de postagem atrativa e chamativa com hashtags virais (ex: #curiosidades #historia) baseadas na história.\n\n"
        "Você deve retornar a resposta formatada estritamente em JSON no seguinte formato:\n"
        "{\n"
        "  \"caption\": \"Texto da legenda com hashtags aqui\",\n"
        "  \"scenes\": [\n"
        "    {\n"
        "      \"scene_number\": 1,\n"
        "      \"type\": \"animation\",\n"
        "      \"narration\": \"Narração reescrita da cena aqui\",\n"
        "      \"visual_prompt\": \"Cinematic photo, vertical 9:16, prompt detalhado do visual aqui\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    max_retries = 5
    response = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            break
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Erro definitivo na chamada da API do Gemini após {max_retries} tentativas: {e}")
                try:
                    client.files.delete(name=uploaded_file.name)
                except:
                    pass
                return False
            sleep_time = (2 ** attempt) * 5 + 3
            print(f"Aviso: Falha na API do Gemini (tentativa {attempt + 1}/{max_retries}): {e}. Tentando novamente em {sleep_time}s...")
            time.sleep(sleep_time)
    
    # Limpa o arquivo da nuvem após a análise
    try:
        client.files.delete(name=uploaded_file.name)
    except Exception as e:
        print(f"Aviso ao deletar arquivo temporário da nuvem: {e}")

    if response.text:
        try:
            result = json.loads(response.text.strip())
            
            # Salva o arquivo de cenas para o generate_assets.py
            with open("scenes.json", 'w', encoding='utf-8') as f:
                json.dump(result["scenes"], f, indent=2, ensure_ascii=False)
            
            # Salva a legenda do post
            with open("post_caption.txt", 'w', encoding='utf-8') as f:
                f.write(result["caption"])
                
            print("Análise e roteirização geradas com sucesso!")
            return True
        except Exception as json_err:
            print(f"Erro ao analisar o JSON retornado pela IA: {json_err}")
            print(response.text)
            return False
    return False
