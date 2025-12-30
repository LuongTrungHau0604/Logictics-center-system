import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { Eye, EyeOff, User, Lock } from 'lucide-react-native'; // Đổi Phone thành User
import { loginAPI } from '../lib/api';

export default function LoginScreen() {
  const router = useRouter();
  // Đổi state từ phoneNumber sang username để chứa được cả email hoặc tên đăng nhập
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username.trim() || !password.trim()) {
      Alert.alert('Lỗi', 'Vui lòng điền đầy đủ thông tin đăng nhập');
      return;
    }

    setLoading(true);
    
    try {
      console.log('⏳ Đang gọi API Login...');
      const data = await loginAPI(username, password);
      
      console.log('✅ API Login thành công:', data);
      
      // Lấy role và chuẩn hóa (viết hoa hết, cắt khoảng trắng thừa nếu có)
      const userRole = data.user?.role ? data.user.role.trim().toUpperCase() : '';
      console.log('👤 Role phát hiện:', userRole);

      if (userRole === 'SHIPPER') {
        // SỬA LỖI: Chỉ chuyển trang KHI người dùng bấm OK trên Alert
        Alert.alert(
          'Thành công', 
          `Xin chào Shipper, ${data.user.username}`,
          [
            { 
              text: 'OK', 
              onPress: () => {
                console.log('🔄 Đang chuyển sang trang Delivery...');
                router.replace('/(tabs)/delivery'); 
              }
            }
          ]
        );
      } 
      else if (userRole === 'WAREHOUSE_STAFF') {
        Alert.alert('Thành công', `Xin chào nhân viên kho, ${data.user.username}`, [
            { 
              text: 'OK', 
              // Điều hướng sang layout Warehouse mới tạo
              onPress: () => router.replace('/(warehouse)') 
            }
        ]);
      } 
      else {
        console.log('❌ Role không hợp lệ:', userRole);
        Alert.alert('Lỗi', `Quyền truy cập không xác định: ${userRole}`);
      }
      
    } catch (error: any) {
      console.error('❌ Login Error:', error);
      Alert.alert('Đăng nhập thất bại', error.message || 'Vui lòng kiểm tra lại kết nối.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#2563EB' }}>
      <ScrollView
        style={{ flex: 1 }}
        contentContainerStyle={{ flexGrow: 1, justifyContent: 'center', paddingHorizontal: 24 }}
        showsVerticalScrollIndicator={false}
      >
        {/* Logo Section */}
        <View style={{ alignItems: 'center', marginBottom: 48 }}>
          <View
            style={{
              width: 100,
              height: 100,
              backgroundColor: '#fff',
              borderRadius: 50,
              justifyContent: 'center',
              alignItems: 'center',
              marginBottom: 24,
            }}
          >
            <Text style={{ fontSize: 48, fontWeight: '700', color: '#2563EB' }}>AI</Text>
          </View>
          <Text style={{ fontSize: 28, fontWeight: '700', color: '#fff', marginBottom: 8 }}>
            Shipper App
          </Text>
          <Text style={{ fontSize: 16, color: 'rgba(255, 255, 255, 0.8)', textAlign: 'center' }}>
            Quản lý giao hàng dễ dàng
          </Text>
        </View>

        {/* Form Section */}
        <View style={{ backgroundColor: '#fff', borderRadius: 16, padding: 24, marginBottom: 24 }}>
          
          {/* Username/Email Input */}
          <View style={{ marginBottom: 16 }}>
            <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>
              Tên đăng nhập / Email
            </Text>
            <View
              style={{
                flexDirection: 'row',
                alignItems: 'center',
                backgroundColor: '#f9fafb',
                borderWidth: 1,
                borderColor: '#E5E7EB',
                borderRadius: 8,
                paddingHorizontal: 12,
              }}
            >
              {/* Dùng icon User thay vì Phone */}
              <User size={20} {...({ stroke: '#9CA3AF' } as any)} style={{ marginRight: 8 }} />
              <TextInput
                placeholder="Nhập username hoặc email"
                // Dùng email-address để tiện nhập liệu, tắt autoCapitalize để user không bị sai format
                keyboardType="email-address"
                autoCapitalize="none"
                value={username}
                onChangeText={setUsername}
                editable={!loading}
                style={{
                  flex: 1,
                  paddingVertical: 12,
                  fontSize: 14,
                  color: '#111827',
                }}
                placeholderTextColor="#9CA3AF"
              />
            </View>
          </View>

          {/* Password Input */}
          <View style={{ marginBottom: 24 }}>
            <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>
              Mật khẩu
            </Text>
            <View
              style={{
                flexDirection: 'row',
                alignItems: 'center',
                backgroundColor: '#f9fafb',
                borderWidth: 1,
                borderColor: '#E5E7EB',
                borderRadius: 8,
                paddingHorizontal: 12,
              }}
            >
              <Lock size={20} {...({ stroke: '#9CA3AF' } as any)} style={{ marginRight: 8 }} />
              <TextInput
                placeholder="Nhập mật khẩu"
                secureTextEntry={!showPassword}
                value={password}
                onChangeText={setPassword}
                editable={!loading}
                style={{
                  flex: 1,
                  paddingVertical: 12,
                  fontSize: 14,
                  color: '#111827',
                }}
                placeholderTextColor="#9CA3AF"
              />
              <TouchableOpacity onPress={() => setShowPassword(!showPassword)} disabled={loading}>
                {showPassword ? (
                  <EyeOff size={20} {...({ stroke: '#9CA3AF' } as any)} />
                ) : (
                  <Eye size={20} {...({ stroke: '#9CA3AF' } as any)} />
                )}
              </TouchableOpacity>
            </View>
          </View>

          {/* Login Button */}
          <TouchableOpacity
            onPress={handleLogin}
            disabled={loading}
            style={{
              backgroundColor: '#2563EB',
              borderRadius: 8,
              paddingVertical: 14,
              alignItems: 'center',
              opacity: loading ? 0.6 : 1,
            }}
            activeOpacity={0.8}
          >
            <Text style={{ color: '#fff', fontWeight: '600', fontSize: 16 }}>
              {loading ? 'Đang xác thực...' : 'Đăng nhập'}
            </Text>
          </TouchableOpacity>

          {/* Forgot Password Link */}
          <TouchableOpacity
            style={{ marginTop: 16, alignItems: 'center' }}
            disabled={loading}
          >
            <Text style={{ color: '#2563EB', fontWeight: '500', fontSize: 14 }}>
              Quên mật khẩu?
            </Text>
          </TouchableOpacity>
        </View>

        {/* Info Section */}
        <View style={{ backgroundColor: 'rgba(255, 255, 255, 0.15)', borderRadius: 12, padding: 16 }}>
          <Text style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: 13, lineHeight: 20 }}>
            💡 <Text style={{ fontWeight: '600' }}>Lưu ý:</Text> Bạn có thể đăng nhập bằng Tên đăng nhập (Username) hoặc Email đã đăng ký.
          </Text>
        </View>

        {/* Footer */}
        <View style={{ marginTop: 32, alignItems: 'center' }}>
          <Text style={{ color: 'rgba(255, 255, 255, 0.7)', fontSize: 13 }}>
            AI Transport Center © 2024
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}