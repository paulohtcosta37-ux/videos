import React, { useRef, useEffect, useMemo } from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export const DustParticles: React.FC = () => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // Gera parâmetros estáveis para as partículas usando um gerador pseudo-aleatório semeado (LCG)
  // Isso garante que a renderização seja idêntica em todas as threads/máquinas
  const particles = useMemo(() => {
    const numParticles = 40;
    const list = [];
    let seed = 98765; // Semente estável para consistência em múltiplos renders

    const random = () => {
      seed = (seed * 1664525 + 1013904223) % 4294967296;
      return seed / 4294967296;
    };

    for (let i = 0; i < numParticles; i++) {
      list.push({
        xStart: random() * width,
        yStart: random() * height,
        size: random() * 2.5 + 1.2, // Tamanhos de 1.2px a 3.7px
        speedX: (random() - 0.5) * 0.4,
        speedY: -(random() * 0.7 + 0.3), // Movimento ascendente constante
        swayAmplitude: random() * 12 + 4,
        swaySpeed: random() * 0.04 + 0.015,
        opacity: random() * 0.4 + 0.15,
      });
    }
    return list;
  }, [width, height]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Limpa o canvas a cada frame antes do redesenho
    ctx.clearRect(0, 0, width, height);

    particles.forEach((p) => {
      // Posição base linear dependente do frame
      let x = p.xStart + p.speedX * frame;
      let y = p.yStart + p.speedY * frame;

      // Mantém as partículas em loop infinito dentro da tela
      y = ((y % height) + height) % height;
      x = ((x % width) + width) % width;

      // Adiciona o movimento senoidal horizontal (balanço suave)
      x += Math.sin(frame * p.swaySpeed) * p.swayAmplitude;
      x = ((x % width) + width) % width;

      // Desenha a partícula com um leve glow radial
      ctx.beginPath();
      ctx.arc(x, y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(255, 255, 240, ${p.opacity})`; // Um tom levemente âmbar/quente
      ctx.shadowBlur = p.size * 2.5;
      ctx.shadowColor = "rgba(255, 255, 240, 0.4)";
      ctx.fill();
    });
  }, [frame, particles, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 10,
        mixBlendMode: "screen",
      }}
    />
  );
};
