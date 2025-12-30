import React, { useState, useCallback, useEffect } from 'react';
import { View, ScrollView, RefreshControl, Text, ActivityIndicator, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useFocusEffect } from 'expo-router';
import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';

import SectionHeader from '@/components/SectionHeader';
import OrderCard from '@/components/OrderCard';
import { orderClient, updateShipperLocation } from '@/lib/api';

// ============================================================================
// 1. ĐỊNH NGHĨA TASK CHẠY NGẦM
// ============================================================================
const LOCATION_TASK_NAME = 'background-location-task';

TaskManager.defineTask(LOCATION_TASK_NAME, async ({ data, error }) => {
  if (error) {
    console.error("❌ [Background-Task] Lỗi TaskManager:", error);
    return;
  }
  if (data) {
    const { locations } = data as any;
    const lat = locations[0].coords.latitude;
    const lon = locations[0].coords.longitude;
    
    console.log(`📍 [Background-Task] Nhận tọa độ mới: ${lat}, ${lon}`);
    console.log(`🚀 [Background-Task] Đang gửi lên Server...`);
    
    try {
      await updateShipperLocation(lat, lon);
      console.log(`✅ [Background-Task] Gửi thành công!`);
    } catch (err) {
      console.error(`❌ [Background-Task] Gửi thất bại:`, err);
    }
  }
});

// Định nghĩa kiểu dữ liệu trả về từ API Backend
interface PickupTask {
  order_id: string;
  order_code: string;
  leg_status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED';
  sender_name: string;
  sender_phone: string;
  pickup_address: string;
  receiver_address: string;
}

