// app/(tabs)/FeedScreen.tsx
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { View, FlatList, StyleSheet, useWindowDimensions, type ViewToken, ActivityIndicator } from "react-native";
import { setAudioModeAsync } from "expo-audio";
import VideoPlayer, { VideoPlayerHandle } from "../../src/components/videoPlayer";

const DATA = [
  // use loud, known-good samples
  { id: "1", uri: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" },
  { id: "2", uri: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4" },
  { id: "3", uri: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/Sintel.mp4" },
  { id: "4", uri: "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4" },
];

export default function FeedScreen() {
  const { height, width } = useWindowDimensions();
  const PAGE_HEIGHT = Math.round(height);

  // ✅ Gate the UI until audio mode is applied (iOS silent switch)
  const [audioReady, setAudioReady] = useState(false);
  useEffect(() => {
    (async () => {
      try {
        await setAudioModeAsync({ playsInSilentMode: true }); // expo-audio API
        setAudioReady(true);
      } catch (e) {
        console.warn("setAudioModeAsync error:", e);
        setAudioReady(true); // still render so we can see other errors
      }
    })();
  }, []);

  const [activeIndex, setActiveIndex] = useState(0);
  const refs = useRef<Record<string, VideoPlayerHandle | null>>({});

  const onViewableItemsChanged = useRef(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      if (!viewableItems?.length) return;
      const nextIndex = viewableItems[0]?.index ?? 0;
      setActiveIndex(nextIndex);
    }
  ).current;

  const viewabilityConfig = useMemo(() => ({ itemVisiblePercentThreshold: 80 }), []);

  const makeRef = useCallback(
    (id: string) => (node: VideoPlayerHandle | null) => { refs.current[id] = node; },
    []
  );

  const renderItem = useCallback(
    ({ item, index }: { item: { id: string; uri: string }; index: number }) => (
      <View style={[styles.page, { height: PAGE_HEIGHT, width }]}>
        <VideoPlayer
          ref={makeRef(item.id)}
          uri={item.uri}
          paused={index !== activeIndex}
          muted={false}
          fit="cover"
          position={{ dx: 0, dy: 0 }}
        />
      </View>
    ),
    [activeIndex, PAGE_HEIGHT, width, makeRef]
  );

  if (!audioReady) {
    return (
      <View style={[styles.page, { height: PAGE_HEIGHT, width, alignItems: "center", justifyContent: "center" }]}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <FlatList
      data={DATA}
      keyExtractor={(item) => item.id}
      renderItem={renderItem}
      pagingEnabled
      decelerationRate="fast"
      showsVerticalScrollIndicator={false}
      snapToInterval={PAGE_HEIGHT}
      snapToAlignment="start"
      getItemLayout={(_, i) => ({ length: PAGE_HEIGHT, offset: PAGE_HEIGHT * i, index: i })}
      onViewableItemsChanged={onViewableItemsChanged}
      viewabilityConfig={viewabilityConfig}
      initialNumToRender={1}
      maxToRenderPerBatch={2}
      windowSize={3}
      removeClippedSubviews
    />
  );
}

const styles = StyleSheet.create({
  page: { backgroundColor: "black" },
});
