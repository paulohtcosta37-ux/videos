export interface SubtitleWord {
  text: string;
  start: number;
  end: number;
}

export interface Scene {
  scene_number: number;
  type: "presenter" | "animation";
  audio_src: string;
  duration_in_seconds: number;
  duration_in_frames: number;
  subtitles: SubtitleWord[];
  image_src?: string;
  video_src?: string;
}

export interface VideoData {
  scenes: Scene[];
}

export const defaultVideoData: VideoData = {
  scenes: [
    {
      scene_number: 1,
      type: "presenter",
      audio_src: "audio_1.mp3",
      duration_in_seconds: 3.0,
      duration_in_frames: 90,
      subtitles: [
        { text: "Olá!", start: 0.1, end: 1.0 },
        { text: "Bem-vindo", start: 1.0, end: 2.0 },
        { text: "ao", start: 2.0, end: 2.5 },
        { text: "canal.", start: 2.5, end: 3.0 }
      ],
      image_src: "avatar.jpg"
    }
  ]
};
