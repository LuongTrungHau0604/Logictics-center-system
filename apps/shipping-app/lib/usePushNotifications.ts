// hooks/usePushNotifications.ts
import { useState, useEffect, useRef } from 'react';
import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import { registerDeviceToken } from '@/lib/api'; // Import hàm API vừa tạo

// Cấu hình cách hiển thị thông báo khi App đang mở (Foreground)
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true, // Hiện thông báo đè lên màn hình
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export function usePushNotifications() {
  const [expoPushToken, setExpoPushToken] = useState<string | undefined>();
  const notificationListener = useRef<any>();
  const responseListener = useRef<any>();

  async function registerForPushNotificationsAsync() {
    let token;
    if (Platform.OS === 'android') {
      await Notifications.setNotificationChannelAsync('default', {
        name: 'Logistics Updates',
        importance: Notifications.AndroidImportance.MAX,
        vibrationPattern: [0, 250, 250, 250],
        lightColor: '#FF231F7C',
      });
    }

    if (Device.isDevice) {
      const { status: existingStatus } = await Notifications.getPermissionsAsync();
      let finalStatus = existingStatus;
      if (existingStatus !== 'granted') {
        const { status } = await Notifications.requestPermissionsAsync();
        finalStatus = status;
      }
      if (finalStatus !== 'granted') {
        alert('Cần cấp quyền thông báo để nhận đơn hàng!');
        return;
      }
      
      // Lấy FCM Token (Dùng cho Firebase) hoặc Expo Token
      // Nếu backend bạn dùng firebase-admin như đã bàn, ta lấy DevicePushToken
      token = (await Notifications.getDevicePushTokenAsync()).data;
      
      // Gửi token lên server ngay khi lấy được
      if (token) {
        console.log("📲 My Device Token:", token);
        await registerDeviceToken(token);
      }
    } else {
      alert('Phải dùng thiết bị thật để test thông báo Push');
    }
    return token;
  }

  useEffect(() => {
    registerForPushNotificationsAsync().then(token => setExpoPushToken(token));

    // Lắng nghe khi có thông báo đến (App đang mở)
    notificationListener.current = Notifications.addNotificationReceivedListener(notification => {
      // Bạn có thể reload lại list đơn hàng tại đây nếu muốn
      console.log("🔔 Đã nhận thông báo mới:", notification);
    });

    // Lắng nghe khi người dùng BẤM vào thông báo
    responseListener.current = Notifications.addNotificationResponseReceivedListener(response => {
      console.log("👆 Người dùng bấm vào thông báo");
      // Điều hướng đến màn hình chi tiết đơn hàng (Router push)
    });

    return () => {
      Notifications.removeNotificationSubscription(notificationListener.current);
      Notifications.removeNotificationSubscription(responseListener.current);
    };
  }, []);

  return expoPushToken;
}