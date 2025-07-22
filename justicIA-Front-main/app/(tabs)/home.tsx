import Header from "@/components/Header";
import { LinearGradient } from "expo-linear-gradient";
import { useRouter } from "expo-router";
import React, { useEffect, useState } from "react";
import { ActivityIndicator, Image, StyleSheet, Text, TouchableOpacity, View } from "react-native";
import { apiService, Caso } from "@/services/api";

export default function Home() {
  const [caso, setCaso] = useState<Caso | null>(null);
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchUltimoCaso = async () => {
      try {
        setError(null);
        const data = await apiService.getCasos();

        if (data.length > 0) {
          const ultimo = data[data.length - 1];
          setCaso(ultimo);
        } else {
          setCaso(null);
        }
      } catch (error) {
        console.error("Error cargando casos:", error);
        setError("Error de conexión con el servidor");
        setCaso(null);
      } finally {
        setCargando(false);
      }
    };

    fetchUltimoCaso();

    const intervalo = setInterval(fetchUltimoCaso, 20000);

    return () => clearInterval(intervalo);
  }, []);
  const handleProcesar = () => {
    if (caso) {
      router.push({
        pathname: "/viewLoad",
        params: { id: caso.id },
      });
    }
  };

  return (
    <LinearGradient
      colors={["#74409B", "#384C81"]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 0 }}
    >
      <Header />
      <View style={styles.body}>
        <View style={styles.logoContainer}>
          <Image
            source={
              caso
                ? require("@/assets/images/logoOcupade.png")
                : require("@/assets/images/logoWhite.png")
            }
            style={styles.logo}
          />

          {/* Información del caso si existe */}
          {caso && (
            <View style={styles.casoInfo}>
              <Text style={styles.casoTitle}>📋 Último Caso Disponible:</Text>
              <Text style={styles.casoAlert} numberOfLines={2}>
                🚨 {caso.alerta}
              </Text>
              <Text style={styles.casoDescription} numberOfLines={3}>
                {caso.descripcion}
              </Text>
              <Text style={styles.casoUser}>
                👮 {caso.dispositivo?.user || "Usuario no especificado"}
              </Text>
            </View>
          )}

      {cargando ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.loadingText}>Conectando con servidor...</Text>
        </View>
      ) : error ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <Text style={styles.apiUrlText}>
            API: {apiService.getBaseURL()}
          </Text>
          <TouchableOpacity
            style={[styles.boton, { backgroundColor: "#FF6B6B" }]}
            onPress={() => {
              setCargando(true);
              // Reintentar conexión
              setTimeout(() => {
                setCargando(false);
              }, 2000);
            }}
          >
            <Text style={styles.botonTexto}>Reintentar</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <TouchableOpacity
          style={[styles.boton, { backgroundColor: caso ? "#2FA45C" : "#EEEEEE" }]}
          onPress={handleProcesar}
          disabled={!caso}
        >
          <Text style={styles.botonTexto}>
            {caso ? "Procesar Caso" : "Esperando Caso..."}
          </Text>
        </TouchableOpacity>
      )}
        </View>
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
  logoContainer: {
    alignItems: "center",
  },
  body: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  logo: {
    marginBottom: 20,
    width: 150,
    height: 150,
  },
  // Nuevos estilos para manejo de estados
  loadingContainer: {
    alignItems: "center",
  },
  loadingText: {
    color: "#fff",
    marginTop: 10,
    fontSize: 16,
  },
  errorContainer: {
    alignItems: "center",
    paddingHorizontal: 20,
  },
  errorText: {
    color: "#FF6B6B",
    fontSize: 16,
    textAlign: "center",
    marginBottom: 10,
  },
  apiUrlText: {
    color: "#fff",
    fontSize: 12,
    textAlign: "center",
    marginBottom: 15,
    opacity: 0.8,
  },
  button: {
    marginTop: 30,
    backgroundColor: "#fff",
    paddingHorizontal: 30,
    paddingVertical: 12,
    borderRadius: 25,
  },
  buttonText: {
    color: "#384C81",
    fontWeight: "bold",
    fontSize: 16,
  },
  boton: {
    padding: 15,
    borderRadius: 10,
  },
  botonTexto: {
    color: "#fff",
    fontSize: 18,
  },
  casoInfo: {
    backgroundColor: "#f8f9fa",
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: "#e9ecef",
  },
  casoTitle: {
    fontSize: 16,
    fontWeight: "bold",
    color: "#384C81",
    marginBottom: 8,
  },
  casoAlert: {
    fontSize: 14,
    color: "#dc3545",
    fontWeight: "600",
    marginBottom: 4,
  },
  casoDescription: {
    fontSize: 14,
    color: "#6c757d",
    marginBottom: 4,
  },
  casoUser: {
    fontSize: 12,
    color: "#6c757d",
    fontStyle: "italic",
  },
});
