// src/components/videoPlayer.tsx
import React, { forwardRef, useEffect, useImperativeHandle } from "react";
import { View, StyleSheet } from "react-native";
import { useVideoPlayer, VideoView, type VideoSource } from "expo-video";

export type VideoPlayerHandle = { play: () => void; pause: () => void };

type Props = {
  uri: string;
  paused?: boolean;
  muted?: boolean;
  fit?: "cover" | "contain" | "fill";               // 👈 add this
  position?: { dx: number; dy: number };            // 👈 iOS-only fine-tune
};

const VideoPlayer = forwardRef<VideoPlayerHandle, Props>(
  ({ uri, paused = false, muted = false, fit = "cover", position }, ref) => {
    const source: VideoSource = { uri, useCaching: true };
    const player = useVideoPlayer(source, (p) => {
      p.loop = true;
      p.muted = muted;
      if (!paused) p.play();
    });

    useImperativeHandle(ref, () => ({ play: () => player.play(), pause: () => player.pause() }), [player]);

    useEffect(() => { player.muted = muted; }, [muted, player]);
    useEffect(() => { paused ? player.pause() : player.play(); }, [paused, player]);

    return (
      <View style={styles.container}>
        <VideoView
          player={player}
          style={StyleSheet.absoluteFill}
          contentFit={fit}                   // 👈 center + scale as requested
          contentPosition={position}         // 👈 optional (iOS only)
          allowsFullscreen={false}
          allowsPictureInPicture={false}
        />
      </View>
    );
  }
);

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "black", overflow: "hidden" }, // overflow helps on Android
});

export default VideoPlayer;
