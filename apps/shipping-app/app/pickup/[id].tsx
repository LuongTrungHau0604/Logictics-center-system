import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useLocalSearchParams, useRouter } from 'expo-router';
import * as SecureStore from 'expo-secure-store'; // [NEW] Để lấy token
import { jwtDecode } from 'jwt-decode'; // [NEW] Để giải mã token
import { 
  MapPin, 
  Phone, 
  Package, 
  Clock,
  Navigation,
  CheckCircle2,
  Lock // Icon cho màn hình chặn
} from 'lucide-react-native';
import StatusBadge from '@/components/StatusBadge';
import ActionButton from '@/components/ActionButton';
import { pickupTasks } from '@/lib/mockOrders';

// Định nghĩa kiểu dữ liệu cho Token Payload
interface TokenPayload {
  sub: string;
  role: 'SHIPPER' | 'WAREHOUSE_STAFF' | string;
  user_id: number;
  exp: number;
}

export default function PickupDetailScreen() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  
  // [NEW] State để kiểm tra quyền
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [userRole, setUserRole] = useState<string | null>(null);

  const order = pickupTasks.find(o => o.id === id);

  // [NEW] Logic kiểm tra Role khi vào màn hình
  useEffect(() => {
    const checkPermission = async () => {
      try {
        const token = await SecureStore.getItemAsync('access_token');
        
        if (!token) {
          Alert.alert('Lỗi', 'Bạn chưa đăng nhập');
          router.replace('/'); // Về trang login
          return;
        }

        const decoded = jwtDecode<TokenPayload>(token);
        setUserRole(decoded.role);

        // Nếu là WAREHOUSE_STAFF, xử lý riêng (hoặc đẩy về trang khác)
        if (decoded.role === 'WAREHOUSE_STAFF') {
           // Logic cho kho (làm sau)
           // Ví dụ: router.replace('/warehouse/dashboard');
        }

      } catch (error) {
        console.error('Lỗi xác thực:', error);
        router.replace('/');
      } finally {
        setIsCheckingAuth(false);
      }
    };

    checkPermission();
  }, []);

  // [NEW] Màn hình Loading khi đang check quyền
  if (isCheckingAuth) {
    return (
      <SafeAreaView style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#2563EB" />
        <Text style={{ marginTop: 12, color: '#6B7280' }}>Đang kiểm tra quyền truy cập...</Text>
      </SafeAreaView>
    );
  }

  // [NEW] Màn hình chặn nếu là WAREHOUSE_STAFF (Vì chưa làm chức năng này)
  if (userRole === 'WAREHOUSE_STAFF') {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center', padding: 24 }}>
        <View style={{ width: 80, height: 80, backgroundColor: '#fee2e2', borderRadius: 40, justifyContent: 'center', alignItems: 'center', marginBottom: 16 }}>
          <Lock size={40} color="#ef4444" />
        </View>
        <Text style={{ fontSize: 20, fontWeight: 'bold', color: '#1f2937', textAlign: 'center', marginBottom: 8 }}>
          Khu vực giới hạn
        </Text>
        <Text style={{ fontSize: 16, color: '#4b5563', textAlign: 'center', marginBottom: 24 }}>
          Màn hình này dành riêng cho Shipper. Tài khoản Kho chưa được hỗ trợ tại đây.
        </Text>
        <TouchableOpacity 
          onPress={() => router.back()}
          style={{ backgroundColor: '#2563EB', paddingHorizontal: 24, paddingVertical: 12, borderRadius: 8 }}
        >
          <Text style={{ color: '#fff', fontWeight: '600' }}>Quay lại</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  // --- Logic cũ của Shipper ---

  if (!order) {
    return (
      <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb', justifyContent: 'center', alignItems: 'center' }}>
        <Text style={{ color: '#4b5563' }}>Đơn hàng không tồn tại</Text>
      </SafeAreaView>
    );
  }

  const handleStartPickup = () => {
    Alert.alert(
      'Bắt đầu lấy hàng',
      'Điều hướng đến vị trí lấy hàng?',
      [
        { text: 'Hủy', style: 'cancel' },
        { 
          text: 'Đi ngay', 
          onPress: () => Alert.alert('Điều hướng', 'Đang mở bản đồ...')
        }
      ]
    );
  };

  const handleScanPackage = () => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      Alert.alert(
        'Thành công',
        'Đã xác nhận lấy hàng!',
        [
          { text: 'OK', onPress: () => router.back() }
        ]
      );
    }, 1500);
  };

  const handleCallSender = () => {
    Alert.alert('Gọi người gửi', `Đang gọi ${order.senderPhone}...`);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {/* Order Header */}
        <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 24, marginBottom: 16 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 28, fontWeight: '700', color: '#111827', marginBottom: 8 }}>
                {order.orderCode}
              </Text>
              <StatusBadge status={order.status} />
            </View>
          </View>

          {/* Package Info */}
          <View style={{ backgroundColor: '#f3f4f6', borderRadius: 8, padding: 16, marginTop: 16 }}>
            <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 8 }}>
              <Package size={16} {...({ stroke: '#6B7280' } as any)} />
              <Text style={{ fontSize: 14, color: '#4b5563', marginLeft: 8 }}>Chi tiết gói hàng</Text>
            </View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 8 }}>
              <Text style={{ color: '#374151' }}>Khối lượng:</Text>
              <Text style={{ fontWeight: '600', color: '#111827' }}>{order.weight} kg</Text>
            </View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 }}>
              <Text style={{ color: '#374151' }}>Loại hàng:</Text>
              <Text style={{ fontWeight: '600', color: '#111827' }}>{order.packageType}</Text>
            </View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginTop: 4 }}>
              <Text style={{ color: '#374151' }}>Khoảng cách:</Text>
              <Text style={{ fontWeight: '600', color: '#111827' }}>{order.distanceKm} km</Text>
            </View>
          </View>
        </View>

        {/* Sender Information */}
        <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 24, marginBottom: 16 }}>
          <Text style={{ fontSize: 18, fontWeight: '700', color: '#111827', marginBottom: 16 }}>
            Thông tin người gửi
          </Text>
          
          <View style={{ gap: 12 }}>
            <View style={{ flexDirection: 'row', alignItems: 'flex-start' }}>
              <View style={{ backgroundColor: '#dbeafe', borderRadius: 50, padding: 8, marginRight: 12 }}>
                <MapPin size={16} {...({ stroke: '#2563EB' } as any)} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 14, color: '#4b5563', marginBottom: 4 }}>Địa chỉ lấy hàng</Text>
                <Text style={{ fontSize: 16, color: '#111827', fontWeight: '500' }}>
                  {order.pickupAddress}
                </Text>
              </View>
            </View>

            <View style={{ flexDirection: 'row', alignItems: 'flex-start' }}>
              <View style={{ backgroundColor: '#d1fae5', borderRadius: 50, padding: 8, marginRight: 12 }}>
                <Phone size={16} {...({ stroke: '#10B981' } as any)} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 14, color: '#4b5563', marginBottom: 4 }}>Liên hệ</Text>
                <Text style={{ fontSize: 16, color: '#111827', fontWeight: '500' }}>
                  {order.senderName}
                </Text>
                <Text style={{ fontSize: 14, color: '#4b5563' }}>{order.senderPhone}</Text>
              </View>
            </View>

            <View style={{ flexDirection: 'row', alignItems: 'flex-start' }}>
              <View style={{ backgroundColor: '#fef3c7', borderRadius: 50, padding: 8, marginRight: 12 }}>
                <Clock size={16} {...({ stroke: '#F59E0B' } as any)} />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 14, color: '#4b5563', marginBottom: 4 }}>Giờ lấy hàng</Text>
                <Text style={{ fontSize: 16, color: '#111827', fontWeight: '500' }}>
                  {order.pickupTime}
                </Text>
              </View>
            </View>
          </View>

          {/* Call Button */}
          <TouchableOpacity
            onPress={handleCallSender}
            style={{ backgroundColor: '#f0fdf4', borderWidth: 1, borderColor: '#bbf7d0', borderRadius: 12, paddingVertical: 12, marginTop: 16, flexDirection: 'row', justifyContent: 'center', alignItems: 'center' }}
            activeOpacity={0.7}
          >
            <Phone size={18} {...({ stroke: '#10B981' } as any)} />
            <Text style={{ color: '#10B981', fontWeight: '600', marginLeft: 8 }}>Gọi người gửi</Text>
          </TouchableOpacity>
        </View>

        {/* Special Notes */}
        {order.notes && (
          <View style={{ backgroundColor: '#fef3c7', borderWidth: 1, borderColor: '#fde047', borderRadius: 12, padding: 16, marginBottom: 16 }}>
            <Text style={{ fontSize: 14, fontWeight: '600', color: '#854d0e', marginBottom: 4 }}>
              ⚠️ Lưu ý đặc biệt
            </Text>
            <Text style={{ fontSize: 14, color: '#92400e' }}>{order.notes}</Text>
          </View>
        )}

        {/* Action Buttons */}
        <View style={{ gap: 12, marginBottom: 24 }}>
          {order.status === 'assigned' && (
            <>
              <ActionButton
                label="Dẫn đường"
                onPress={handleStartPickup}
                icon={Navigation}
                variant="primary"
              />
              <ActionButton
                label="Quét & Xác nhận lấy hàng"
                onPress={handleScanPackage}
                icon={CheckCircle2}
                variant="success"
                loading={loading}
              />
            </>
          )}
          
          {order.status === 'picked' && (
            <View style={{ backgroundColor: '#f0fdf4', borderWidth: 1, borderColor: '#bbf7d0', borderRadius: 12, padding: 16 }}>
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                <CheckCircle2 size={20} {...({ stroke: '#10B981' } as any)} />
                <Text style={{ color: '#10B981', fontWeight: '600', marginLeft: 8 }}>
                  Đã lấy hàng thành công
                </Text>
              </View>
              <Text style={{ fontSize: 14, color: '#4b5563', marginTop: 8 }}>
                Gói hàng này đã được lấy và sẵn sàng để giao.
              </Text>
            </View>
          )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}