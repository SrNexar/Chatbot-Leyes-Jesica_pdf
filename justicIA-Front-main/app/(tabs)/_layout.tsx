import Colors from "@/constants/Colors";
import { Tabs } from "expo-router";
import { Clock, Home } from "lucide-react-native";
import {
  Dimensions
} from "react-native";

const { width, height } = Dimensions.get("window");

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: Colors.primary[500],
          borderTopWidth: 0,
          height: height * 0.15,
          paddingTop: 8,
          paddingBottom: 8,
        },
        tabBarActiveTintColor: "#fff",
        tabBarInactiveTintColor: "#fff",
        tabBarLabelStyle: {
          fontSize: 12,
          fontWeight: "600",
        },
      }}
    >
      <Tabs.Screen
        name="home"
        options={{
          title: "Inicio",
          tabBarIcon: ({ color }) => <Home size={24} color={color} />,
        }}
      />
      <Tabs.Screen
        name="historial"
        options={{
          title: "Historial",
          tabBarIcon: ({ color }) => <Clock size={24} color={color} />,
        }}
      />
    </Tabs>
  );
}