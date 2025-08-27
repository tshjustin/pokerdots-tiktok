// app/(tabs)/profile/_layout.tsx
import { Stack } from 'expo-router';

export default function ProfileLayout() {
  // No children/components here — just declare the navigator
  return <Stack screenOptions={{ headerShown: false }} />;
}
