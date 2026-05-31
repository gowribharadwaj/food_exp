import React, { useEffect, useState } from 'react';
import {
  View, Text, FlatList, StyleSheet,
  ActivityIndicator, RefreshControl, TouchableOpacity
} from 'react-native';
import { useRouter } from 'expo-router';
import PantryCard from '../../components/PantryCard';
import { getPantry, deletePantryItem } from '../../services/api';

export default function HomeScreen() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const router = useRouter();

  const fetchPantry = async () => {
    try {
      const res = await getPantry();
      setItems(res.data);
    } catch (e) {
      console.error('Failed to fetch pantry:', e);
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

  const expiringSoon = items.filter(i => i.urgency === 'red' || i.urgency === 'yellow');

  if (loading) return <ActivityIndicator style={styles.loader} size="large" color="#4CAF50" />;

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>My Pantry</Text>
        <TouchableOpacity onPress={() => router.push('/add')}>
          <Text style={styles.addBtn}>+ Add</Text>
        </TouchableOpacity>
      </View>

      {expiringSoon.length > 0 && (
        <View style={styles.alert}>
          <Text style={styles.alertText}>
            ⚠️ {expiringSoon.length} item{expiringSoon.length > 1 ? 's' : ''} expiring soon
          </Text>
        </View>
      )}

      <FlatList
        data={items}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <PantryCard item={item} onDelete={handleDelete} />
        )}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={() => {
            setRefreshing(true);
            fetchPantry();
          }} />
        }
        ListEmptyComponent={
          <Text style={styles.empty}>No items in pantry. Tap + Add to get started.</Text>
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  loader: { flex: 1 },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingTop: 60,
    backgroundColor: '#fff',
  },
  title: { fontSize: 24, fontWeight: '700', color: '#1a1a1a' },
  addBtn: { fontSize: 16, color: '#4CAF50', fontWeight: '600' },
  alert: {
    backgroundColor: '#FFF3CD',
    margin: 16,
    padding: 12,
    borderRadius: 8,
  },
  alertText: { color: '#856404', fontWeight: '500' },
  empty: { textAlign: 'center', marginTop: 60, color: '#888', fontSize: 16 },
});