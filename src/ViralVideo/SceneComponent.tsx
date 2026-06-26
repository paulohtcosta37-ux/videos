import React from "react";
import { 
  useCurrentFrame, 
  interpolate, 
  staticFile, 
  Video, 
  Audio, 
  Img,
  AbsoluteFill
} from "remotion";
import { Scene } from "../types";
import { Subtitle } from "./Subtitle";
import { DustParticles } from "./DustParticles";
import { LightLeaks } from "./LightLeaks";
import { VideoScene3D } from "./Scene3D";

interface SceneComponentProps {
  scene: Scene;
}

export const SceneComponent: React.FC<SceneComponentProps> = ({ scene }) => {
  const frame = useCurrentFrame();
  const durationInFrames = scene.duration_in_frames;

  // Efeito Ken Burns (Zoom suave de 1.0 a 1.15)
  const scale = interpolate(
    frame,
    [0, durationInFrames],
    [1.0, 1.18],
    { extrapolateRight: "clamp" }
  );

  // Movimento de câmera lento lateral (pan)
  const translateX = interpolate(
    frame,
    [0, durationInFrames],
    [-20, 20],
    { extrapolateRight: "clamp" }
  );

  // Movimento vertical leve (tilt)
  const translateY = interpolate(
    frame,
    [0, durationInFrames],
    [-10, 10],
    { extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", overflow: "hidden" }}>
      {scene.video_src ? (
        // Se houver vídeo (Avatar do SadTalker)
        <Video
          src={staticFile(scene.video_src)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
          }}
        />
      ) : (
        // Se houver imagem (Estilo de animação ou Fallback do avatar)
        <div
          style={{
            width: "100%",
            height: "100%",
            transform: `scale(${scale}) translate(${translateX}px, ${translateY}px)`,
            transformOrigin: "center center",
          }}
        >
          <Img
            src={staticFile(scene.image_src || "avatar.jpg")}
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
            }}
          />
        </div>
      )}

      {/* Camadas de Efeitos Atmosféricos Dinâmicos */}
      <LightLeaks />
      <DustParticles />

      {/* Áudio da Narração */}
      <Audio src={staticFile(scene.audio_src)} />

      {/* Legendas dinâmicas */}
      <Subtitle words={scene.subtitles} />
    </AbsoluteFill>
  );
};
