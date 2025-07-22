import { LinearGradient } from "expo-linear-gradient";
import { useLocalSearchParams, useRouter } from "expo-router";
import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Dimensions,
  Image,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { apiService, Caso, ChatBotResponse } from "@/services/api";

const { width, height } = Dimensions.get("window");

export default function PantallaCarga() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const [documento, setDocumento] = useState<Caso | null>(null);
  const [respuesta, setRespuesta] = useState<ChatBotResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const procesar = async () => {
      try {
        if (!id || typeof id !== 'string') {
          throw new Error('ID de caso inválido');
        }

        // Obtener el caso específico primero
        const casos = await apiService.getCasos();
        const casoEncontrado = casos.find(caso => caso.id === id);
        
        if (!casoEncontrado) {
          throw new Error('Caso no encontrado');
        }

        setDocumento(casoEncontrado);

        // Procesar con el chatbot
        const dataChat = await apiService.consultarChatbot(id);
        setRespuesta(dataChat);

        // Navegar a la pantalla de resultados
        router.replace({
          pathname: "/chatBot",
          params: {
            documento: JSON.stringify(casoEncontrado),
            respuesta: dataChat.respuesta,
          },
        });
      } catch (error) {
        console.error("Error en procesamiento:", error);
        setError(error instanceof Error ? error.message : 'Error desconocido');
        
        // Regresar después de 3 segundos en caso de error
        setTimeout(() => {
          router.back();
        }, 3000);
      }
    };

    if (id) procesar();
  }, [id]);

  return (
    <LinearGradient
      colors={["#74409B", "#384C81"]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 0 }}
    >
      <View style={styles.loaderContainer}>
        {error ? (
          <>
            <Text style={styles.errorText}>❌ Error</Text>
            <Text style={styles.errorDescription}>{error}</Text>
            <Text style={styles.redirectText}>Regresando...</Text>
          </>
        ) : (
          <>
            <ActivityIndicator size={180} color="#fff" />
            <Text style={styles.loadingText}>Generando Resolución Judicial</Text>
            <View style={styles.infoCard}>
              <View style={styles.rowCenter}>
                <Image
                  source={require("@/assets/images/docSearch.png")}
                  style={styles.infoIcon}
                  resizeMode="contain"
                />
                <Text style={styles.infoTitle}>
                  Inteligencia Artificial Jurídica
                </Text>
              </View>
              <Text style={styles.infoText}>
                Utilizamos modelos avanzados de IA entrenados con miles de casos
                judiciales para garantizar resoluciones precisas y fundamentadas
                legalmente.
              </Text>
            </View>
          </>
        )}
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loaderContainer: {
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  loadingText: {
    fontSize: 22,
    fontWeight: "bold",
    color: "#fff",
    marginTop: 20,
    textAlign: "center",
  },
  infoCard: {
    backgroundColor: "#6a676b",
    padding: 20,
    borderRadius: 10,
    marginTop: 30,
    width: width * 0.95,
  },
  infoText: {
    color: "#fff",
    fontSize: 16,
    textAlign: "justify",
  },
  rowCenter: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 10,
  },
  infoIcon: {
    width: 30,
    height: 30,
    marginRight: 10,
  },
  infoTitle: {
    fontWeight: "bold",
    color: "#fff",
    fontSize: 16,
  },
  // Nuevos estilos para manejo de errores
  errorText: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#FF6B6B",
    textAlign: "center",
    marginBottom: 20,
  },
  errorDescription: {
    fontSize: 18,
    color: "#fff",
    textAlign: "center",
    marginBottom: 20,
    paddingHorizontal: 20,
  },
  redirectText: {
    fontSize: 16,
    color: "#fff",
    textAlign: "center",
    opacity: 0.8,
  },
});
