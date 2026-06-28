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
    
    # 2. Força a verificação e o processamento do canal do Jeffin (@jeffin.reddit)
    print("Processando canal target do Jeffin (@jeffin.reddit) conforme solicitado pelo usuário...")
    new_video_url, video_id, title = monitor.check_tiktok_channel("jeffin.reddit")
    target_channel = "jeffin.reddit"
    
    if not new_video_url:
        print("Erro: Não foi possível obter o último vídeo do Jeffin. Abortando pipeline.")
        return
        
    history["jeffin.reddit"] = video_id
        
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
    monitor.save_history(history)
    print("Pipeline de ativos concluído com sucesso!")

if __name__ == "__main__":
    main()
