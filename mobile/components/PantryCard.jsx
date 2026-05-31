import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import ExpiryBadge from './ExpiryBadge';
import { formatDate } from '../utils/dateUtils';

export default function PantryCard({ item, onDelete }) {
  return (
    <View style={styles.card}>
      <View style={styles.left}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.meta}>{item.category} · {item.storage_type}</Text>
        <Text style={styles.date}>Expires: {formatDate(item.expiry_date)}</Text>
        {item.high_risk === true && (
          <Text style={styles.risk}>⚠️ High risk item</Text>
        )}
      </View>
      <View style={styles.right}>
        <ExpiryBadge expiryDate={item.expiry_date} />
        <TouchableOpacity onPress={() => onDelete(item.id)} style={styles.delete}>
          <Text style={styles.deleteText}>✕</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 6,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.06,
    shadowRadius: 4,
    elevation: 2,
  },
  left: { flex: 1 },
  right: { alignItems: 'flex-end', gap: 8 },
  name: { fontSize: 16, fontWeight: '600', color: '#1a1a1a' },
  meta: { fontSize: 12, color: '#888', marginTop: 2 },
  date: { fontSize: 12, color: '#555', marginTop: 2 },
  risk: { fontSize: 11, color: '#FF4444', marginTop: 2 },
  delete: { padding: 4 },
  deleteText: { color: '#FF4444', fontSize: 16 },
});