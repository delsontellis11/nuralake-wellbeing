import { View, Text, StyleSheet, ScrollView } from 'react-native';

export default function LeadDetailScreen({ route }) {
  const { lead } = route.params;

  return (
    <ScrollView style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.label}>Name</Text>
        <Text style={styles.value}>{lead.name}</Text>

        <Text style={styles.label}>Phone</Text>
        <Text style={styles.value}>{lead.phone}</Text>

        <Text style={styles.label}>Intent</Text>
        <Text style={styles.value}>{lead.intent}</Text>

        <Text style={styles.label}>Captured At</Text>
        <Text style={styles.value}>
          {new Date(lead.created_at).toLocaleString()}
        </Text>

        <Text style={styles.label}>Last Updated</Text>
        <Text style={styles.value}>
          {new Date(lead.updated_at).toLocaleString()}
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FDF6F0' },
  card: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 20,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  label: {
    fontSize: 12,
    color: '#999',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginTop: 16,
    marginBottom: 4,
  },
  value: { fontSize: 16, color: '#333', fontWeight: '500' },
});