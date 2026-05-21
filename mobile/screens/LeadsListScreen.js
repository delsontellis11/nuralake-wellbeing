import { useEffect, useState } from 'react';
import {
  View, Text, FlatList, TouchableOpacity,
  StyleSheet, ActivityIndicator, RefreshControl
} from 'react-native';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://ihtitagydthjtrmdldqz.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlodGl0YWd5ZHRoanRybWRsZHF6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzkyNTcyMDQsImV4cCI6MjA5NDgzMzIwNH0.AVCGdE-ONzAmNBkP5P2msNo8K8-FjVFRHqSoJkLdH0E'
);

export default function LeadsListScreen({ navigation }) {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchLeads = async () => {
    const { data, error } = await supabase
      .from('leads')
      .select('*')
      .order('created_at', { ascending: false });

    if (!error) setLeads(data);
    setLoading(false);
    setRefreshing(false);
  };

  useEffect(() => {
    fetchLeads();
    const interval = setInterval(fetchLeads, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#6B4226" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <FlatList
        data={leads}
        keyExtractor={(item) => item.id}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => {
            setRefreshing(true);
            fetchLeads();
          }} />
        }
        ListEmptyComponent={
          <View style={styles.center}>
            <Text style={styles.empty}>No leads yet</Text>
          </View>
        }
        renderItem={({ item }) => (
          <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate('LeadDetail', { lead: item })}
          >
            <View style={styles.cardHeader}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.time}>
                {new Date(item.created_at).toLocaleDateString()}
              </Text>
            </View>
            <Text style={styles.intent} numberOfLines={2}>{item.intent}</Text>
            <Text style={styles.phone}>{item.phone}</Text>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#FDF6F0' },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', marginTop: 100 },
  empty: { color: '#999', fontSize: 16 },
  card: {
    backgroundColor: '#fff',
    margin: 12,
    marginBottom: 0,
    padding: 16,
    borderRadius: 12,
    shadowColor: '#000',
    shadowOpacity: 0.08,
    shadowRadius: 8,
    elevation: 3,
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  name: { fontSize: 18, fontWeight: 'bold', color: '#6B4226' },
  time: { fontSize: 12, color: '#999' },
  intent: { fontSize: 14, color: '#555', marginBottom: 6 },
  phone: { fontSize: 12, color: '#999' },
});