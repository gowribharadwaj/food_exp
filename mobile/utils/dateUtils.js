import { differenceInDays, parseISO } from 'date-fns';

export const getUrgency = (expiryDate) => {
  const today = new Date();
  const expiry = typeof expiryDate === 'string' ? parseISO(expiryDate) : expiryDate;
  const daysRemaining = differenceInDays(expiry, today);

  if (daysRemaining <= 1) return { color: '#FF4444', label: 'red', daysRemaining };
  if (daysRemaining <= 4) return { color: '#FFA500', label: 'yellow', daysRemaining };
  return { color: '#4CAF50', label: 'green', daysRemaining };
};

export const formatDate = (date) => {
  const d = typeof date === 'string' ? parseISO(date) : date;
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
};