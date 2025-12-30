import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Calendar, CheckCircle2, XCircle, TrendingUp } from 'lucide-react-native';
import StatusBadge from '@/components/StatusBadge';
import { historyTasks } from '@/lib/mockOrders';

export default function HistoryScreen() {
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'delivered' | 'failed'>('all');

  const filteredTasks = selectedFilter === 'all' 
    ? historyTasks 
    : historyTasks.filter(t => t.status === selectedFilter);

  const deliveredCount = historyTasks.filter(t => t.status === 'delivered').length;
  const failedCount = historyTasks.filter(t => t.status === 'failed').length;
  const successRate = Math.round((deliveredCount / historyTasks.length) * 100);

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {/* Statistics Card */}
        <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 24, marginBottom: 16 }}>
          <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 16 }}>
            <TrendingUp size={20} {...({ stroke: '#2563EB' } as any)} />
            <Text style={{ fontSize: 18, fontWeight: '700', color: '#111827', marginLeft: 8 }}>
              Performance Stats
            </Text>
          </View>

          <View style={{ flexDirection: 'row', justifyContent: 'space-around' }}>
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 32, fontWeight: '700', color: '#10B981' }}>{deliveredCount}</Text>
              <Text style={{ fontSize: 14, color: '#4b5563', marginTop: 4 }}>Delivered</Text>
            </View>
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 32, fontWeight: '700', color: '#ef4444' }}>{failedCount}</Text>
              <Text style={{ fontSize: 14, color: '#4b5563', marginTop: 4 }}>Failed</Text>
            </View>
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 32, fontWeight: '700', color: '#2563EB' }}>{successRate}%</Text>
              <Text style={{ fontSize: 14, color: '#4b5563', marginTop: 4 }}>Success Rate</Text>
            </View>
          </View>
        </View>

        {/* Filter Tabs */}
        <View style={{ flexDirection: 'row', marginBottom: 16, backgroundColor: '#fff', borderRadius: 12, padding: 8 }}>
          <FilterTab
            label="All"
            count={historyTasks.length}
            isActive={selectedFilter === 'all'}
            onPress={() => setSelectedFilter('all')}
          />
          <FilterTab
            label="Delivered"
            count={deliveredCount}
            isActive={selectedFilter === 'delivered'}
            onPress={() => setSelectedFilter('delivered')}
          />
          <FilterTab
            label="Failed"
            count={failedCount}
            isActive={selectedFilter === 'failed'}
            onPress={() => setSelectedFilter('failed')}
          />
        </View>

        {/* History List */}
        <View style={{ gap: 12 }}>
          {filteredTasks.map((order) => (
            <View
              style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#f3f4f6' }}
            >
              {/* Header */}
              <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
                <View style={{ flex: 1 }}>
                  <Text style={{ fontSize: 16, fontWeight: '700', color: '#111827', marginBottom: 4 }}>
                    {order.orderCode}
                  </Text>
                  <Text style={{ fontSize: 14, color: '#4b5563' }}>
                    {order.receiverName || order.senderName}
                  </Text>
                </View>
                <StatusBadge status={order.status} />
              </View>

              {/* Address */}
              <Text style={{ fontSize: 14, color: '#374151', marginBottom: 12 }} numberOfLines={1}>
                {order.deliveryAddress || order.pickupAddress}
              </Text>

              {/* Time Info */}
              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingTop: 12, borderTopWidth: 1, borderTopColor: '#f3f4f6' }}>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                  {order.status === 'delivered' ? (
                    <CheckCircle2 size={14} {...({ stroke: '#10B981' } as any)} />
                  ) : (
                    <XCircle size={14} {...({ stroke: '#EF4444' } as any)} />
                  )}
                  <Text style={{ fontSize: 12, color: '#4b5563', marginLeft: 4 }}>
                    {order.deliveryTime}
                  </Text>
                </View>
                <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                  <Calendar size={14} {...({ stroke: '#9CA3AF' } as any)} />
                  <Text style={{ fontSize: 12, color: '#6b7280', marginLeft: 4 }}>
                    Nov 15, 2024
                  </Text>
                </View>
              </View>

              {/* Failure Reason */}
              {order.failureReason && (
                <View style={{ backgroundColor: '#fef2f2', borderRadius: 8, padding: 12, marginTop: 12 }}>
                  <Text style={{ fontSize: 12, fontWeight: '600', color: '#7f1d1d', marginBottom: 4 }}>
                    Failure Reason:
                  </Text>
                  <Text style={{ fontSize: 12, color: '#991b1b' }}>
                    {order.failureReason}
                  </Text>
                </View>
              )}
            </View>
          ))}
        </View>

        {filteredTasks.length === 0 && (
          <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 32, alignItems: 'center' }}>
            <Text style={{ color: '#9ca3af', textAlign: 'center' }}>
              No {selectedFilter !== 'all' ? selectedFilter : ''} deliveries found
            </Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

interface FilterTabProps {
  label: string;
  count: number;
  isActive: boolean;
  onPress: () => void;
}

function FilterTab({ label, count, isActive, onPress }: FilterTabProps) {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={{ flex: 1, paddingVertical: 8, borderRadius: 8, backgroundColor: isActive ? '#2563EB' : 'transparent' }}
      activeOpacity={0.7}
    >
      <Text style={{ textAlign: 'center', fontWeight: '600', fontSize: 14, color: isActive ? '#fff' : '#4b5563' }}>
        {label} ({count})
      </Text>
    </TouchableOpacity>
  );
}