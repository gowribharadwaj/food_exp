import { Tabs } from 'expo-router';
import { Text } from 'react-native';

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#4CAF50',
        tabBarInactiveTintColor: '#888',
        tabBarStyle: { paddingBottom: 5, height: 60 },
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          tabBarLabel: 'Home',
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🏠</Text>,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          tabBarLabel: 'Pantry',
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🥫</Text>,
        }}
      />
      <Tabs.Screen
        name="recipes"
        options={{
          tabBarLabel: 'Recipes',
          tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>👨‍🍳</Text>,
        }}
      />
    </Tabs>
  );
}