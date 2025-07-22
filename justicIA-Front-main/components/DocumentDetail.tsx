import React from "react";
import { Dimensions, StyleSheet, Text, View } from "react-native";
import { Caso } from "@/services/api";

const { width } = Dimensions.get("window");

export default function DocumentDetail({ caso }: { caso: Caso }) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>📄 Detalles del Caso</Text>
      <Text style={styles.item}>⚠️ Alerta: {caso.alerta}</Text>
      <Text style={styles.item}>📌 Dirección: {caso.dispositivo?.ubicacion || "No disponible"}</Text>
      <Text style={styles.item}>🕒 Hora del Hecho: {caso.dispositivo?.hora || "No disponible"}</Text>
      <Text style={styles.item}>📅 Fecha del Hecho: {caso.dispositivo?.fecha || "No disponible"}</Text>
      <Text style={styles.item} numberOfLines={4}>
        ℹ️ Descripción: {caso.descripcion || "No disponible"}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#fff",
    borderRadius: 12,
    padding: 20,
    width: width * 0.9,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 10,
    color: "#384C81",
  },
  item: {
    fontSize: 16,
    marginBottom: 6,
    color: "#333",
  },
});