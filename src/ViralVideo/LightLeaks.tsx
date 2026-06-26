import React from "react";
import { useCurrentFrame, interpolate } from "remotion";

export const LightLeaks: React.FC = () => {
  const frame = useCurrentFrame();

  // Movimento cíclico lento para o vazamento de luz 1 (âmbar/laranja no canto superior esquerdo)
  const x1 = interpolate(Math.sin(frame * 0.015), [-1, 1], [-15, 25]);
  const y1 = interpolate(Math.cos(frame * 0.018), [-1, 1], [-25, 15]);
  const size1 = interpolate(Math.sin(frame * 0.01), [-1, 1], [40, 60]);

  // Movimento cíclico lento para o vazamento de luz 2 (rosa/azul no canto inferior direito)
  const x2 = interpolate(Math.cos(frame * 0.02), [-1, 1], [75, 105]);
  const y2 = interpolate(Math.sin(frame * 0.013), [-1, 1], [65, 95]);
  const size2 = interpolate(Math.cos(frame * 0.011), [-1, 1], [35, 50]);

  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        width: "100%",
        height: "100%",
        pointerEvents: "none",
        zIndex: 9,
        mixBlendMode: "screen",
        opacity: 0.38, // Regula a intensidade geral do vazamento de luz
        background: `
          radial-gradient(circle ${size1}% at ${x1}% ${y1}%, rgba(255, 136, 0, 0.4) 0%, rgba(255, 136, 0, 0) 70%),
          radial-gradient(circle ${size2}% at ${x2}% ${y2}%, rgba(0, 183, 255, 0.25) 0%, rgba(0, 183, 255, 0) 75%)
        `,
      }}
    />
  );
};
