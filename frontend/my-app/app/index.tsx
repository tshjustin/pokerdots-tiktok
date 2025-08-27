// app/index.tsx
import { Redirect } from 'expo-router';

export default function Index() {
  // send first-time users to login; change to '/(tabs)/home' if you want
  return <Redirect href="/(auth)/login" />;
}
