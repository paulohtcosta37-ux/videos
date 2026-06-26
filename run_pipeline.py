import os
import json
import monitor
import analyze_and_script
import generate_assets

def main():
    # 1. Carrega histórico de monitoramento
    history = monitor.load_history()
    
    new_video_url = None
    target_channel = None
    
    # 2. Varre os perfis (começando pelo canal do edu para este teste)
    # Colocamos o canal do edu no topo para priorizar
    channels = ["canaldoedu_"] + [c for c in monitor.TIKTOK_CHANNELS if c != "canaldoedu_"]
    
    for channel in channels:
        video_url, video_id, title = monitor.check_tiktok_channel(channel)
        if video_url and video_id:
            last_processed = history.get(channel)
            if last_processed != video_id:
                print(f"NOVO VÍDEO DETECTADO no canal @{channel}: '{title}' ({video_id})")
                new_video_url = video_url
                target_channel = channel
                # Atualiza o ID do vídeo no histórico
                history[channel] = video_id
                break
                
    if not new_video_url:
        print("Nenhum vídeo novo detectado nos perfis monitorados.")
        # Como é o primeiro teste, se não detectar diferença, força o download do último vídeo do canal do Edu de qualquer forma
        print("Forçando download do vídeo do Canal do Edu para teste de inicialização...")
        new_video_url, video_id, title = monitor.check_tiktok_channel("canaldoedu_")
        target_channel = "canaldoedu_"
        history["canaldoedu_"] = video_id
        
    # 3. Baixa o vídeo do TikTok
    temp_video_path = "temp_video.mp4"
    download_success = monitor.download_video(new_video_url, temp_video_path)
    if not download_success:
        print("Erro ao baixar o vídeo do TikTok. Abortando pipeline.")
        return
        
    # 4. Envia o vídeo para o Gemini "assistir" e criar o roteiro + legenda
    analyze_success = analyze_and_script.analyze_video_with_gemini(temp_video_path)
    
    # Remove o vídeo temporário original
    if os.path.exists(temp_video_path):
        os.remove(temp_video_path)
        
    if not analyze_success:
        print("Erro na análise do vídeo pela IA. Abortando pipeline.")
        return
        
    # 5. Roda o script de geração de ativos (FLUX + Gemini TTS)
    print("Iniciando geração dos ativos de voz e imagem do novo vídeo...")
    generate_assets.main()
    
    # Salva o novo histórico após o pipeline rodar com sucesso
    monitor.save_history(history)
    print("Pipeline de ativos concluído com sucesso!")

if __name__ == "__main__":
    main()
