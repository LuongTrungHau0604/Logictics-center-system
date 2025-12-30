import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  return (
    <>
      <StatusBar style="dark" />
      <Stack screenOptions={{ headerShown: false }}>
        {/* Các màn hình chính */}
        <Stack.Screen name="login" />
        <Stack.Screen name="index" />
        
        {/* Luồng Tabs (Bao gồm cả Delivery List & Detail bên trong) */}
        <Stack.Screen name="(tabs)" />

        {/* Các màn hình con nằm NGOÀI tabs (nếu có thư mục app/pickup/[id].tsx thì giữ lại) */}
        <Stack.Screen 
          name="pickup/[id]"
          options={{
            headerShown: true,
            headerTitle: 'Pickup Details',
            headerBackTitle: 'Back',
          }}
        />
        
        <Stack.Screen 
          name="history/index" 
          options={{
            headerShown: true,
            headerTitle: 'Delivery History',
            headerBackTitle: 'Back',
          }}
        />
        <Stack.Screen 
          name="schedule/index" 
          options={{
            headerShown: true,
            headerTitle: 'Work Schedule',
            headerBackTitle: 'Back',
          }}
        />
        <Stack.Screen 
          name="settings/index" 
          options={{
            headerShown: true,
            headerTitle: 'Settings',
            headerBackTitle: 'Back',
          }}
        />
      </Stack>
    </>
  );
}