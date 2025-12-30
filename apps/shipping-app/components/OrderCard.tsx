import React from 'react';
import { View, Text, TouchableOpacity } from 'react-native';
import { MapPin, Package, Clock } from 'lucide-react-native';
import { Order } from '@/lib/types';
import StatusBadge from './StatusBadge';

interface OrderCardProps {
  order: Order;
  onPress: () => void;
  showETA?: boolean;
}

const OrderCard: React.FC<OrderCardProps> = ({ order, onPress, showETA = false }) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: '#F3F4F6' }}
      activeOpacity={0.7}
    >
      {/* Header */}
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <View style={{ flex: 1 }}>
          <Text style={{ fontSize: 18, fontWeight: '700', color: '#111827', marginBottom: 4 }}>
            {order.orderCode}
          </Text>
          <Text style={{ fontSize: 14, color: '#4B5563' }}>
            {order.senderName || order.receiverName}
          </Text>
        </View>
        <StatusBadge status={order.status} />
      </View>

      {/* Address */}
      <View style={{ flexDirection: 'row', alignItems: 'flex-start', marginBottom: 12 }}>
        <MapPin size={16} {...({ stroke: '#6B7280' } as any)} style={{ marginTop: 2, marginRight: 8 }} />
        <Text style={{ fontSize: 14, color: '#374151', flex: 1 }} numberOfLines={2}>
          {order.deliveryAddress || order.pickupAddress}
        </Text>
      </View>

      {/* Bottom Info */}
      <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <View style={{ flexDirection: 'row', alignItems: 'center' }}>
          <Package size={14} {...({ stroke: '#9CA3AF' } as any)} />
          <Text style={{ fontSize: 12, color: '#6B7280', marginLeft: 4 }}>
            {order.distanceKm} km
          </Text>
          {order.weight && (
            <Text style={{ fontSize: 12, color: '#6B7280', marginLeft: 8 }}>
              • {order.weight} kg
            </Text>
          )}
        </View>
        
        {showETA && order.eta && (
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Clock size={14} {...({ stroke: '#2563EB' } as any)} />
            <Text style={{ fontSize: 12, color: '#2563EB', fontWeight: '600', marginLeft: 4 }}>
              ETA {order.eta}
            </Text>
          </View>
        )}
        
        {order.pickupTime && !showETA && (
          <View style={{ flexDirection: 'row', alignItems: 'center' }}>
            <Clock size={14} {...({ stroke: '#6B7280' } as any)} />
            <Text style={{ fontSize: 12, color: '#4B5563', marginLeft: 4 }}>
              {order.pickupTime}
            </Text>
          </View>
        )}
      </View>
    </TouchableOpacity>
  );
};

export default OrderCard;