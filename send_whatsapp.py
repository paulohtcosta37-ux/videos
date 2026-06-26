import os
import urllib.request
import json
from twilio.rest import Client

def upload_video_to_file_io(filepath):
    print("Fazendo upload temporário do vídeo para o file.io...")
    try:
        url = "https://file.io"
        # Prepara a requisição multipart para upload
        with open(filepath, 'rb') as f:
            file_data = f.read()
            
        boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
        data = []
        data.append(f"--{boundary}".encode('utf-8'))
        data.append(b'\r\nContent-Disposition: form-data; name="file"; filename="final_video.mp4"')
        data.append(b'\r\nContent-Type: video/mp4\r\n\r\n')
        data.append(file_data)
        data.append(f"\r\n--{boundary}--".encode('utf-8'))
        
        body = b''.join(data)
        headers = {
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'Content-Length': str(len(body))
        }
        
        req = urllib.request.Request(url, data=body, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            if res_data.get("success"):
                video_url = res_data.get("link")
                print(f"Upload concluído! Link público temporário: {video_url}")
                return video_url
    except Exception as e:
        print(f"Erro ao subir arquivo no file.io: {e}")
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
            
    video_url = upload_video_to_file_io(video_path)
    if video_url:
        send_to_whatsapp(video_url, caption)

if __name__ == "__main__":
    main()
