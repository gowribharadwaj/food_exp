import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { getUrgency } from '../utils/dateUtils';

export default function ExpiryBadge({ expiryDate }) {
  const { color, daysRemaining } = getUrgency(expiryDate);

  const label =
    daysRemaining < 0 ? 'Expired' :
    daysRemaining === 0 ? 'Expires today' :
    daysRemaining === 1 ? 'Expires tomorrow' :
    `${daysRemaining} days left`;

  return (
    <View style={[styles.badge, { backgroundColor: color }]}>
      <Text style={styles.text}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  text: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
});