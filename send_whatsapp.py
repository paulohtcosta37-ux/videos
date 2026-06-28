import os
import urllib.request
import json
from twilio.rest import Client
import requests

def upload_video_to_tmpfiles(filepath):
    print("Fazendo upload temporário do vídeo para o tmpfiles.org...")
    try:
        url = "https://tmpfiles.org/api/v1/upload"
        with open(filepath, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            
        if response.status_code == 200:
            res_data = response.json()
            if res_data.get("status") == "success":
                upload_url = res_data["data"]["url"]
                # Converte para link de download direto
                direct_url = upload_url.replace("https://tmpfiles.org/", "https://tmpfiles.org/dl/")
                print(f"Upload concluído! Link público de download direto: {direct_url}")
                return direct_url
    except Exception as e:
        print(f"Erro ao subir arquivo no tmpfiles.org: {e}")
    return None

def send_to_whatsapp(video_url, caption):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    to_number = os.environ.get("TWILIO_TO_NUMBER", "+5531996293728")
    from_number = os.environ.get("TWILIO_FROM_NUMBER", "+14155238886") # Número padrão do Sandbox
    
    if not account_sid or not auth_token:
        print("Erro: TWILIO_ACCOUNT_SID ou TWILIO_AUTH_TOKEN não configuradas.")
        return False
        
    print(f"Enviando vídeo e legenda para o WhatsApp {to_number}...")
    try:
        client = Client(account_sid, auth_token)
        
        # 1. Envia a mensagem do vídeo
        message_video = client.messages.create(
            from_=f"whatsapp:{from_number}",
            media_url=[video_url],
            to=f"whatsapp:{to_number}"
        )
        print(f"Vídeo enviado! SID: {message_video.sid}")
        
        # 2. Envia a mensagem de texto da legenda do post
        message_caption = client.messages.create(
            from_=f"whatsapp:{from_number}",
            body=f"📋 *Legenda sugerida para o post:*\n\n{caption}",
            to=f"whatsapp:{to_number}"
        )
        print(f"Legenda enviada! SID: {message_caption.sid}")
        return True
    except Exception as e:
        print(f"Erro ao enviar pelo Twilio: {e}")
        return False

def main():
    video_path = "output/final_video.mp4"
    caption_path = "post_caption.txt"
    
    if not os.path.exists(video_path):
        print(f"Erro: Vídeo final em {video_path} não encontrado.")
        return
        
    caption = "Confira esta história fantástica!"
    if os.path.exists(caption_path):
        with open(caption_path, 'r', encoding='utf-8') as f:
            caption = f.read().strip()
            
    video_url = upload_video_to_tmpfiles(video_path)
    if video_url:
        send_to_whatsapp(video_url, caption)

if __name__ == "__main__":
    main()
