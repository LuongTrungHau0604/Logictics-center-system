import { useFocusEffect, useRouter } from 'expo-router';

export default function WelcomeScreen() {
  const router = useRouter();

  useFocusEffect(() => {
    // Redirect to login screen immediately
    router.replace('/login');
  });

  return null;
}