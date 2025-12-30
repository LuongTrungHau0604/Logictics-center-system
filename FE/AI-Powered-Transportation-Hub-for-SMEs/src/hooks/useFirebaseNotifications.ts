// src/hooks/useFirebaseNotifications.ts
import { useEffect } from 'react';
import { ref, onChildAdded } from 'firebase/database'; // Bỏ 'remove'
import { database } from '../services/firebase';
import { toast } from 'sonner';

export function useFirebaseNotifications(userId: string | undefined) {
  useEffect(() => {
    if (!userId) return;

    const notifRef = ref(database, `notifications/${userId}`);

    // Chỉ lắng nghe tin mới để hiện Toast
    const unsubscribe = onChildAdded(notifRef, (snapshot) => {
      const data = snapshot.val();
      
      // Kiểm tra thời gian: Chỉ hiện Toast cho tin nhắn mới (trong vòng 5s đổ lại)
      // Để tránh việc F5 lại trang nó lại hiện Toast cũ
      const now = Date.now();
      const isRecent = data.timestamp && (now - data.timestamp < 10000); 

      if (data && isRecent) {
        if (data.type === 'SUCCESS') {
          toast.success(data.title, { description: data.message });
        } else if (data.type === 'ERROR') {
          toast.error(data.title, { description: data.message });
        } else {
          toast.info(data.title, { description: data.message });
        }
      }
      
      // ❌ QUAN TRỌNG: Đã XÓA dòng remove(snapshot.ref) đi rồi nhé!
    });

    return () => unsubscribe();
  }, [userId]);
}