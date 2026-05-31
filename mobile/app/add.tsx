import React, { useState } from 'react';
import {
  View, Text, TextInput, StyleSheet,
  TouchableOpacity, ScrollView, Alert, ActivityIndicator
} from 'react-native';
import { useRouter } from 'expo-router';
import { lookupProduct, addPantryItem } from '../services/api';

export default function AddScreen() {
  const [name, setName] = useState('');
  const [storageType, setStorageType] = useState('fridge');
  const [quantity, setQuantity] = useState('');
  const [loading, setLoading] = useState(false);
  const [lookupResult, setLookupResult] = useState(null);
  const router = useRouter();

  const handleLookup = async () => {
    if (!name.trim()) return;
    setLoading(true);
    try {
      const res = await lookupProduct(name, storageType);
      setLookupResult(res.data);
    } catch (e) {
      Alert.alert('Error', 'Could not look up product');
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    if (!lookupResult || !lookupResult.shelf_life_days) {
      Alert.alert('Error', 'No shelf life data found for this item');
      return;
    }
    const today = new Date();
    const expiry = new Date(today);
    expiry.setDate(today.getDate() + lookupResult.shelf_life_days);

    const item = {
      name: name.trim(),
      category: lookupResult.category,
      purchase_date: today.toISOString().split('T')[0],
      expiry_date: expiry.toISOString().split('T')[0],
      storage_type: storageType,
      high_risk: lookupResult.high_risk,
      quantity: quantity.trim() || null,
    };

    try {
      await addPantryItem(item);
      Alert.alert('Added!', `${name} added to pantry`);
      router.push('/');
    } catch (e) {
      Alert.alert('Error', 'Could not add item');
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Add Grocery</Text>

      <Text style={styles.label}>Product Name</Text>
      <TextInput
        style={styles.input}
        value={name}
        onChangeText={setName}
        placeholder="e.g. paneer, milk, bread"
        onSubmitEditing={handleLookup}
      />

      <Text style={styles.label}>Storage Type</Text>
      <View style={styles.options}>
        {['pantry', 'fridge', 'freezer'].map(opt => (
          <TouchableOpacity
            key={opt}
            style={[styles.option, storageType === opt && styles.optionActive]}
            onPress={() => setStorageType(opt)}
          >
            <Text style={[styles.optionText, storageType === opt && styles.optionTextActive]}>
              {opt}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Quantity (optional)</Text>
      <TextInput
        style={styles.input}
        value={quantity}
        onChangeText={setQuantity}
        placeholder="e.g. 500g, 1L, 2 pieces"
      />

      <TouchableOpacity style={styles.lookupBtn} onPress={handleLookup} disabled={loading}>
        {loading
          ? <ActivityIndicator color="#fff" />
          : <Text style={styles.btnText}>Look Up Shelf Life</Text>
        }
      </TouchableOpacity>

      {lookupResult && (
        <View style={styles.result}>
          <Text style={styles.resultTitle}>Found:</Text>
          <Text style={styles.resultText}>Category: {lookupResult.category}</Text>
          <Text style={styles.resultText}>
            Shelf life: {lookupResult.shelf_life_days
              ? `${lookupResult.shelf_life_days} days`
              : 'Unknown'}
          </Text>
          <Text style={styles.resultText}>
            High risk: {lookupResult.high_risk ? 'Yes ⚠️' : 'No'}
          </Text>
          <TouchableOpacity style={styles.addBtn} onPress={handleAdd}>
            <Text style={styles.btnText}>Add to Pantry</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5', padding: 20, paddingTop: 60 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 24, color: '#1a1a1a' },
  label: { fontSize: 14, fontWeight: '600', color: '#555', marginBottom: 6, marginTop: 16 },
  input: {
    backgroundColor: '#fff', borderRadius: 10,
    padding: 14, fontSize: 16,
    borderWidth: 1, borderColor: '#e0e0e0',
  },
  options: { flexDirection: 'row', gap: 10 },
  option: {
    flex: 1, padding: 12, borderRadius: 10,
    backgroundColor: '#fff', borderWidth: 1, borderColor: '#e0e0e0',
    alignItems: 'center',
  },
  optionActive: { backgroundColor: '#4CAF50', borderColor: '#4CAF50' },
  optionText: { color: '#555', fontWeight: '500' },
  optionTextActive: { color: '#fff' },
  lookupBtn: {
    backgroundColor: '#4CAF50', padding: 16,
    borderRadius: 12, alignItems: 'center', marginTop: 24,
  },
  addBtn: {
    backgroundColor: '#2196F3', padding: 16,
    borderRadius: 12, alignItems: 'center', marginTop: 12,
  },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  result: {
    backgroundColor: '#fff', borderRadius: 12,
    padding: 16, marginTop: 20, borderWidth: 1, borderColor: '#e0e0e0',
  },
  resultTitle: { fontSize: 16, fontWeight: '700', marginBottom: 8 },
  resultText: { fontSize: 14, color: '#555', marginBottom: 4 },
});