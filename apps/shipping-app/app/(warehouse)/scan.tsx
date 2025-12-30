import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Alert, StyleSheet, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { CameraView, useCameraPermissions } from 'expo-camera'; // Thư viện Camera mới
import { useRouter } from 'expo-router';
import { orderClient } from '@/lib/api'; //

export default function ScanScreen() {
  const router = useRouter();
  const [permission, requestPermission] = useCameraPermissions();
  const [scanned, setScanned] = useState(false);
  const [loading, setLoading] = useState(false);

  // Xin quyền Camera khi vào màn hình
  useEffect(() => {
    if (!permission?.granted) {
      requestPermission();
    }
  }, [permission]);

  // Hàm xử lý khi quét được mã
  const handleBarCodeScanned = async ({ type, data }: { type: string; data: string }) => {
    if (scanned || loading) return; // Chặn quét liên tục
    
    setScanned(true); // Khóa quét
    setLoading(true);

    try {
      console.log(`📦 Đã quét mã: ${data}`);

      // Gọi API Backend
      const response = await orderClient.post('/journey/scan', {
        code_value: data
      });

      const result = response.data;

      // Hiển thị thông báo thành công
      Alert.alert(
        'Thành công',
        `${result.message}\nTrạng thái mới: ${result.new_order_status}`,
        [
          {
            text: 'OK',
            onPress: () => {
              setScanned(false);
              setLoading(false);
            }
          }
        ]
      );

    } catch (error: any) {
      console.error("Lỗi quét mã:", error);
      Alert.alert(
        'Lỗi',
        error.response?.data?.detail || 'Không thể xử lý mã này.',
        [
          { 
            text: 'Quét lại', 
            onPress: () => {
              setScanned(false);
              setLoading(false);
            } 
          }
        ]
      );
    }
  };

  // Màn hình chờ cấp quyền
  if (!permission) {
    return <View style={styles.container} />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.container}>
        <Text style={{ color: '#fff', textAlign: 'center', marginBottom: 20 }}>
          Cần cấp quyền Camera để quét mã hàng.
        </Text>
        <TouchableOpacity onPress={requestPermission} style={styles.button}>
          <Text style={styles.buttonText}>Cấp quyền</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>Quét mã đơn hàng</Text>
        <Text style={styles.subtitle}>Di chuyển camera vào mã vạch trên gói hàng</Text>
      </View>

      <View style={styles.cameraContainer}>
        <CameraView
          style={styles.camera}
          onBarcodeScanned={scanned ? undefined : handleBarCodeScanned}
          barcodeScannerSettings={{
            barcodeTypes: ["qr", "code128", "ean13"], // Các loại mã hỗ trợ
          }}
        >
          {/* Khung nhắm ảo để người dùng căn chỉnh */}
          <View style={styles.overlay}>
            <View style={styles.unfocusedContainer} />
            <View style={styles.middleContainer}>
              <View style={styles.unfocusedContainer} />
              <View style={styles.focusedContainer} />
              <View style={styles.unfocusedContainer} />
            </View>
            <View style={styles.unfocusedContainer} />
          </View>
        </CameraView>
        
        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#2563EB" />
            <Text style={{ color: '#fff', marginTop: 10 }}>Đang xử lý...</Text>
          </View>
        )}
      </View>

      <View style={styles.footer}>
        <TouchableOpacity 
          style={[styles.button, scanned && { backgroundColor: '#6B7280' }]}
          onPress={() => setScanned(false)}
          disabled={!scanned}
        >
          <Text style={styles.buttonText}>
            {scanned ? 'Nhấn để quét tiếp' : 'Đang tìm mã...'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#111827',
  },
  header: {
    padding: 24,
    alignItems: 'center',
  },
  title: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
    marginBottom: 8,
  },
  subtitle: {
    color: 'rgba(255, 255, 255, 0.7)',
    fontSize: 14,
  },
  cameraContainer: {
    flex: 1,
    overflow: 'hidden',
    borderRadius: 24,
    marginHorizontal: 16,
    marginBottom: 16,
  },
  camera: {
    flex: 1,
  },
  footer: {
    padding: 24,
    alignItems: 'center',
  },
  button: {
    backgroundColor: '#2563EB',
    paddingVertical: 16,
    paddingHorizontal: 48,
    borderRadius: 12,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  // Styles cho khung nhắm
  overlay: {
    flex: 1,
    backgroundColor: 'transparent',
  },
  unfocusedContainer: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
  },
  middleContainer: {
    flexDirection: 'row',
    flex: 1.5,
  },
  focusedContainer: {
    flex: 6,
    borderWidth: 2,
    borderColor: '#2563EB',
    backgroundColor: 'transparent',
  },
  loadingOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(0,0,0,0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  }
});