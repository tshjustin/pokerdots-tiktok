import { Stack } from 'expo-router';
import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';
import Likes from './likes';
import Videos from './videos';

const Top = createMaterialTopTabNavigator();

export default function ProfileLayout() {
  // Wrap top tabs inside a stack screen so headerShown can be toggled if needed
  return (
    <Stack screenOptions={{ headerShown: false }}>
      <Stack.Screen name="index" options={{ headerShown: false }}>
        {() => (
          <Top.Navigator>
            <Top.Screen name="videos" component={Videos} options={{ title: 'Videos' }} />
            <Top.Screen name="likes" component={Likes} options={{ title: 'Likes' }} />
          </Top.Navigator>
        )}
      </Stack.Screen>
    </Stack>
  );
}
