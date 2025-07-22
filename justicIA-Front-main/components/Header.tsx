// app/components/DocumentosList.tsx
import React from "react";
import {
  Dimensions,
  Image,
  StyleSheet,
  View
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
const { width, height } = Dimensions.get("window");

export default function Header() {
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.header, { paddingTop: insets.top }]}>
            <Image
              source={require("@/assets/images/logoFace.png")}
              style={styles.logo}
              resizeMode="contain"
            />
            <Image
              source={require("@/assets/images/kuntur.png")}
              style={styles.kuntur}
              resizeMode="contain"
            />
            <Image
              source={require("@/assets/images/iconBalance.png")}
              style={styles.logo}
              resizeMode="contain"
            />
          </View>
  );
}

const styles = StyleSheet.create({
  logo: {
    width: 60,
    height: 60,
  },
  kuntur: {
    width: 150,
    height: 100,
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingHorizontal: 20,
    width: "100%",
  }
});
