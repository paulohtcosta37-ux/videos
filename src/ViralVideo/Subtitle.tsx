import React from "react";
import { useCurrentFrame, useVideoConfig, spring, interpolate } from "remotion";
import { SubtitleWord } from "../types";

interface SubtitleProps {
  words: SubtitleWord[];
}

export const Subtitle: React.FC<SubtitleProps> = ({ words }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentTime = frame / fps;

  // Agrupa as palavras em blocos de até 4 palavras
  const chunks = React.useMemo(() => {
    const list = [];
    const chunkSize = 4;
    for (let i = 0; i < words.length; i += chunkSize) {
      const chunk = words.slice(i, i + chunkSize);
      if (chunk.length > 0) {
        const start = chunk[0].start;
        const end = chunk[chunk.length - 1].end;
        list.push({
          words: chunk,
          start,
          end
        });
      }
    }
    return list;
  }, [words]);

  // Encontra o bloco de palavras ativo baseado no tempo atual do frame
  const activeChunk = chunks.find(
    (c) => currentTime >= c.start && currentTime <= c.end
  );

  // Se não encontrar bloco ativo, mas o vídeo já passou do último bloco, exibe o último
  const chunkToDisplay = activeChunk || (chunks.length > 0 && currentTime > chunks[chunks.length - 1].end ? chunks[chunks.length - 1] : null);

  if (!chunkToDisplay) {
    return null;
  }

  return (
    <div
      style={{
        position: "absolute",
        bottom: 380, // Centralizado um pouco mais acima para limpar a interface do TikTok/Reels
        width: "100%",
        display: "flex",
        flexWrap: "wrap",
        justifyContent: "center",
        padding: "0 40px",
        pointerEvents: "none",
        zIndex: 100,
        boxSizing: "border-box",
      }}
    >
      {chunkToDisplay.words.map((word, index) => {
        const isActive = currentTime >= word.start && currentTime <= word.end;
        const isSpoken = currentTime > word.end;

        let color = "rgba(255, 255, 255, 0.4)";
        if (isSpoken) color = "#FFFFFF";
        if (isActive) color = "#FFE600";

        let scale = 1.0;
        let rotate = 0;
        
        if (isActive) {
          const wordActiveFrame = Math.max(0, (currentTime - word.start) * fps);

          const spr = spring({
            frame: wordActiveFrame,
            fps,
            config: {
              damping: 8,     // Balanço físico de mola leve
              mass: 0.35,     // Fluidez rápida
              stiffness: 180, // Impacto instantâneo
            },
          });

          scale = interpolate(spr, [0, 1], [1.0, 1.25]);
          rotate = interpolate(spr, [0, 1], [0, -3.0]);
        }

        return (
          <span
            key={index}
            style={{
              fontFamily: "'Impact', 'Arial Black', sans-serif",
              fontSize: 70, // Aumentado para 70px para melhor leitura
              fontWeight: 900,
              color: color,
              textTransform: "uppercase",
              margin: "6px 12px",
              display: "inline-block",
              transform: `scale(${scale}) rotate(${rotate}deg)`,
              transformOrigin: "center center",
              transition: "color 0.08s ease",
              textShadow: `
                -3px -3px 0 #000,  
                 3px -3px 0 #000,
                -3px  3px 0 #000,
                 3px  3px 0 #000,
                 0px  6px 12px rgba(0, 0, 0, 0.9)
              `,
            }}
          >
            {word.text}
          </span>
        );
      })}
    </div>
  );
};
