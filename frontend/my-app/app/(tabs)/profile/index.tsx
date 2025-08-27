// app/(tabs)/profile/index.tsx
import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';
import { SafeAreaView } from 'react-native-safe-area-context';
import Likes from './likes';
import Videos from './videos';

const Top = createMaterialTopTabNavigator();

export default function ProfileTabs() {
  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: 'white' }}>
        <Top.Navigator>
            <Top.Screen name="videos" component={Videos} options={{ title: 'Videos' }} />
            <Top.Screen name="likes" component={Likes} options={{ title: 'Likes' }} />
        </Top.Navigator>
    </SafeAreaView>

  );
}
