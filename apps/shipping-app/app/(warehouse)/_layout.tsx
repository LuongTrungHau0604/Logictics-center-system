import { Tabs } from 'expo-router';
import { Calendar, Scan, LogOut } from 'lucide-react-native'; // Import icon phù hợp
import { TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';

export default function WarehouseLayout() {
  const router = useRouter();

  const handleLogout = () => {
    // Xử lý logout đơn giản, quay về login
    router.replace('/login');
  };

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#2563EB', // Màu xanh chủ đạo
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
      {/* Tab 1: Lịch làm việc (Màn hình chính của Kho) */}
      <Tabs.Screen
        name="index"
        options={{
          title: 'Lịch làm việc',
          tabBarIcon: ({ color, size }) => (
            <Calendar size={size} stroke={color} />
          ),
        }}
      />

      {/* Tab 2: Quét mã */}
      <Tabs.Screen
        name="scan"
        options={{
          title: 'Quét mã',
          tabBarIcon: ({ color, size }) => (
            <Scan size={size} stroke={color} />
          ),
        }}
      />
      
      {/* Nút logout giả lập (Optional) - Có thể để trong Profile nếu muốn */}
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Tài khoản',
          tabBarIcon: ({ color, size }) => (
            <LogOut size={size} stroke={color} />
          ),
        }}
        listeners={() => ({
          tabPress: (e) => {
            e.preventDefault();
            handleLogout();
          },
        })}
      />
    </Tabs>
  );
}