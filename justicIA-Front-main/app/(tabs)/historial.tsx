import DocumentList from "@/components/DocumentList";
import Header from "@/components/Header";
import { LinearGradient } from "expo-linear-gradient";
import { useRouter } from "expo-router";
import React, { useState } from "react";
import {
  Dimensions,
  StyleSheet,
  Text,
  TouchableOpacity,
  View
} from "react-native";

const { width, height } = Dimensions.get("window");

export default function principal() {
  const router = useRouter();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  return (
    <LinearGradient
      colors={["#74409B", "#384C81"]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 0 }}
    >
      <Header/>
      <View style={styles.body}>

        <DocumentList
          selectedId={selectedId}
          onSelect={(id) => setSelectedId(id)}
        />

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[styles.button, styles.reviewButton]}
            disabled={!selectedId}
            onPress={() => {
              router.push({
                pathname: "/documento",
                params: { id: selectedId },
              });
            }}
          >
            <Text style={styles.textButton}> Revisar</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, styles.processButton, !selectedId && styles.disabledButton]}
            disabled={!selectedId}
            onPress={() => {
              router.push({
                pathname: "/viewLoad",
                params: { id: selectedId },
              });
            }}
          >
            <Text style={[styles.textButton, styles.processButtonText]}>
               Procesar con IA
            </Text>
          </TouchableOpacity>
        </View>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  body: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  button: {
    backgroundColor: "#fff",
    width: width * 0.35, // Reducido para que quepan dos lado a lado
    height: height * 0.045,
    borderRadius: 25, // Reducido un poco el border radius
    paddingHorizontal: 10, // Reducido el padding
    marginTop: 8,
    flexDirection: "row",
    justifyContent: "center",
    alignItems: "center",
  },
  arrow: {
    fontSize: 20,
    color: "#384c81",
  },
  textButton: {
    fontSize: 14, // Reducido de 16 a 14 para botones más pequeños
    color: "#384c81",
    fontFamily: "Poppins",
    fontWeight: "800",
  },
  // Nuevos estilos para los botones
  buttonContainer: {
    flexDirection: "row", // Cambiado de "column" a "row"
    alignItems: "center",
    justifyContent: "space-around", // Para distribuir uniformemente
    gap: 15, // Espacio entre botones
    marginTop: 20,
    paddingHorizontal: 20, // Padding horizontal para los bordes
  },
  reviewButton: {
    backgroundColor: "#fff",
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  processButton: {
    backgroundColor: "#28A745", // Verde vibrante para mejor contraste
    width: width * 0.35, // Mismo tamaño que el botón revisar
    shadowColor: "#000",
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  processButtonText: {
    color: "#fff",
    fontWeight: "bold",
    fontSize: 14, // Reducido de 16 a 14 para consistencia
  },
  disabledButton: {
    backgroundColor: "#8E8E93",
    opacity: 0.8,
    shadowOpacity: 0.1,
  },
});
