import React from 'react';
import { View, Text } from 'react-native';
import { Clock, Package, Truck } from 'lucide-react-native';
import { Shift } from '@/lib/types';

interface ShiftCardProps {
  shift: Shift;
}

const ShiftCard: React.FC<ShiftCardProps> = ({ shift }) => {
  const isPickup = shift.type === 'pickup';
  
  return (
    <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 12, borderWidth: 1, borderColor: '#F3F4F6' }}>
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12 }}>
        <View style={{
          width: 40,
          height: 40,
          borderRadius: 20,
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: isPickup ? '#DBEAFE' : '#D1FAE5',
        }}>
          {isPickup ? (
            <Package size={20} {...({ stroke: '#2563EB' } as any)} />
          ) : (
            <Truck size={20} {...({ stroke: '#10B981' } as any)} />
          )}
        </View>
        <View style={{ marginLeft: 12, flex: 1 }}>
          <Text style={{ fontSize: 18, fontWeight: '700', color: '#111827' }}>
            {isPickup ? 'Pickup Shift' : 'Delivery Shift'}
          </Text>
          <Text style={{ fontSize: 14, color: '#4B5563' }}>
            {shift.tasksCount} tasks assigned
          </Text>
        </View>
      </View>

      <View style={{ flexDirection: 'row', alignItems: 'center' }}>
        <Clock size={16} {...({ stroke: '#6B7280' } as any)} />
        <Text style={{ fontSize: 14, color: '#374151', marginLeft: 8 }}>
          {shift.startTime} - {shift.endTime}
        </Text>
      </View>
    </View>
  );
};

export default ShiftCard;