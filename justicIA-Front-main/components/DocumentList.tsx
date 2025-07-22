// app/components/DocumentosList.tsx
import React, { useEffect, useState } from "react";
import {
  ActivityIndicator,
  Dimensions,
  FlatList,
  Image,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { apiService, Caso } from "@/services/api";

const { width, height } = Dimensions.get("window");

type CasoFormatted = {
  id: string;
  fecha: string;
  hora: string;
  nombrePolicia: string;
  ubicacion: string;
  descripcion: string;
};

type Props = {
  onSelect: (id: string) => void;
  selectedId: string | null;
};

export default function DocumentList({ onSelect, selectedId }: Props) {
  const [casos, setCasos] = useState<CasoFormatted[]>([]);
  const [visibleCasos, setVisibleCasos] = useState<CasoFormatted[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [index, setIndex] = useState(0);
  const ITEMS_PER_LOAD = 3;

  useEffect(() => {
    const loadCasos = async () => {
      try {
        setError(null);
        const data = await apiService.getCasos();
        
        // Transformamos los datos
        const casosFormateados = data.map((item: Caso) => ({
          id: item.id,
          fecha: item.dispositivo?.fecha || "Sin fecha",
          hora: item.dispositivo?.hora || "Sin hora",
          nombrePolicia: item.dispositivo?.nombrePolicia || item.dispositivo?.user || "Sin nombre",
          ubicacion: item.dispositivo?.ubicacion || "Sin ubicación",
          descripcion: item.descripcion || "Sin descripción",
        }));

        setCasos(casosFormateados);
        setVisibleCasos(casosFormateados.slice(0, ITEMS_PER_LOAD));
      } catch (err) {
        console.error("Error loading casos:", err);
        setError("Error al cargar los casos");
      } finally {
        setLoading(false);
      }
    };

    loadCasos();
  }, []);

  const loadMore = () => {
    const nextIndex = index + ITEMS_PER_LOAD;
    const nextItems = casos.slice(0, nextIndex + ITEMS_PER_LOAD);
    setVisibleCasos(nextItems);
    setIndex(nextIndex);
  };

  const renderItem = ({ item }: { item: CasoFormatted }) => (
    <TouchableOpacity
      style={[
        styles.card,
        selectedId === item.id && styles.selectedCard,
      ]}
      onPress={() => onSelect(item.id)}
    >
      <Image
        source={require("@/assets/images/docIcon.png")}
        style={styles.docIcon}
      />
      <View style={styles.cardContent}>
        <Text style={styles.cardTime}>Fecha y Hora: {item.fecha} {item.hora}</Text>
        <Text style={styles.cardText}>Policía: {item.nombrePolicia}</Text>
        <Text numberOfLines={2} style={styles.cardText}>
          {item.descripcion}
        </Text>
      </View>
    </TouchableOpacity>
  );

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity
          style={styles.retryButton}
          onPress={() => {
            setLoading(true);
            setError(null);
          }}
        >
          <Text style={styles.retryButtonText}>Reintentar</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={{ height: height * 0.5, marginTop: "5%" }}>
      <Text style={styles.title}>Documentos cargados</Text>
      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#fff" />
          <Text style={styles.loadingText}>Cargando casos...</Text>
        </View>
      ) : visibleCasos.length === 0 ? (
        <Text style={styles.emptyText}>No hay casos disponibles</Text>
      ) : (
        <FlatList
          data={visibleCasos}
          keyExtractor={(item) => item.id}
          renderItem={renderItem}
          onEndReached={loadMore}
          onEndReachedThreshold={0.5}
          contentContainerStyle={{ paddingBottom: 20 }}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  title: {
    fontSize: 25,
    color: "#fff",
    fontFamily: "Poppins",
    fontWeight: "800",
    alignSelf: "flex-start",
    marginLeft: "-3%"
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  loadingText: {
    color: "#fff",
    marginTop: 10,
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 20,
  },
  errorText: {
    color: "#FF6B6B",
    fontSize: 16,
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
  },
  emptyText: {
    color: "#fff",
    fontSize: 16,
    textAlign: "center",
    marginTop: 50,
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 15,
    padding: 10,
    marginTop: 12,
    flexDirection: "row",
    alignItems: "center",
    width: width * 0.9,
  },
  selectedCard: {
    borderColor: "#6083e3ff",
    borderWidth: 3,
  },
  docIcon: {
    width: 40,
    height: 40,
    marginRight: 10,
  },
  cardContent: {
    flex: 1,
  },
  cardTime: {
    fontWeight: "bold",
    color: "#384C81",
  },
  cardText: {
    color: "#333",
    fontSize: 14,
  },
});
