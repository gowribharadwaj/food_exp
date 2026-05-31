import React, { useEffect, useState } from 'react';
import {
  View, Text, FlatList, StyleSheet,
  RefreshControl, ActivityIndicator
} from 'react-native';
import PantryCard from '../../components/PantryCard';
import { getPantry, deletePantryItem } from '../../services/api';

export default function PantryScreen() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchPantry = async () => {
    try {
      const res = await getPantry();
      setItems(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => { fetchPantry(); }, []);

  const handleDelete = async (id) => {
    await deletePantryItem(id);
    fetchPantry();
  };

  const red = items.filter(i => i.urgency === 'red');
  const yellow = items.filter(i => i.urgency === 'yellow');
  const green = items.filter(i => i.urgency === 'green');

  if (loading) return <ActivityIndicator style={{ flex: 1 }} size="large" color="#4CAF50" />;

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Full Pantry</Text>
      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => <PantryCard item={item} onDelete={handleDelete} />}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => {
          setRefreshing(true); fetchPantry();
        }} />}
        ListHeaderComponent={
          <View style={styles.summary}>
            <Text style={[styles.dot, { color: '#FF4444' }]}>● {red.length} expiring</Text>
            <Text style={[styles.dot, { color: '#FFA500' }]}>● {yellow.length} soon</Text>
            <Text style={[styles.dot, { color: '#4CAF50' }]}>● {green.length} fresh</Text>
          </View>
        }
        ListEmptyComponent={<Text style={styles.empty}>Pantry is empty.</Text>}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  title: { fontSize: 24, fontWeight: '700', padding: 20, paddingTop: 60, backgroundColor: '#fff' },
  summary: { flexDirection: 'row', gap: 16, padding: 16 },
  dot: { fontSize: 14, fontWeight: '600' },
  empty: { textAlign: 'center', marginTop: 60, color: '#888' },
});