import React, { useEffect, useState } from 'react';
import { View, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { Tabs } from 'expo-router';
import { Package, Truck, Scan, User } from 'lucide-react-native';
import { usePushNotifications } from "../hooks/usePushNotifications"; 
import { registerDeviceToken, getShipperProfile } from '@/lib/api'; // <--- Đảm bảo đã có hàm getShipperProfile trong api.ts
import IncidentModal from '@/components/IncidentModal'; 

export default function TabLayout() {
  const token = usePushNotifications();
  const [modalVisible, setModalVisible] = useState(false);
  
  // State để lưu Shipper ID thật
  const [currentShipperId, setCurrentShipperId] = useState<string>(""); 

  // Hàm lấy thông tin Shipper từ Server
  const fetchShipperInfo = async () => {
    try {
      const profile = await getShipperProfile();
      console.log("👤 Thông tin Shipper nhận được:", profile);
      
      // ⚠️ QUAN TRỌNG: Kiểm tra log xem field chứa ID tên là gì?
      // Thường là 'shipper_id', 'id', hoặc 'user_id'. 
      // Ở đây đang giả định là 'shipper_id'
      if (profile && profile.shipper_id) {
        setCurrentShipperId(profile.shipper_id);
      } else if (profile && profile.id) {
        // Fallback nếu backend trả về là 'id'
        setCurrentShipperId(profile.id);
      }
    } catch (error) {
      console.log("❌ Lỗi lấy profile:", error);
    }
  };

  useEffect(() => {
    // 1. Lấy thông tin shipper ngay khi vào Tabs
    fetchShipperInfo();

    // 2. Gửi FCM Token nếu có
    if (token) {
      registerDeviceToken(token); 
    }
  }, [token]);

  return (
    <View style={{ flex: 1 }}>
      <Tabs
        screenOptions={{
          tabBarActiveTintColor: '#2563EB',
          tabBarInactiveTintColor: '#9CA3AF',
          tabBarStyle: {
            backgroundColor: '#FFFFFF',
            borderTopWidth: 1,
            borderTopColor: '#E5E7EB',
            height: 60,
            paddingBottom: 8,
            paddingTop: 8,
          },
          tabBarLabelStyle: {
            fontSize: 12,
            fontWeight: '600',
          },
          headerShown: false,
        }}
      >
        <Tabs.Screen
          name="pickup"
          options={{
            title: 'Pickup',
            tabBarIcon: ({ color, size }) => ( <Package size={size} color={color} /> ),
          }}
        />
        <Tabs.Screen
          name="delivery"
          options={{
            title: 'Delivery',
            tabBarIcon: ({ color, size }) => ( <Truck size={size} color={color} /> ),
          }}
        />
        <Tabs.Screen
          name="scan"
          options={{
            title: 'Scan',
            tabBarIcon: ({ color, size }) => ( <Scan size={size} color={color} /> ),
          }}
        />
        <Tabs.Screen
          name="profile"
          options={{
            title: 'Profile',
            tabBarIcon: ({ color, size }) => ( <User size={size} color={color} /> ),
          }}
        />
      </Tabs>

      {/* Chỉ hiện nút SOS khi đã lấy được ID (tránh lỗi gửi ID rỗng) */}
      {currentShipperId ? (
        <TouchableOpacity
          onPress={() => setModalVisible(true)}
          style={styles.fab}
          activeOpacity={0.8}
        >
          <Text style={styles.fabText}>🆘</Text>
        </TouchableOpacity>
      ) : null}

      <IncidentModal 
        visible={modalVisible} 
        onClose={() => setModalVisible(false)}
        shipperId={currentShipperId} // <--- Truyền ID thật vào đây
      />
    </View>
  );
}

const styles = StyleSheet.create({
  fab: {
    position: 'absolute',
    bottom: 80,
    right: 20,
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#DC2626',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4.65,
    elevation: 8,
    zIndex: 999,
    borderWidth: 2,
    borderColor: 'white',
  },
  fabText: {
    fontSize: 24,
  }
});