export default function PickupScreen() {
  const router = useRouter();
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [tasks, setTasks] = useState<PickupTask[]>([]);

  // ==========================================================================
  // 2. LOGIC KÍCH HOẠT ĐỊNH VỊ
  // ==========================================================================
  useEffect(() => {
    const startLocationTracking = async () => {
      console.log("🛡️ [Tracking] Bắt đầu quy trình xin quyền...");
      try {
        // A. Xin quyền Foreground
        const { status: fgStatus } = await Location.requestForegroundPermissionsAsync();
        console.log(`🛡️ [Tracking] Quyền Foreground: ${fgStatus}`);
        
        if (fgStatus !== 'granted') {
          Alert.alert("Cần cấp quyền", "Ứng dụng cần quyền vị trí để giao hàng.");
          return;
        }

        // B. Xin quyền Background
        const { status: bgStatus } = await Location.requestBackgroundPermissionsAsync();
        console.log(`🛡️ [Tracking] Quyền Background: ${bgStatus}`);
        
        if (bgStatus !== 'granted') {
          console.log("⚠️ [Tracking] User không cấp quyền 'Allow all the time'. Chỉ chạy khi mở App.");
        }

        // C. Kiểm tra Task đã chạy chưa
        const hasStarted = await Location.hasStartedLocationUpdatesAsync(LOCATION_TASK_NAME);
        console.log(`❓ [Tracking] Task đã chạy chưa? -> ${hasStarted}`);
        
        if (!hasStarted) {
          console.log("🚀 [Tracking] Đang đăng ký Task chạy nền...");
          await Location.startLocationUpdatesAsync(LOCATION_TASK_NAME, {
            accuracy: Location.Accuracy.High,
            timeInterval: 10000,
            distanceInterval: 50,
            showsBackgroundLocationIndicator: true,
            foregroundService: {
              notificationTitle: "Shipper đang hoạt động",
              notificationBody: "Vị trí của bạn đang được theo dõi để điều phối đơn hàng.",
              notificationColor: "#2563EB",
            },
          });
          console.log("✅ [Tracking] Đăng ký thành công!");
        } else {
          console.log("ℹ️ [Tracking] Task đang chạy rồi, không cần đăng ký lại.");
        }
      } catch (e) {
        console.error("❌ [Tracking] Lỗi khởi động tracking:", e);
      }
    };

    startLocationTracking();
  }, []);

  // Hàm gọi API lấy danh sách nhiệm vụ
  const fetchTasks = async () => {
    console.log("🔄 [API] Đang lấy danh sách Pickup...");
    try {
      const res = await orderClient.get('/orders/shipper/my-pickups');
      console.log(`✅ [API] Lấy thành công ${res.data.length} đơn hàng.`);
      setTasks(res.data);
    } catch (error) {
      console.error("❌ [API] Lỗi lấy danh sách pickup:", error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useFocusEffect(
    useCallback(() => {
      console.log("👀 [Screen] PickupScreen được focus.");
      fetchTasks();
    }, [])
  );

  const onRefresh = () => {
    console.log("hz [Screen] User kéo để refresh.");
    setRefreshing(true);
    fetchTasks();
  };

  // Phân loại task
  const assignedTasks = tasks.filter(t => t.leg_status === 'IN_PROGRESS');
  const pendingTasks = tasks.filter(t => t.leg_status === 'PENDING');
  const pickedTasks = tasks.filter(t => t.leg_status === 'COMPLETED');

  // Hiển thị Loading
  if (loading && tasks.length === 0) {
    return (
      <SafeAreaView style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f9fafb' }}>
        <ActivityIndicator size="large" color="#2563EB" />
        <Text style={{ marginTop: 12, color: '#6B7280' }}>Đang tải danh sách...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{ padding: 16, paddingBottom: 100 }}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <SectionHeader
          title="Nhiệm vụ lấy hàng"
          subtitle={`${pendingTasks.length + assignedTasks.length} đơn cần xử lý hôm nay`}
        />

        {/* 1. Đang thực hiện */}
        {assignedTasks.length > 0 && (
          <View style={{ marginBottom: 24 }}>
            <View style={{ marginBottom: 12 }}>
              <Text style={{ fontSize: 14, fontWeight: '600', color: '#2563EB', marginBottom: 8 }}>
                ⏳ Đang thực hiện ({assignedTasks.length})
              </Text>
            </View>
            {assignedTasks.map((task) => (
              <OrderCard
                key={task.order_id}
                order={{
                  id: task.order_id,
                  orderCode: task.order_code,
                  status: 'assigned',
                  senderName: task.sender_name || 'Khách hàng',
                  pickupAddress: task.pickup_address,
                  distanceKm: 0,
                  timeSlot: 'Hôm nay'
                }}
                onPress={() => router.push(`/delivery/${task.order_id}`)}
              />
            ))}
          </View>
        )}

        {/* 2. Chờ xử lý */}
        {pendingTasks.length > 0 && (
          <View style={{ marginBottom: 24 }}>
            <View style={{ marginBottom: 12 }}>
              <Text style={{ fontSize: 14, fontWeight: '600', color: '#374151', marginBottom: 8 }}>
                🆕 Chờ lấy hàng ({pendingTasks.length})
              </Text>
            </View>
            {pendingTasks.map((task) => (
              <OrderCard
                key={task.order_id}
                order={{
                  id: task.order_id,
                  orderCode: task.order_code,
                  status: 'pending',
                  senderName: task.sender_name || 'Khách hàng',
                  pickupAddress: task.pickup_address,
                  distanceKm: 0,
                  timeSlot: 'Hôm nay'
                }}
                onPress={() => router.push(`/delivery/${task.order_id}`)}
              />
            ))}
          </View>
        )}

        {/* 3. Đã hoàn thành */}
        {pickedTasks.length > 0 && (
          <View style={{ marginBottom: 24 }}>
            <View style={{ marginBottom: 12 }}>
              <Text style={{ fontSize: 14, fontWeight: '600', color: '#10B981', marginBottom: 8 }}>
                ✅ Đã lấy xong ({pickedTasks.length})
              </Text>
            </View>
            {pickedTasks.map((task) => (
              <OrderCard
                key={task.order_id}
                order={{
                  id: task.order_id,
                  orderCode: task.order_code,
                  status: 'picked',
                  senderName: task.sender_name || 'Khách hàng',
                  pickupAddress: task.pickup_address,
                  distanceKm: 0,
                  timeSlot: 'Hoàn tất'
                }}
                onPress={() => router.push(`/delivery/${task.order_id}`)}
              />
            ))}
          </View>
        )}

        {/* Empty State */}
        {tasks.length === 0 && (
          <View style={{ alignItems: 'center', marginTop: 60 }}>
            <Text style={{ fontSize: 40, marginBottom: 10 }}>📦</Text>
            <Text style={{ color: '#6B7280', fontSize: 16 }}>Chưa có nhiệm vụ nào.</Text>
            <Text style={{ color: '#9CA3AF', fontSize: 14, marginTop: 4 }}>Kéo xuống để làm mới</Text>
          </View>
        )}

      </ScrollView>
    </SafeAreaView>
  );
}