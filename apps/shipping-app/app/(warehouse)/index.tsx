import React from 'react';
import { View, Text, StyleSheet, FlatList } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

export default function WarehouseScheduleScreen() {
  // Mock data - Sau này bạn sẽ gọi API lấy danh sách việc cần làm
  const tasks = [
    { id: '1', title: 'Nhập kho lô hàng A1', status: 'PENDING', time: '08:00' },
    { id: '2', title: 'Xuất kho đơn ORD-123', status: 'COMPLETED', time: '09:30' },
    { id: '3', title: 'Kiểm kê khu vực B', status: 'PENDING', time: '14:00' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Lịch làm việc kho</Text>
        <Text style={styles.subtitle}>Danh sách nhiệm vụ hôm nay</Text>
      </View>

      <FlatList
        data={tasks}
        keyExtractor={(item) => item.id}
        contentContainerStyle={{ padding: 16 }}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <View>
              <Text style={styles.taskTitle}>{item.title}</Text>
              <Text style={styles.taskTime}>{item.time}</Text>
            </View>
            <View style={[
              styles.badge, 
              { backgroundColor: item.status === 'COMPLETED' ? '#D1FAE5' : '#FEF3C7' }
            ]}>
              <Text style={[
                styles.badgeText,
                { color: item.status === 'COMPLETED' ? '#065F46' : '#92400E' }
              ]}>
                {item.status === 'COMPLETED' ? 'Đã xong' : 'Chờ xử lý'}
              </Text>
            </View>
          </View>
        )}
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  header: { padding: 24, backgroundColor: '#fff', borderBottomWidth: 1, borderColor: '#E5E7EB' },
  title: { fontSize: 24, fontWeight: 'bold', color: '#111827' },
  subtitle: { fontSize: 14, color: '#6B7280', marginTop: 4 },
  card: {
    backgroundColor: '#fff',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  taskTitle: { fontSize: 16, fontWeight: '600', color: '#111827' },
  taskTime: { fontSize: 14, color: '#6B7280', marginTop: 4 },
  badge: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 16 },
  badgeText: { fontSize: 12, fontWeight: '600' },
});