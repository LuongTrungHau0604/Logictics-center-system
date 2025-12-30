import { useState, useEffect, useRef } from 'react';
import * as Device from 'expo-device';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';
import Constants from 'expo-constants'; // Cần cài: npx expo install expo-constants

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: false,
  }),
});

export function usePushNotifications() {
  const [token, setToken] = useState<string | undefined>();

  useEffect(() => {
    console.log("🎬 [Hook] Bắt đầu quy trình lấy Token...");
    
    registerForPushNotificationsAsync()
      .then(fetchedToken => {
        if (fetchedToken) {
          console.log("✅ [Hook] Thành công! Token là:", fetchedToken);
          setToken(fetchedToken);
        } else {
          console.log("❌ [Hook] Thất bại: Không lấy được token nào.");
        }
      })
      .catch(err => console.error("💥 [Hook] Lỗi Fatal:", err));
  }, []);

  return token;
}

async function registerForPushNotificationsAsync() {
  if (!Device.isDevice) {
    console.log('⚠️ [Hook] Cảnh báo: Đang chạy trên Máy ảo. Push Notification có thể không hoạt động.');
    // Trên máy ảo vẫn cứ thử chạy tiếp, nhưng khả năng cao sẽ fail
  }

  // 1. Cấu hình Channel cho Android
  if (Platform.OS === 'android') {
    await Notifications.setNotificationChannelAsync('default', {
      name: 'Shipper Alerts',
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: '#FF231F7C',
    });
  }

  // 2. Xin quyền
  console.log("Step 1: Kiểm tra quyền...");
  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;
  
  if (existingStatus !== 'granted') {
    console.log("Step 1.5: Đang xin quyền người dùng...");
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }
  
  if (finalStatus !== 'granted') {
    console.log('❌ [Hook] Quyền bị từ chối!');
    return undefined;
  }

  // 3. Lấy Token (Có timeout để chống treo)
  console.log("Step 2: Đang gọi Firebase lấy Token (Timeout 5s)...");
  
  try {
    // Tạo một Promise đua tốc độ: Ai xong trước thì thắng
    const tokenPromise = Notifications.getDevicePushTokenAsync();
    
    // Timeout sau 5 giây
    const timeoutPromise = new Promise((_, reject) => 
      setTimeout(() => reject(new Error("Quá thời gian chờ (Timeout)")), 5000)
    );

    const tokenData: any = await Promise.race([tokenPromise, timeoutPromise]);
    
    console.log("Step 3: Firebase phản hồi OK.");
    return tokenData.data;

  } catch (e: any) {
    console.error(`❌ [Hook] Lỗi lấy Device Token: ${e.message}`);
    
    // Fallback: Thử lấy Expo Token nếu FCM lỗi (Để debug xem config Expo có đúng ko)
    try {
        console.log("⚠️ [Hook] Thử fallback sang Expo Push Token...");
        const projectId = Constants?.expoConfig?.extra?.eas?.projectId ?? Constants?.easConfig?.projectId;
        
        // Nếu không có projectId thì log ra để biết
        if (!projectId) console.log("⚠️ [Hook] Không tìm thấy Project ID trong app.json");

        const expoToken = await Notifications.getExpoPushTokenAsync({
            projectId: projectId // Truyền Project ID nếu có
        });
        console.log("⚠️ [Hook] Expo Token (Fallback):", expoToken.data);
        return expoToken.data; 
    } catch (ex) {
        console.error("❌ [Hook] Fallback cũng thất bại:", ex);
        return undefined;
    }
  }
}