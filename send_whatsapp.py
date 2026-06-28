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

def send_to_email(video_url, caption):
    api_key = os.environ.get("RESEND_API_KEY")
    to_email = os.environ.get("EMAIL_TO_ADDRESS")
    
    if not api_key or not to_email:
        print("Aviso: RESEND_API_KEY ou EMAIL_TO_ADDRESS não configuradas. Envio de e-mail pulado.")
        return False
        
    print(f"Enviando e-mail com o vídeo e legenda para {to_email}...")
    
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    html_caption = caption.replace("\n", "<br>")
    
    body = {
        "from": "Videos IA <onboarding@resend.dev>",
        "to": to_email,
        "subject": "🎬 Novo Vídeo Automatizado Pronto para Postar!",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #4F46E5; text-align: center;">Seu vídeo está pronto! 🚀</h2>
            <p>Olá Paulo,</p>
            <p>O pipeline automático concluiu a geração de um novo vídeo vertical (9:16) na nuvem.</p>
            
            <div style="background-color: #F3F4F6; padding: 15px; border-radius: 6px; margin: 20px 0;">
                <h4 style="margin-top: 0; color: #1F2937;">📋 Legenda Sugerida para Postagem:</h4>
                <p style="font-style: italic; color: #4B5563;">{html_caption}</p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{video_url}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    📥 Baixar Vídeo MP4
                </a>
                <p style="font-size: 11px; color: #9CA3AF; margin-top: 8px;">(O link expira temporariamente)</p>
            </div>
            
            <hr style="border: 0; border-top: 1px solid #e0e0e0; margin: 20px 0;">
            <p style="font-size: 12px; color: #6B7280; text-align: center;">Enviado automaticamente pelo GitHub Actions.</p>
        </div>
        """
    }
    
    try:
        response = requests.post(url, headers=headers, json=body)
        if response.status_code in [200, 201]:
            print("E-mail enviado com sucesso via Resend!")
            return True
        else:
            print(f"Erro ao enviar e-mail: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
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
        send_to_email(video_url, caption)

if __name__ == "__main__":
    main()
