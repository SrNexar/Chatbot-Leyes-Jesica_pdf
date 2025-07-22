import Header from "@/components/Header";
import { LinearGradient } from "expo-linear-gradient";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useEffect, useState } from "react";
import {
    Dimensions,
    StyleSheet,
    Text,
    TouchableOpacity,
    View
} from "react-native";
import { apiService, Caso } from "@/services/api";

const { width, height } = Dimensions.get("window");

export default function Documento() {
  const { id } = useLocalSearchParams();
  const [documento, setDocumento] = useState<Caso | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const procesar = async () => {
      try {
        if (!id || typeof id !== 'string') {
          throw new Error('ID de documento inválido');
        }

        setError(null);
        // Obtener todos los casos y buscar el específico
        const casos = await apiService.getCasos();
        const casoEncontrado = casos.find(caso => caso.id === id);
        
        if (!casoEncontrado) {
          throw new Error('Documento no encontrado');
        }

        setDocumento(casoEncontrado);
      } catch (error) {
        console.error("Error al obtener documento:", error);
        setError(error instanceof Error ? error.message : 'Error desconocido');
      } finally {
        setLoading(false);
      }
    };

    if (id) procesar();
  }, [id]);

  if (loading) {
    return (
      <LinearGradient
        colors={["#74409B", "#384C81"]}
        style={styles.container}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      >
        <Header />
        <View style={styles.loadingContainer}>
          <Text style={styles.loadingText}>Cargando documento...</Text>
        </View>
      </LinearGradient>
    );
  }

  if (error) {
    return (
      <LinearGradient
        colors={["#74409B", "#384C81"]}
        style={styles.container}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      >
        <Header />
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>❌ Error</Text>
          <Text style={styles.errorDescription}>{error}</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => router.back()}
          >
            <Text style={styles.retryButtonText}>Regresar</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  if (!documento) {
    return (
      <LinearGradient
        colors={["#74409B", "#384C81"]}
        style={styles.container}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 0 }}
      >
        <Header />
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>📄 Sin Documento</Text>
          <Text style={styles.errorDescription}>No se encontró el documento solicitado</Text>
          <TouchableOpacity
            style={styles.retryButton}
            onPress={() => router.back()}
          >
            <Text style={styles.retryButtonText}>Regresar</Text>
          </TouchableOpacity>
        </View>
      </LinearGradient>
    );
  }

  return (
    <LinearGradient
      colors={["#74409B", "#384C81"]}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 0 }}
    >
      <Header />
      <View style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.title}>Detalles del Caso</Text>

          <Text style={styles.label}>Fecha:</Text>
          <Text style={styles.value}>
            {documento.dispositivo?.fecha || "No disponible"}
          </Text>

          <Text style={styles.label}>Hora:</Text>
          <Text style={styles.value}>
            {documento.dispositivo?.hora || "No disponible"}
          </Text>

          <Text style={styles.label}>Nombre de la policía:</Text>
          <Text style={styles.value}>
            {documento.dispositivo?.nombrePolicia || documento.dispositivo?.user || "No disponible"}
          </Text>
          
          <Text style={styles.label}>Ubicación:</Text>
          <Text style={styles.value}>
            {documento.dispositivo?.ubicacion || "No disponible"}
          </Text>

          <Text style={styles.label}>Descripción del caso:</Text>
          <Text style={styles.value}>
            {documento.descripcion || "No disponible"}
          </Text>
        </View>
        <TouchableOpacity
          style={styles.button}
          onPress={() => {
            router.push({
              pathname: "/historial",
            });
          }}
        >
            <Text style={styles.textButton}>Regresar</Text>
        </TouchableOpacity>
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    justifyContent: "center",
    alignItems: "center",
    padding: 10,
    height: height * 0.6,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 10,
    padding: 20,
    elevation: 5,
    marginBottom: 20,
  },
  textButton: {
    fontSize: 20,
    color: "#384c81",
    fontFamily: "Poppins",
    fontWeight: "800",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 10,
    color: "#333",
  },
  label: {
    fontWeight: "bold",
    color: "#555",
    marginTop: 10,
  },
  value: {
    color: "#000",
    marginBottom: 5,
  },
  text: {
    color: "#fff",
    padding: 20,
    fontSize: 18,
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
  // Nuevos estilos para manejo de estados
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    color: "#fff",
    fontSize: 18,
    textAlign: "center",
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  errorText: {
    fontSize: 24,
    fontWeight: "bold",
    color: "#FF6B6B",
    textAlign: "center",
    marginBottom: 20,
  },
  errorDescription: {
    fontSize: 16,
    color: "#fff",
    textAlign: "center",
    marginBottom: 20,
  },
  retryButton: {
    backgroundColor: "#fff",
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 5,
  },
  retryButtonText: {
    color: "#384C81",
    fontWeight: "bold",
    fontSize: 16,
  },
});
