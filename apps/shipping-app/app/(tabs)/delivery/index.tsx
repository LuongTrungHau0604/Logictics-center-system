// app/delivery/index.tsx
import React, { useState, useCallback } from 'react';
import { View, ScrollView, RefreshControl, Text, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useFocusEffect } from 'expo-router';
import SectionHeader from '@/components/SectionHeader';
import OrderCard from '@/components/OrderCard';
import { orderClient } from '@/lib/api';

// Interface dữ liệu
interface DeliveryTask {
  leg_id: number;
  order_id: string;
  order_code: string;
  leg_status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  leg_type: string;
  receiver_name: string;
  receiver_phone: string;
  delivery_address: string;
  weight: number;
  notes?: string;
  receiver_latitude: number;
  receiver_longitude: number;
}

export default function DeliveryListScreen() {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState<DeliveryTask[]>([]);

  // Gọi API lấy danh sách
  const fetchTasks = useCallback(async () => {
    try {
      const res = await orderClient.get('/orders/shipper/my-deliveries');
      setTasks(res.data);
    } catch (error) {
      console.error("Lỗi lấy danh sách delivery:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      fetchTasks();
    }, [fetchTasks])
  );

  const onRefresh = () => {
    setRefreshing(true);
    fetchTasks();
  };

  

  const handlePressOrder = (task: DeliveryTask) => {
    router.push({
      // SỬA DÒNG NÀY: Dùng định dạng [id] thay vì điền số trực tiếp
      pathname: '/delivery/[id]', 
      
      // Expo sẽ tự lấy giá trị 'id' ở dưới này đắp vào '[id]' ở trên
      params: {
        id: task.order_id, 
        code: task.order_code,
        name: task.receiver_name,
        phone: task.receiver_phone,
        address: task.delivery_address,
        weight: task.weight,
        note: task.notes || '',
        status: task.leg_status
      }
    });
  };

  // Phân loại task
  const activeDeliveries = tasks.filter(t => t.leg_status === 'IN_PROGRESS');
  const pendingDeliveries = tasks.filter(t => t.leg_status === 'PENDING');
  const completedDeliveries = tasks.filter(t => t.leg_status === 'COMPLETED');

  if (loading && tasks.length === 0) {
    return (
      <SafeAreaView style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#2563EB" />
        <Text style={{ marginTop: 12, color: '#6B7280' }}>Đang tải đơn giao...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 16, paddingBottom: 100 }}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} />}
      >
        <SectionHeader
          title="Nhiệm vụ giao hàng"
          subtitle={`${pendingDeliveries.length + activeDeliveries.length} đơn cần giao`}
        />

        {/* 1. Đang đi giao */}
        {activeDeliveries.length > 0 && (
          <View style={{ marginBottom: 24 }}>
            <Text style={{ fontSize: 14, fontWeight: '600', color: '#2563EB', marginBottom: 12 }}>
              🚚 Đang trên đường giao ({activeDeliveries.length})
            </Text>
            {activeDeliveries.map((task) => (
              <OrderCard
                key={task.leg_id}
                order={{
                  id: task.order_id,
                  orderCode: task.order_code,
                  status: 'delivering',
                  senderName: task.receiver_name,
                  pickupAddress: task.delivery_address,
                  distanceKm: 0,
                  timeSlot: 'Ngay bây giờ'
                }}
                onPress={() => handlePressOrder(task)}
              />
            ))}
          </View>
        )}

        {/* 2. Chờ giao */}
        {pendingDeliveries.length > 0 && (
          <View style={{ marginBottom: 24 }}>
            <Text style={{ fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 12 }}>
              📦 Chờ đi giao ({pendingDeliveries.length})
            </Text>
            {pendingDeliveries.map((task) => (
              <OrderCard
                key={task.leg_id}
                order={{
                  id: task.order_id,
                  orderCode: task.order_code,
                  status: 'pending',
                  senderName: task.receiver_name,
                  pickupAddress: task.delivery_address,
                  distanceKm: 0,
                  timeSlot: 'Hôm nay'
                }}
                onPress={() => handlePressOrder(task)}
              />
            ))}
          </View>
        )}

        {/* 3. Đã giao xong */}
        {completedDeliveries.length > 0 && (
          <View>
            <Text style={{ fontSize: 14, fontWeight: '600', color: '#10B981', marginBottom: 12 }}>
              ✅ Đã giao xong ({completedDeliveries.length})
            </Text>
            {completedDeliveries.map((task) => (
              <OrderCard
                key={task.leg_id}
                order={{
                  id: task.order_id,
                  orderCode: task.order_code,
                  status: 'delivered',
                  senderName: task.receiver_name,
                  pickupAddress: task.delivery_address,
                  distanceKm: 0,
                  timeSlot: 'Hoàn tất'
                }}
                onPress={() => handlePressOrder(task)}
              />
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}