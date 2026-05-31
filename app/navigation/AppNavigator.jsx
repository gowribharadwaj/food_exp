import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import { Text } from 'react-native';
import HomeScreen from '../screens/HomeScreen';
import AddScreen from '../screens/AddScreen';
import RecipeScreen from '../screens/RecipeScreen';
import PantryScreen from '../screens/PantryScreen';

const Tab = createBottomTabNavigator();
const Stack = createStackNavigator();

function HomeStack() {
  return (
    <Stack.Navigator screenOptions={{ headerShown: false }}>
      <Stack.Screen name="Home" component={HomeScreen} />
      <Stack.Screen name="Add" component={AddScreen} />
    </Stack.Navigator>
  );
}

export default function AppNavigator() {
  return (
    <NavigationContainer>
      <Tab.Navigator
        screenOptions={{
          headerShown: false,
          tabBarActiveTintColor: '#4CAF50',
          tabBarInactiveTintColor: '#888',
          tabBarStyle: { paddingBottom: 5, height: 60 },
        }}
      >
        <Tab.Screen
          name="Dashboard"
          component={HomeStack}
          options={{ tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🏠</Text> }}
        />
        <Tab.Screen
          name="Pantry"
          component={PantryScreen}
          options={{ tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>🥫</Text> }}
        />
        <Tab.Screen
          name="Recipes"
          component={RecipeScreen}
          options={{ tabBarIcon: ({ color }) => <Text style={{ color, fontSize: 20 }}>👨‍🍳</Text> }}
        />
      </Tab.Navigator>
    </NavigationContainer>
  );
}