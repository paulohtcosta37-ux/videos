import "./index.css";
import { Composition } from "remotion";
import { HelloWorld, myCompSchema } from "./HelloWorld";
import { Logo, myCompSchema2 } from "./HelloWorld/Logo";
import { ViralComposition } from "./ViralVideo/Composition";
import rawScenesData from "../public/scenes_data.json";
import { VideoData } from "./types";

const scenesData = rawScenesData as VideoData;
const transitionDuration = 15;
const totalDuration = scenesData.scenes.reduce((acc, s, index) => {
  if (index === 0) return s.duration_in_frames;
  return acc + s.duration_in_frames - transitionDuration;
}, 0);

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="ViralVideo"
        component={ViralComposition}
        durationInFrames={totalDuration || 90}
        fps={30}
        width={1080}
        height={1920}
      />

      <Composition
        // You can take the "id" to render a video:
        // npx remotion render HelloWorld
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        // You can override these props for each render:
        // https://www.remotion.dev/docs/parametrized-rendering
        schema={myCompSchema}
        defaultProps={{
          titleText: "Welcome to Remotion",
          titleColor: "#000000",
          logoColor1: "#91EAE4",
          logoColor2: "#86A8E7",
        }}
      />

      {/* Mount any React component to make it show up in the sidebar and work on it individually! */}
      <Composition
        id="OnlyLogo"
        component={Logo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        schema={myCompSchema2}
        defaultProps={{
          logoColor1: "#91dAE2" as const,
          logoColor2: "#86A8E7" as const,
        }}
      />
    </>
  );
};
