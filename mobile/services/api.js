import axios from 'axios';

const BASE_URL = 'http://192.168.29.133:8000';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
});

export const getPantry = () => api.get('/pantry/');
export const addPantryItem = (item) => api.post('/pantry/', item);
export const deletePantryItem = (id) => api.delete(`/pantry/${id}`);
export const lookupProduct = (name, storageType = 'fridge') =>
  api.post('/lookup/', { name, storage_type: storageType });

// Recipes needs longer timeout — Ollama takes 30-60 seconds
export const getRecipes = (expiringItems) =>
  axios.post(`${BASE_URL}/recipes/`, 
    { expiring_items: expiringItems },
    { timeout: 120000 }
  );