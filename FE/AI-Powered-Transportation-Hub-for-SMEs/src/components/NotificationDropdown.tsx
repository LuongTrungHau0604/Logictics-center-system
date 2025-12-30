import { useState, useEffect } from 'react';
import { Bell, Check, Trash2 } from 'lucide-react';
import { Button } from '../components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { ScrollArea } from '../components/ui/scroll-area';
import { ref, onValue, remove } from 'firebase/database';
import { database } from '../services/firebase';
import { formatDistanceToNow } from 'date-fns'; // Cần cài: npm install date-fns

export function NotificationDropdown() {
  const [notifications, setNotifications] = useState<any[]>([]);
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  useEffect(() => {
    if (!user.user_id) return;

    const notifRef = ref(database, `notifications/${user.user_id}`);

    // onValue: Lấy toàn bộ danh sách mỗi khi có thay đổi
    const unsubscribe = onValue(notifRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        // Chuyển đổi Object Firebase thành Array và sắp xếp mới nhất lên đầu
        const list = Object.entries(data).map(([key, val]: any) => ({
          id: key,
          ...val,
        }));
        
        // Sắp xếp giảm dần theo timestamp
        list.sort((a, b) => b.timestamp - a.timestamp);
        setNotifications(list);
      } else {
        setNotifications([]);
      }
    });

    return () => unsubscribe();
  }, [user.user_id]);

  // Hàm xóa tất cả thông báo
  const handleClearAll = () => {
    if (!user.user_id) return;
    const notifRef = ref(database, `notifications/${user.user_id}`);
    remove(notifRef);
  };

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="w-5 h-5" />
          {/* Chấm đỏ báo số lượng */}
          {notifications.length > 0 && (
            <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-600 rounded-full border-2 border-background animate-pulse" />
          )}
        </Button>
      </DropdownMenuTrigger>

      <DropdownMenuContent align="end" className="w-80">
        <DropdownMenuLabel className="flex justify-between items-center">
          <span>Thông báo ({notifications.length})</span>
          {notifications.length > 0 && (
            <Button 
                variant="ghost" 
                size="sm" 
                className="text-xs text-red-500 h-6 px-2"
                onClick={handleClearAll}
            >
              <Trash2 className="w-3 h-3 mr-1" /> Xóa hết
            </Button>
          )}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        <ScrollArea className="h-[300px]">
          {notifications.length === 0 ? (
            <div className="p-4 text-center text-sm text-muted-foreground">
              Không có thông báo mới
            </div>
          ) : (
            notifications.map((item) => (
              <DropdownMenuItem 
                key={item.id} 
                className="flex flex-col items-start gap-1 p-3 border-b border-border last:border-0 cursor-pointer"
              >
                <div className="flex justify-between w-full">
                  <span className={`font-semibold text-sm ${
                    item.type === 'SUCCESS' ? 'text-green-600' : 
                    item.type === 'ERROR' ? 'text-red-600' : 'text-blue-600'
                  }`}>
                    {item.title}
                  </span>
                  <span className="text-[10px] text-muted-foreground whitespace-nowrap ml-2">
                    {item.timestamp ? formatDistanceToNow(item.timestamp, { addSuffix: true }) : ''}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground line-clamp-2">
                  {item.message}
                </p>
              </DropdownMenuItem>
            ))
          )}
        </ScrollArea>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}