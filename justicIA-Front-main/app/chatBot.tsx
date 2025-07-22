import RespuestaChatbot from "@/components/ChatbotResponse";
import DetalleDocumento from "@/components/DocumentDetail";
import Header from "@/components/Header";
import { LinearGradient } from "expo-linear-gradient";
import { useLocalSearchParams, useRouter } from "expo-router";
import React from "react";
import {
  Dimensions,
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";

const { width, height } = Dimensions.get("window");

export default function PantallaResultado() {
  const { documento, respuesta } = useLocalSearchParams();
  const caso = JSON.parse(documento as string);
  const router = useRouter();

  return (
    <LinearGradient
      colors={["#74409B", "#384C81"]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 0 }}
    >
      <Header />
      <ScrollView contentContainerStyle={styles.content}>
        <DetalleDocumento caso={caso} />
        <RespuestaChatbot texto={respuesta as string} />
        <TouchableOpacity style={styles.button} onPress={() => router.back()}>
          <Text style={styles.buttonText}>Regresar</Text>
        </TouchableOpacity>

        <View style={{ height: 50 }} />
      </ScrollView>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flexGrow: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
    gap: 20,
  },
  button: {
    backgroundColor: "#fff",
    width: width * 0.5,
    height: height * 0.06,
    borderRadius: 50,
    paddingHorizontal: 20,
    marginTop: 10,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
  },
  buttonText: {
    fontSize: 20,
    color: "#384c81",
    fontFamily: "Poppins",
    fontWeight: "800",
  },
});
