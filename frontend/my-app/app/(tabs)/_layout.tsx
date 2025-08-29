import { Tabs } from 'expo-router';
import { Image } from 'react-native';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#000',   // active labels black
        tabBarInactiveTintColor: '#888', // inactive labels gray
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: 'Home',
          tabBarIcon: ({ size, focused }) => (
            <Image
              source={require('../../assets/icons/home.png')}
              style={{
                width: size,
                height: size,
                tintColor: focused ? '#000' : '#888',
              }}
              resizeMode="contain"
            />
          ),
        }}
      />

      <Tabs.Screen
        name="add"
        options={{
          // Hide label
          tabBarLabel: () => null,
          // Always render as a static button (not tinted by active state)
          tabBarIcon: ({ size }) => (
            <Image
              source={require('../../assets/icons/add.png')}
              style={{
                width: 40,   // slightly larger for emphasis
                height: 40,
              }}
              resizeMode="contain"
            />
          ),
        }}
      />

      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profile',
          tabBarIcon: ({ size, focused }) => (
            <Image
              source={require('../../assets/icons/profile.png')}
              style={{
                width: size,
                height: size,
                tintColor: focused ? '#000' : '#888',
              }}
              resizeMode="contain"
            />
          ),
        }}
      />
    </Tabs>
  );
}
