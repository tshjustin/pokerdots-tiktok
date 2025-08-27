import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      {/* Auth stack */}
      <Stack.Screen name="(auth)" options={{ headerShown: false }} />
      {/* Main tabs */}
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
    </Stack>
  );
}
