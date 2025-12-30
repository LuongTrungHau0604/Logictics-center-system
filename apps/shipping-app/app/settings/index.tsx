import React, { useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, TextInput, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { ChevronLeft, Eye, EyeOff, Lock, Phone } from 'lucide-react-native';

export default function SettingsScreen() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'password' | 'phone'>('password');
  const [showPassword, setShowPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  
  // Password state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  // Phone state
  const [phoneNumber, setPhoneNumber] = useState('0987654321');
  const [phoneOtp, setPhoneOtp] = useState('');
  const [phoneOtpSent, setPhoneOtpSent] = useState(false);
  const [phoneOtpVerified, setPhoneOtpVerified] = useState(false);

  // Password OTP state
  const [passwordOtp, setPasswordOtp] = useState('');
  const [passwordOtpSent, setPasswordOtpSent] = useState(false);
  const [passwordOtpVerified, setPasswordOtpVerified] = useState(false);

  const handleSendPhoneOtp = () => {
    if (!phoneNumber.trim()) {
      Alert.alert('Error', 'Vui lòng nhập số điện thoại');
      return;
    }
    setPhoneOtpSent(true);
    Alert.alert('Success', `OTP đã được gửi đến ${phoneNumber}\nSử dụng OTP: 123456`);
  };

  const handleVerifyPhoneOtp = () => {
    if (!phoneOtp.trim()) {
      Alert.alert('Error', 'Vui lòng nhập OTP');
      return;
    }
    if (phoneOtp === '123456') {
      setPhoneOtpVerified(true);
      Alert.alert('Success', 'OTP xác minh thành công!');
    } else {
      Alert.alert('Error', 'OTP không chính xác');
    }
  };

  const handleUpdatePhone = () => {
    if (!phoneOtpVerified) {
      Alert.alert('Error', 'Vui lòng xác minh OTP trước');
      return;
    }
    Alert.alert('Success', 'Cập nhật số điện thoại thành công!');
    setPhoneNumber('');
    setPhoneOtp('');
    setPhoneOtpSent(false);
    setPhoneOtpVerified(false);
  };

  const handleSendPasswordOtp = () => {
    if (!currentPassword.trim() || !newPassword.trim() || !confirmPassword.trim()) {
      Alert.alert('Error', 'Vui lòng điền đầy đủ các trường');
      return;
    }
    if (newPassword !== confirmPassword) {
      Alert.alert('Error', 'Mật khẩu mới không khớp');
      return;
    }
    setPasswordOtpSent(true);
    Alert.alert('Success', 'OTP đã được gửi đến email của bạn\nSử dụng OTP: 654321');
  };

  const handleVerifyPasswordOtp = () => {
    if (!passwordOtp.trim()) {
      Alert.alert('Error', 'Vui lòng nhập OTP');
      return;
    }
    if (passwordOtp === '654321') {
      setPasswordOtpVerified(true);
      Alert.alert('Success', 'OTP xác minh thành công!');
    } else {
      Alert.alert('Error', 'OTP không chính xác');
    }
  };

  const handleUpdatePassword = () => {
    if (!passwordOtpVerified) {
      Alert.alert('Error', 'Vui lòng xác minh OTP trước');
      return;
    }
    Alert.alert('Success', 'Cập nhật mật khẩu thành công!');
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
    setPasswordOtp('');
    setPasswordOtpSent(false);
    setPasswordOtpVerified(false);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
      {/* Tabs */}
      <View style={{ flexDirection: 'row', backgroundColor: '#fff', borderBottomWidth: 1, borderBottomColor: '#F3F4F6', paddingHorizontal: 16 }}>
        <TouchableOpacity
          onPress={() => setActiveTab('password')}
          style={{
            flex: 1,
            paddingVertical: 16,
            borderBottomWidth: activeTab === 'password' ? 2 : 0,
            borderBottomColor: activeTab === 'password' ? '#2563EB' : 'transparent',
          }}
        >
          <Text style={{ textAlign: 'center', color: activeTab === 'password' ? '#2563EB' : '#9CA3AF', fontWeight: activeTab === 'password' ? '600' : '500' }}>
            Change Password
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => setActiveTab('phone')}
          style={{
            flex: 1,
            paddingVertical: 16,
            borderBottomWidth: activeTab === 'phone' ? 2 : 0,
            borderBottomColor: activeTab === 'phone' ? '#2563EB' : 'transparent',
          }}
        >
          <Text style={{ textAlign: 'center', color: activeTab === 'phone' ? '#2563EB' : '#9CA3AF', fontWeight: activeTab === 'phone' ? '600' : '500' }}>
            Change Phone Number
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {activeTab === 'password' ? (
          // Password Tab
          <View>
            {/* Current Password */}
            <View style={{ marginBottom: 16 }}>
              <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>Current Password</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 8, paddingHorizontal: 12 }}>
                <Lock size={20} {...({ stroke: '#9CA3AF' } as any)} style={{ marginRight: 8 }} />
                <TextInput
                  placeholder="Enter current password"
                  secureTextEntry={!showPassword}
                  value={currentPassword}
                  onChangeText={setCurrentPassword}
                  style={{ flex: 1, paddingVertical: 12, fontSize: 14, color: '#111827' }}
                  placeholderTextColor="#9CA3AF"
                />
                <TouchableOpacity onPress={() => setShowPassword(!showPassword)}>
                  {showPassword ? (
                    <EyeOff size={20} {...({ stroke: '#9CA3AF' } as any)} />
                  ) : (
                    <Eye size={20} {...({ stroke: '#9CA3AF' } as any)} />
                  )}
                </TouchableOpacity>
              </View>
            </View>

            {/* New Password */}
            <View style={{ marginBottom: 16 }}>
              <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>New Password</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 8, paddingHorizontal: 12 }}>
                <Lock size={20} {...({ stroke: '#9CA3AF' } as any)} style={{ marginRight: 8 }} />
                <TextInput
                  placeholder="Enter new password"
                  secureTextEntry={!showNewPassword}
                  value={newPassword}
                  onChangeText={setNewPassword}
                  style={{ flex: 1, paddingVertical: 12, fontSize: 14, color: '#111827' }}
                  placeholderTextColor="#9CA3AF"
                />
                <TouchableOpacity onPress={() => setShowNewPassword(!showNewPassword)}>
                  {showNewPassword ? (
                    <EyeOff size={20} {...({ stroke: '#9CA3AF' } as any)} />
                  ) : (
                    <Eye size={20} {...({ stroke: '#9CA3AF' } as any)} />
                  )}
                </TouchableOpacity>
              </View>
            </View>

            {/* Confirm Password */}
            <View style={{ marginBottom: 16 }}>
              <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>Confirm password</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 8, paddingHorizontal: 12 }}>
                <Lock size={20} {...({ stroke: '#9CA3AF' } as any)} style={{ marginRight: 8 }} />
                <TextInput
                  placeholder="Confirm new password"
                  secureTextEntry
                  value={confirmPassword}
                  onChangeText={setConfirmPassword}
                  style={{ flex: 1, paddingVertical: 12, fontSize: 14, color: '#111827' }}
                  placeholderTextColor="#9CA3AF"
                />
              </View>
            </View>

            {/* Send OTP Button */}
            {!passwordOtpSent ? (
              <TouchableOpacity
                onPress={handleSendPasswordOtp}
                style={{ backgroundColor: '#2563EB', borderRadius: 8, paddingVertical: 12, alignItems: 'center', marginBottom: 16 }}
                activeOpacity={0.7}
              >
                <Text style={{ color: '#fff', fontWeight: '600', fontSize: 14 }}>Send OTP</Text>
              </TouchableOpacity>
            ) : (
              <>
                {/* OTP Input */}
                <View style={{ marginBottom: 16 }}>
                  <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>OTP Code</Text>
                  <TextInput
                    placeholder="Enter OTP 6 number"
                    value={passwordOtp}
                    onChangeText={setPasswordOtp}
                    keyboardType="number-pad"
                    maxLength={6}
                    style={{ backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 12, fontSize: 14, color: '#111827' }}
                    placeholderTextColor="#9CA3AF"
                  />
                </View>

                {/* Verify OTP Button */}
                <TouchableOpacity
                  onPress={handleVerifyPasswordOtp}
                  style={{ backgroundColor: '#10B981', borderRadius: 8, paddingVertical: 12, alignItems: 'center', marginBottom: 16 }}
                  activeOpacity={0.7}
                >
                  <Text style={{ color: '#fff', fontWeight: '600', fontSize: 14 }}>Xác minh OTP</Text>
                </TouchableOpacity>

                {passwordOtpVerified && (
                  <>
                    <View style={{ backgroundColor: '#DCFCE7', borderRadius: 8, padding: 12, marginBottom: 16 }}>
                      <Text style={{ color: '#15803D', fontWeight: '500' }}>✓ OTP đã xác minh thành công</Text>
                    </View>

                    {/* Update Password Button */}
                    <TouchableOpacity
                      onPress={handleUpdatePassword}
                      style={{ backgroundColor: '#2563EB', borderRadius: 8, paddingVertical: 12, alignItems: 'center' }}
                      activeOpacity={0.7}
                    >
                      <Text style={{ color: '#fff', fontWeight: '600', fontSize: 14 }}>Cập nhật mật khẩu</Text>
                    </TouchableOpacity>
                  </>
                )}
              </>
            )}

            {/* Test OTP Info */}
            <View style={{ backgroundColor: '#FEF3C7', borderRadius: 8, padding: 12, marginTop: 24 }}>
              <Text style={{ color: '#92400E', fontSize: 12 }}>💡 OTP thử nghiệm: <Text style={{ fontWeight: '700' }}>654321</Text></Text>
            </View>
          </View>
        ) : (
          // Phone Tab
          <View>
            {/* Current Phone */}
            <View style={{ marginBottom: 16 }}>
              <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>Current Phone Number</Text>
              <View style={{ backgroundColor: '#F3F4F6', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 12, flexDirection: 'row', alignItems: 'center' }}>
                <Phone size={20} {...({ stroke: '#9CA3AF' } as any)} style={{ marginRight: 8 }} />
                <Text style={{ fontSize: 14, color: '#9CA3AF' }}>0987654321</Text>
              </View>
            </View>

            {/* New Phone Number */}
            <View style={{ marginBottom: 16 }}>
              <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>New Phone Number</Text>
              <View style={{ flexDirection: 'row', alignItems: 'center', backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 8, paddingHorizontal: 12 }}>
                <Phone size={20} {...({ stroke: '#9CA3AF' } as any)} style={{ marginRight: 8 }} />
                <TextInput
                  placeholder="Enter new phone number"
                  keyboardType="phone-pad"
                  value={phoneNumber}
                  onChangeText={setPhoneNumber}
                  style={{ flex: 1, paddingVertical: 12, fontSize: 14, color: '#111827' }}
                  placeholderTextColor="#9CA3AF"
                />
              </View>
            </View>

            {/* Send OTP Button */}
            {!phoneOtpSent ? (
              <TouchableOpacity
                onPress={handleSendPhoneOtp}
                style={{ backgroundColor: '#2563EB', borderRadius: 8, paddingVertical: 12, alignItems: 'center', marginBottom: 16 }}
                activeOpacity={0.7}
              >
                <Text style={{ color: '#fff', fontWeight: '600', fontSize: 14 }}>Send OTP</Text>
              </TouchableOpacity>
            ) : (
              <>
                {/* OTP Input */}
                <View style={{ marginBottom: 16 }}>
                  <Text style={{ fontSize: 14, fontWeight: '500', color: '#111827', marginBottom: 8 }}>OTP Verify</Text>
                  <TextInput
                    placeholder="Enter OTP 6 number"
                    value={phoneOtp}
                    onChangeText={setPhoneOtp}
                    keyboardType="number-pad"
                    maxLength={6}
                    style={{ backgroundColor: '#fff', borderWidth: 1, borderColor: '#E5E7EB', borderRadius: 8, paddingHorizontal: 12, paddingVertical: 12, fontSize: 14, color: '#111827' }}
                    placeholderTextColor="#9CA3AF"
                  />
                </View>

                {/* Verify OTP Button */}
                <TouchableOpacity
                  onPress={handleVerifyPhoneOtp}
                  style={{ backgroundColor: '#10B981', borderRadius: 8, paddingVertical: 12, alignItems: 'center', marginBottom: 16 }}
                  activeOpacity={0.7}
                >
                  <Text style={{ color: '#fff', fontWeight: '600', fontSize: 14 }}>Verify OTP</Text>
                </TouchableOpacity>

                {phoneOtpVerified && (
                  <>
                    <View style={{ backgroundColor: '#DCFCE7', borderRadius: 8, padding: 12, marginBottom: 16 }}>
                      <Text style={{ color: '#15803D', fontWeight: '500' }}>✓ OTP verified successfully.</Text>
                    </View>

                    {/* Update Phone Button */}
                    <TouchableOpacity
                      onPress={handleUpdatePhone}
                      style={{ backgroundColor: '#2563EB', borderRadius: 8, paddingVertical: 12, alignItems: 'center' }}
                      activeOpacity={0.7}
                    >
                      <Text style={{ color: '#fff', fontWeight: '600', fontSize: 14 }}>Update Phone Number</Text>
                    </TouchableOpacity>
                  </>
                )}
              </>
            )}

            {/* Test OTP Info */}
            <View style={{ backgroundColor: '#FEF3C7', borderRadius: 8, padding: 12, marginTop: 24 }}>
              <Text style={{ color: '#92400E', fontSize: 12 }}>💡 OTP thử nghiệm: <Text style={{ fontWeight: '700' }}>123456</Text></Text>
            </View>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
