import React from "react";
import { AbsoluteFill, useCurrentFrame, interpolate, useVideoConfig } from "remotion";

// 1. FADE SUAVE (Crossfade)
export const CrossfadeTransition: React.FC<{
  durationInFrames: number;
  children: React.ReactNode;
}> = ({ durationInFrames, children }) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(
    frame,
    [0, durationInFrames],
    [0, 1],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  return (
    <AbsoluteFill style={{ opacity }}>
      {children}
    </AbsoluteFill>
  );
};

// 2. SLIDE LATERAL (Slide)
export const SlideTransition: React.FC<{
  durationInFrames: number;
  direction?: "left" | "right" | "top" | "bottom";
  children: React.ReactNode;
}> = ({ durationInFrames, direction = "left", children }) => {
  const frame = useCurrentFrame();
  const { width, height } = useVideoConfig();

  const translation = interpolate(
    frame,
    [0, durationInFrames],
    [direction === "left" || direction === "right" ? width : height, 0],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  const style: React.CSSProperties = {
    position: "absolute",
    width: "100%",
    height: "100%",
    transform: direction === "left"
      ? `translateX(${translation}px)`
      : direction === "right"
      ? `translateX(${-translation}px)`
      : direction === "top"
      ? `translateY(${translation}px)`
      : `translateY(${-translation}px)`,
  };

  return (
    <AbsoluteFill style={style}>
      {children}
    </AbsoluteFill>
  );
};

// 3. ZOOM BLUR (Foco dinâmico e enérgico - muito comum em Shorts/TikTok virais)
export const ZoomBlurTransition: React.FC<{
  durationInFrames: number;
  children: React.ReactNode;
}> = ({ durationInFrames, children }) => {
  const frame = useCurrentFrame();

  // Reduz a escala de 1.25 para 1.0 (efeito de impacto)
  const scale = interpolate(
    frame,
    [0, durationInFrames],
    [1.25, 1.0],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  // Dissolve o desfoque de 20px para 0px
  const blur = interpolate(
    frame,
    [0, durationInFrames],
    [20, 0],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  // Suavização rápida da opacidade
  const opacity = interpolate(
    frame,
    [0, Math.floor(durationInFrames * 0.4)],
    [0, 1],
    { extrapolateRight: "clamp", extrapolateLeft: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        transform: `scale(${scale})`,
        filter: `blur(${blur}px)`,
        opacity,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};
