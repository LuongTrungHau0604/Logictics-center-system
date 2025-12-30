import { Stack } from 'expo-router';

export default function DeliveryStackLayout() {
  return (
    <Stack 
      screenOptions={{ 
        headerShown: false // Tắt header mặc định của Stack vì bạn đã tự làm Header trong từng màn hình
      }}
    >
      {/* Màn hình danh sách (index.tsx) */}
      <Stack.Screen name="index" />

      {/* Màn hình chi tiết ([id].tsx) */}
      <Stack.Screen name="[id]" />
    </Stack>
  );
}