// src/components/videoPlayer.tsx
import React, { forwardRef, useEffect, useImperativeHandle, useMemo } from "react";
import { View, StyleSheet, StyleProp, ViewStyle } from "react-native";
import { useVideoPlayer, VideoView, type VideoSource } from "expo-video";

export type VideoPlayerHandle = { play: () => void; pause: () => void };

type Position = { dx: number; dy: number } | "center";
type Fit = "cover" | "contain" | "fill";

export type Props = {
  uri: string;
  paused?: boolean;            // external control only
  fit?: Fit;
  position?: Position;
  style?: StyleProp<ViewStyle>;
};

const VideoPlayer = forwardRef<VideoPlayerHandle, Props>(
  ({ uri, paused = false, fit = "cover", position = "center", style }, ref) => {
    const source: VideoSource = useMemo(() => ({ uri, useCaching: true }), [uri]);

    const player = useVideoPlayer(source, (p) => {
      p.loop = true;
      p.muted = false;                 // always unmuted
      p.audioMixingMode = "mixWithOthers"; // avoid OS auto-muting
      if (!paused) p.play();
    });

    useImperativeHandle(ref, () => ({
      play: () => {
        player.muted = false;
        try { player.volume = 1; } catch {}
        player.play();
      },
      pause: () => player.pause(),
    }), [player]);

    // Drive play/pause; make sure to unmute *before* resuming
    useEffect(() => {
      if (paused) {
        player.pause();
      } else {
        player.muted = false;
        try { player.volume = 1; } catch {}
        player.play();
      }
    }, [paused, player]);

    // When playback transitions to playing, re-assert unmuted just in case
    useEffect(() => {
      const sub = player.addListener("playingChange", ({ isPlaying }) => {
        if (isPlaying) {
          player.muted = false;
          try { player.volume = 1; } catch {}
        }
      });
      return () => sub.remove();
    }, [player]);

    const mappedContentPosition =
      position === "center" ? { dx: 0.5, dy: 0.5 } : position;

    return (
      <View style={[styles.container, style]}>
        <VideoView
          player={player}
          style={StyleSheet.absoluteFill}
          contentFit={fit}
          contentPosition={mappedContentPosition}
          allowsFullscreen={false}
          allowsPictureInPicture={false}
        />
      </View>
    );
  }
);

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "black", overflow: "hidden" },
});

export default VideoPlayer;
