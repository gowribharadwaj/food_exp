import React, { useEffect, useState } from 'react';
import {
  View, Text, StyleSheet, ScrollView,
  ActivityIndicator, TouchableOpacity
} from 'react-native';
import { getPantry, getRecipes } from '../../services/api';

export default function RecipeScreen() {
  const [recipes, setRecipes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [expiringItems, setExpiringItems] = useState([]);

  const fetchExpiring = async () => {
    try {
      const res = await getPantry();
      console.log('All pantry items:', JSON.stringify(res.data));
      const expiring = res.data
        .filter(i => i.urgency === 'red' || i.urgency === 'yellow')
        .map(i => i.name);
      console.log('Filtered expiring:', expiring);
      setExpiringItems(expiring);
      return expiring;
    } catch (e) {
      console.log('Fetch expiring error:', e.message);
      return [];
    }
  };

  const fetchRecipes = async () => {
    setLoading(true);
    const items = await fetchExpiring();
    console.log('Expiring items found:', items);
    if (items.length === 0) { 
      setLoading(false); 
      return; 
    }
    try {
      console.log('Calling recipes API with:', items);
      const res = await getRecipes(items);
      console.log('Recipe response:', res.data);
      setRecipes(res.data.recipes);
    } catch (e) {
      console.log('Recipe error details:', e.message, e.response?.data);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchExpiring(); }, []);

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>Recipe Suggestions</Text>
      {expiringItems.length > 0 && (
        <View style={styles.itemsBox}>
          <Text style={styles.subtitle}>Using expiring items:</Text>
          <Text style={styles.items}>{expiringItems.join(', ')}</Text>
        </View>
      )}
      <TouchableOpacity style={styles.btn} onPress={fetchRecipes} disabled={loading}>
        {loading
          ? <ActivityIndicator color="#fff" />
          : <Text style={styles.btnText}>Generate Recipes</Text>
        }
      </TouchableOpacity>
      {recipes.map((recipe, i) => (
        <View key={i} style={styles.recipeCard}>
          <Text style={styles.recipeText}>{recipe}</Text>
        </View>
      ))}
      {expiringItems.length === 0 && (
        <Text style={styles.empty}>No expiring items. Add groceries first.</Text>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5', padding: 20, paddingTop: 60 },
  title: { fontSize: 24, fontWeight: '700', marginBottom: 16, color: '#1a1a1a' },
  subtitle: { fontSize: 14, fontWeight: '600', color: '#555' },
  items: { fontSize: 14, color: '#1a1a1a', marginTop: 4 },
  itemsBox: { backgroundColor: '#FFF3CD', padding: 12, borderRadius: 10, marginBottom: 16 },
  btn: { backgroundColor: '#4CAF50', padding: 16, borderRadius: 12, alignItems: 'center', marginBottom: 20 },
  btnText: { color: '#fff', fontWeight: '700', fontSize: 16 },
  recipeCard: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: '#e0e0e0' },
  recipeText: { fontSize: 14, color: '#333', lineHeight: 22 },
  empty: { textAlign: 'center', marginTop: 40, color: '#888' },
});