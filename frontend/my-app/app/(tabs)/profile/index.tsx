import { createMaterialTopTabNavigator } from '@react-navigation/material-top-tabs';
import { View, Text, Image, StyleSheet, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import Appreciations from './appreciations';
import Dashboard from './dashboard';
import { useEffect, useState } from 'react';
import StatsRow from '../../../src/components/StatsRow';
import { fetchProfileSummary, ProfileSummary } from '../../../src/services/profileService';

const Top = createMaterialTopTabNavigator();

export default function ProfilePage() {
  const [data, setData] = useState<ProfileSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const res = await fetchProfileSummary('current-user-id');
        setData(res);
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) {
    return (
      <SafeAreaView style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator />
      </SafeAreaView>
    );
  }

  if (!data) return null;

  return (
    <SafeAreaView style={{ flex: 1 }} edges={['right', 'top', 'left']}>
      {/* Profile Header */}
      <View style={s.header}>
        <Image source={{ uri: data.avatarUrl }} style={s.avatar} />
        <Text style={s.username}>{data.username}</Text>

        <StatsRow
          items={[
            { label: 'Following', value: data.following },
            { label: 'Followers', value: data.followers },
            { label: 'Likes', value: data.likes },
          ]}
        />
      </View>

      {/* Top Tabs */}
      <Top.Navigator
        screenOptions={{
          tabBarIndicatorStyle: { backgroundColor: '#000' },
          tabBarLabelStyle: { fontWeight: '600' },
        }}
      >
        <Top.Screen name="dashboard" component={Dashboard} options={{ title: 'Dashboard' }} />
        <Top.Screen name="appreciations" component={Appreciations} options={{ title: 'Appreciation' }} />
      </Top.Navigator>
    </SafeAreaView>
  );
}

const s = StyleSheet.create({
  header: { alignItems: 'center', paddingVertical: 20 },
  avatar: { width: 100, height: 100, borderRadius: 50, marginBottom: 10 },
  username: { fontSize: 18, fontWeight: '600', marginBottom: 12 },
});
