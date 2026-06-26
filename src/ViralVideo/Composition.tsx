import React from "react";
import { AbsoluteFill, Sequence, staticFile, Audio } from "remotion";
import { SceneComponent } from "./SceneComponent";
import { ZoomBlurTransition } from "./Transitions";
import { VideoData } from "../types";
import rawScenesData from "../../public/scenes_data.json";

// Forçamos a tipagem dos dados importados do JSON
const scenesData = rawScenesData as VideoData;

export const ViralComposition: React.FC = () => {
  const transitionDuration = 15; // 0.5s de sobreposição a 30fps
  let cumulativeFrame = 0;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {/* Música de fundo suave em loop */}
      <Audio 
        src={staticFile("background_music.mp3")} 
        volume={0.12} 
        loop 
      />

      {scenesData.scenes.map((scene, index) => {
        const isFirst = index === 0;
        
        // Cenas seguintes começam 15 frames antes de a anterior acabar para aplicar a sobreposição
        const startFrame = isFirst ? 0 : cumulativeFrame - transitionDuration;
        const duration = scene.duration_in_frames;
        
        // Atualiza o frame acumulado para o início da próxima cena
        cumulativeFrame = startFrame + duration;

        return (
          <Sequence
            key={scene.scene_number}
            from={startFrame}
            durationInFrames={duration}
          >
            {isFirst ? (
              <SceneComponent scene={scene} />
            ) : (
              // Aplica a transição ZoomBlur de entrada apenas nas cenas subsequentes
              <ZoomBlurTransition durationInFrames={transitionDuration}>
                <SceneComponent scene={scene} />
              </ZoomBlurTransition>
            )}
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
