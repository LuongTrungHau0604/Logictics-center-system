import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';
import { 
  User, 
  Calendar, 
  History, 
  Settings, 
  HelpCircle, 
  LogOut,
  ChevronRight,
  Star,
  Award
} from 'lucide-react-native';

// [IMPORTANT] Adjust this path to point to your actual api.ts file
import { getShipperProfile, logout } from '../../lib/api'; 

// Interface matching the response from your Backend
interface ShipperProfile {
  full_name: string;
  email: string;
  phone: string;
  warehouse_id: string;
  shipper_id: string;
  vehicle_type: string;
  status: string;
  rating: number;
  area_id: string;
  total_deliveries?: number;
  success_rate?: number;
}

export default function ProfileScreen() {
  const router = useRouter();
  const [profile, setProfile] = useState<ShipperProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // 1. Fetch Profile Data on Mount
  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const data = await getShipperProfile();
      setProfile(data);
    } catch (error) {
      console.error('Failed to load profile:', error);
      Alert.alert('Error', 'Could not load profile data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              // 2. Call the API logout function to clear tokens
              await logout();
              router.replace('/login');
            } catch (error) {
              console.error('Logout error:', error);
              // Force navigation even if API fail (client-side cleanup)
              router.replace('/login');
            }
          },
        },
      ],
    );
  };

  const handleHelpPress = () => {
    alert('Nếu bạn cần hỗ trợ, vui lòng gửi email về support@company.com');
  };

  // 3. Loading State
  if (loading) {
    return (
      <SafeAreaView style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f9fafb' }}>
        <ActivityIndicator size="large" color="#2563EB" />
        <Text style={{ marginTop: 12, color: '#4B5563' }}>Loading profile...</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#f9fafb' }}>
      <ScrollView style={{ flex: 1 }} contentContainerStyle={{ padding: 16 }}>
        {/* Profile Header */}
        <View style={{ backgroundColor: '#fff', borderRadius: 12, padding: 24, marginBottom: 24, alignItems: 'center' }}>
          <View style={{ backgroundColor: '#2563EB', borderRadius: 60, width: 96, height: 96, justifyContent: 'center', alignItems: 'center', marginBottom: 16 }}>
            {/* Display first letter of name if available, else generic User icon */}
            {profile?.full_name ? (
               <Text style={{ fontSize: 36, color: '#FFFFFF', fontWeight: 'bold' }}>
                 {profile.full_name.charAt(0).toUpperCase()}
               </Text>
            ) : (
               <User size={48} {...({ stroke: '#FFFFFF' } as any)} />
            )}
          </View>
          
          {/* Dynamic Name and ID */}
          <Text style={{ fontSize: 24, fontWeight: '700', color: '#111827', marginBottom: 4, textAlign: 'center' }}>
            {profile?.full_name || 'Shipper'}
          </Text>
          <Text style={{ fontSize: 14, color: '#4B5563', marginBottom: 16 }}>
            ID: {profile?.shipper_id || '---'}
          </Text>

          {/* Dynamic Stats */}
          <View style={{ flexDirection: 'row', width: '100%', justifyContent: 'space-around', marginTop: 16, paddingTop: 16, borderTopWidth: 1, borderTopColor: '#F3F4F6' }}>
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 24, fontWeight: '700', color: '#2563EB' }}>
                {profile?.total_deliveries || 0}
              </Text>
              <Text style={{ fontSize: 12, color: '#4B5563', marginTop: 4 }}>Deliveries</Text>
            </View>
            <View style={{ alignItems: 'center' }}>
              <Text style={{ fontSize: 24, fontWeight: '700', color: '#10B981' }}>
                {profile?.success_rate || 0}%
              </Text>
              <Text style={{ fontSize: 12, color: '#4B5563', marginTop: 4 }}>Success Rate</Text>
            </View>
            <View style={{ alignItems: 'center' }}>
              <View style={{ flexDirection: 'row', alignItems: 'center' }}>
                <Text style={{ fontSize: 24, fontWeight: '700', color: '#F59E0B' }}>
                  {profile?.rating || 5.0}
                </Text>
                <Star size={16} {...({ stroke: '#F59E0B', fill: '#F59E0B' } as any)} style={{ marginLeft: 4 }} />
              </View>
              <Text style={{ fontSize: 12, color: '#4B5563', marginTop: 4 }}>Rating</Text>
            </View>
          </View>
        </View>

        {/* Achievement (Conditional Rendering example) */}
        {(profile?.rating && profile.rating >= 4.8) && (
          <View style={{ backgroundColor: '#FCD34D', borderRadius: 12, padding: 16, marginBottom: 24, flexDirection: 'row', alignItems: 'center' }}>
            <View style={{ backgroundColor: '#fff', borderRadius: 50, padding: 12, marginRight: 16 }}>
              <Award size={24} {...({ stroke: '#F59E0B' } as any)} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ color: '#fff', fontWeight: '700', fontSize: 16, marginBottom: 4 }}>
                Top Performer
              </Text>
              <Text style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: 14 }}>
                You have an excellent rating! Keep it up! 🎉
              </Text>
            </View>
          </View>
        )}

        {/* Menu Items */}
        <View style={{ backgroundColor: '#fff', borderRadius: 12, marginBottom: 24, overflow: 'hidden' }}>
          <MenuItem
            icon={Calendar}
            label="Work Schedule"
            onPress={() => router.push('/schedule')}
          />
          <MenuItem
            icon={History}
            label="Delivery History"
            onPress={() => router.push('/history')}
          />
          <MenuItem
            icon={Settings}
            label="Settings"
            onPress={() => router.push('/settings')}
          />
          <MenuItem
            icon={HelpCircle}
            label="Help & Support"
            onPress={() => handleHelpPress()}
            showDivider={false}
          />
        </View>

        {/* Logout */}
        <TouchableOpacity
          onPress={handleLogout}
          style={{ backgroundColor: '#fff', borderRadius: 12, padding: 16, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', borderWidth: 1, borderColor: '#FCA5A5' }}
          activeOpacity={0.7}
        >
          <LogOut size={20} {...({ stroke: '#EF4444' } as any)} />
          <Text style={{ color: '#EF4444', fontWeight: '600', fontSize: 16, marginLeft: 8 }}>
            Logout
          </Text>
        </TouchableOpacity>

        {/* App Version & Info */}
        <View style={{ marginTop: 24, alignItems: 'center' }}>
           <Text style={{ color: '#9CA3AF', fontSize: 12 }}>Version 1.0.0</Text>
           {profile?.vehicle_type && (
             <Text style={{ color: '#9CA3AF', fontSize: 12, marginTop: 4 }}>
               Vehicle: {profile.vehicle_type}
             </Text>
           )}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

interface MenuItemProps {
  icon: React.ComponentType<any>;
  label: string;
  onPress: () => void;
  showDivider?: boolean;
}

function MenuItem({ icon: Icon, label, onPress, showDivider = true }: MenuItemProps) {
  return (
    <>
      <TouchableOpacity
        onPress={onPress}
        style={{ flexDirection: 'row', alignItems: 'center', padding: 16 }}
        activeOpacity={0.7}
      >
        <View style={{ backgroundColor: '#F3F4F6', borderRadius: 20, padding: 8, marginRight: 12 }}>
          <Icon size={20} {...({ stroke: '#6B7280' } as any)} />
        </View>
        <Text style={{ flex: 1, color: '#111827', fontWeight: '500' }}>
          {label}
        </Text>
        <ChevronRight size={20} {...({ stroke: '#9CA3AF' } as any)} />
      </TouchableOpacity>
      {showDivider && <View style={{ height: 1, backgroundColor: '#F3F4F6', marginLeft: 64 }} />}
    </>
  );
}