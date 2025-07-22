import React from "react";
import { Dimensions, ScrollView, StyleSheet, Text, View } from "react-native";

const { width } = Dimensions.get("window");

export default function RespuestaChatbot({ texto }: { texto: string }) {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>🤖 Resolución del Chatbot</Text>
      <ScrollView style={styles.scrollArea} nestedScrollEnabled={true}>
        <Text style={styles.response}>{texto}</Text>
      </ScrollView>
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
  response: {
    fontSize: 16,
    color: "#333",
    lineHeight: 22,
  },
  scrollArea: {
    maxHeight: 220,
    marginBottom: 20,
  },
});
