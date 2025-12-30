import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Linking, Alert, ActivityIndicator } from 'react-native';
import { useLocalSearchParams, useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ArrowLeft, Phone, Package, MapPin, ClipboardList, CheckCircle } from 'lucide-react-native';
import { completeDeliveryOrder } from '@/lib/api'; 

export default function OrderDetailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();

  // Lấy params
  const id = params.id as string; 
  const code = params.code as string || '---';
  const name = params.name as string || 'Khách hàng';
  const phone = params.phone as string || '';
  const address = params.address as string || 'Chưa có địa chỉ';
  const weight = params.weight ? String(params.weight) : '0';
  const note = params.note as string || '';
  const status = params.status as string || 'PENDING';

  const [loading, setLoading] = useState(false);

  const handleCall = () => {
    if (phone) Linking.openURL(`tel:${phone}`);
  };

  const handleCompleteDelivery = async () => {
    if (status === 'COMPLETED') {
        Alert.alert("Thông báo", "Đơn hàng này đã hoàn thành rồi.");
        return;
    }

    Alert.alert(
      "Xác nhận giao hàng",
      "Bạn chắc chắn đã giao kiện hàng này thành công?",
      [
        { text: "Hủy", style: "cancel" },
        { 
          text: "Đồng ý", 
          onPress: async () => {
            setLoading(true);
            try {
              await completeDeliveryOrder(id);
              Alert.alert("Thành công", "Cập nhật trạng thái thành công!", [
                { text: "OK", onPress: () => router.back() } 
              ]);
            } catch (error: any) {
              Alert.alert("Lỗi", error.message || "Không thể cập nhật đơn hàng.");
            } finally {
              setLoading(false);
            }
          } 
        }
      ]
    );
  };

  const isCompleted = status === 'COMPLETED';

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
          <ArrowLeft size={24} color="#333" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Chi tiết đơn hàng</Text>
        <View style={{ width: 40 }} />
      </View>

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.statusContainer}>
             <View style={[styles.badge, isCompleted ? styles.badgeSuccess : styles.badgePending]}>
                <Text style={[styles.badgeText, isCompleted ? styles.textSuccess : styles.textPending]}>
                    {isCompleted ? 'ĐÃ GIAO XONG' : 'ĐANG GIAO HÀNG'}
                </Text>
             </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Thông tin người nhận</Text>
          <View style={styles.row}>
            <View style={styles.iconBox}><Text style={{ fontSize: 20 }}>👤</Text></View>
            <View style={styles.infoText}>
              <Text style={styles.label}>Họ và tên</Text>
              <Text style={styles.value}>{name}</Text>
            </View>
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <View style={styles.iconBox}><Phone size={20} color="#2563EB" /></View>
            <View style={styles.infoText}>
              <Text style={styles.label}>Số điện thoại</Text>
              <Text style={styles.value}>{phone}</Text>
            </View>
            {phone ? (
              <TouchableOpacity style={styles.callButton} onPress={handleCall}>
                <Text style={styles.callButtonText}>Gọi ngay</Text>
              </TouchableOpacity>
            ) : null}
          </View>
          <View style={styles.divider} />
          <View style={styles.row}>
            <View style={styles.iconBox}><MapPin size={20} color="#EF4444" /></View>
            <View style={styles.infoText}>
              <Text style={styles.label}>Địa chỉ giao hàng</Text>
              <Text style={styles.value}>{address}</Text>
            </View>
          </View>
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Thông tin kiện hàng</Text>
          <View style={styles.row}>
            <Package size={20} color="#6B7280" style={{ marginRight: 12 }} />
            <Text style={styles.label}>Mã đơn hàng:</Text>
            <Text style={[styles.value, { marginLeft: 'auto', fontWeight: 'bold' }]}>{code}</Text>
          </View>
          <View style={[styles.row, { marginTop: 12 }]}>
            <View style={{ width: 20, marginRight: 12 }} /> 
            <Text style={styles.label}>Cân nặng:</Text>
            <Text style={[styles.value, { marginLeft: 'auto' }]}>{weight} kg</Text>
          </View>
        </View>

        {note ? (
          <View style={styles.card}>
            <View style={styles.row}>
              <ClipboardList size={20} color="#F59E0B" style={{ marginRight: 12 }} />
              <Text style={styles.sectionTitle}>Ghi chú</Text>
            </View>
            <Text style={styles.noteText}>{note}</Text>
          </View>
        ) : null}
      </ScrollView>

      {!isCompleted && (
          <View style={styles.footer}>
            <TouchableOpacity 
                style={[styles.completeButton, loading && { opacity: 0.7 }]} 
                onPress={handleCompleteDelivery}
                disabled={loading}
            >
              {loading ? <ActivityIndicator color="#fff" /> : (
                  <>
                    <CheckCircle size={20} color="#fff" style={{ marginRight: 8 }} />
                    <Text style={styles.completeButtonText}>Xác nhận giao thành công</Text>
                  </>
              )}
            </TouchableOpacity>
          </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F3F4F6' },
  header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 16, paddingVertical: 12, backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#E5E7EB' },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#111827' },
  backButton: { padding: 8 },
  content: { padding: 16 },
  statusContainer: { marginBottom: 16, alignItems: 'center' },
  badge: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20 },
  badgePending: { backgroundColor: '#DBEAFE' },
  badgeSuccess: { backgroundColor: '#D1FAE5' },
  badgeText: { fontSize: 12, fontWeight: 'bold' },
  textPending: { color: '#1E40AF' },
  textSuccess: { color: '#065F46' },
  card: { backgroundColor: '#fff', borderRadius: 12, padding: 16, marginBottom: 16, shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 5, elevation: 2 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#374151', marginBottom: 12 },
  row: { flexDirection: 'row', alignItems: 'center' },
  iconBox: { width: 36, height: 36, borderRadius: 18, backgroundColor: '#F3F4F6', alignItems: 'center', justifyContent: 'center', marginRight: 12 },
  infoText: { flex: 1 },
  label: { fontSize: 12, color: '#6B7280', marginBottom: 2 },
  value: { fontSize: 15, color: '#111827', fontWeight: '500', lineHeight: 20 },
  divider: { height: 1, backgroundColor: '#F3F4F6', marginVertical: 12 },
  callButton: { backgroundColor: '#EFF6FF', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, borderWidth: 1, borderColor: '#BFDBFE' },
  callButtonText: { color: '#2563EB', fontWeight: '600', fontSize: 12 },
  noteText: { marginTop: 4, color: '#4B5563', fontStyle: 'italic', lineHeight: 20 },
  footer: { padding: 16, backgroundColor: '#fff', borderTopWidth: 1, borderTopColor: '#E5E7EB' },
  completeButton: { backgroundColor: '#10B981', paddingVertical: 14, borderRadius: 10, alignItems: 'center', flexDirection: 'row', justifyContent: 'center' },
  completeButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
});