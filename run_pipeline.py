import os
import json
import monitor
import analyze_and_script
import generate_assets

def main():
    # 1. Carrega histórico de monitoramento
    history = monitor.load_history()
    
    import sys
    import subprocess
    import send_whatsapp
    
    new_video_url = None
    target_channel = None
    
    # Verifica se uma URL foi passada por argumento
    manual_url = None
    for arg in sys.argv:
        if arg.startswith("http://") or arg.startswith("https://"):
            manual_url = arg
            break
            
    if manual_url:
        new_video_url = manual_url
        print(f"Usando URL fornecida manualmente: {new_video_url}")
    else:
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
            if video_id:
                history["canaldoedu_"] = video_id
            
    if not new_video_url:
        print("Nenhuma URL de vídeo foi obtida. Abortando pipeline.")
        return

    # 2.5 Verifica se o link já foi processado anteriormente
    if monitor.is_link_processed(new_video_url):
        print(f"\n[AVISO DE DUPLICIDADE] O vídeo '{new_video_url}' já foi gerado anteriormente!")
        print("Abortando execução para evitar vídeos repetidos.")
        return

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
        print("Erro na análise do vídeo pela IA.")
        if os.path.exists("scenes.json"):
            print("Aviso: Utilizando o roteiro do arquivo 'scenes.json' existente como fallback!")
            if not os.path.exists("post_caption.txt"):
                with open("post_caption.txt", 'w', encoding='utf-8') as f:
                    f.write("Confira esta história fantástica! #curiosidades #historia")
        else:
            print("Abortando pipeline.")
            return
        
    # 5. Roda o script de geração de ativos (FLUX + Gemini TTS)
    print("Iniciando geração dos ativos de voz e imagem do novo vídeo...")
    generate_assets.main()
    
    # Salva o novo histórico após o pipeline rodar com sucesso
    if target_channel:
        monitor.save_history(history)
        
    print("Pipeline de ativos concluído com sucesso!")
    
    # 6. Renderiza o vídeo usando Remotion
    print("Iniciando a renderização do vídeo com o Remotion...")
    output_dir = "output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    video_output_path = os.path.join(output_dir, "final_video.mp4")
    try:
        # Roda o npx.cmd remotion render
        render_cmd = "npx.cmd remotion render ViralVideo output/final_video.mp4 --gl=angle"
        subprocess.run(render_cmd, shell=True, check=True)
        print("Vídeo renderizado com sucesso em output/final_video.mp4!")
    except Exception as render_err:
        print(f"Erro na renderização do Remotion: {render_err}")
        return
        
    # 7. Faz o upload do vídeo final e gera informações
    print("Iniciando upload do vídeo final...")
    try:
        download_url = send_whatsapp.upload_video_failsafe(video_output_path)
        print(f"Vídeo enviado! Link para download: {download_url}")
        
        caption = "Confira esta história chocante!"
        if os.path.exists("post_caption.txt"):
            with open("post_caption.txt", 'r', encoding='utf-8') as f:
                caption = f.read().strip()
                
        output_info = {
            "download_url": download_url,
            "caption": caption
        }
        with open("output_info.json", 'w', encoding='utf-8') as f:
            json.dump(output_info, f, indent=2, ensure_ascii=False)
            
        print("Informações salvas com sucesso em output_info.json!")
    except Exception as upload_err:
        print(f"Erro no upload do vídeo final: {upload_err}")
        
    # 7.5 Salva o link processado no banco de dados geral
    if new_video_url:
        monitor.add_processed_link(new_video_url)

if __name__ == "__main__":
    main()
