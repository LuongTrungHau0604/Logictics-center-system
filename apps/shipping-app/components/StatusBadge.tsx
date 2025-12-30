import React from 'react';
import { View, Text } from 'react-native';
import { OrderStatus } from '@/lib/types';

interface StatusBadgeProps {
  status: OrderStatus;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const getStatusConfig = () => {
    switch (status) {
      case 'pending':
        return { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Pending' };
      case 'assigned':
        return { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Assigned' };
      case 'picked':
        return { bg: 'bg-purple-100', text: 'text-purple-700', label: 'Picked Up' };
      case 'delivering':
        return { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'In Transit' };
      case 'delivered':
        return { bg: 'bg-green-100', text: 'text-green-700', label: 'Delivered' };
      case 'failed':
        return { bg: 'bg-red-100', text: 'text-red-700', label: 'Failed' };
      default:
        return { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Unknown' };
    }
  };

  const config = getStatusConfig();

  return (
    <View style={{ backgroundColor: config.bg, paddingHorizontal: 12, paddingVertical: 4, borderRadius: 20 }}>
      <Text style={{ color: config.text, fontSize: 12, fontWeight: '600' }}>
        {config.label}
      </Text>
    </View>
  );
};

export default StatusBadge;