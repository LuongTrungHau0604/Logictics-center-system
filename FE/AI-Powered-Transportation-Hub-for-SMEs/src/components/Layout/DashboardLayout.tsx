import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  Warehouse, 
  MapPin, 
  Users, 
  BarChart3, 
  Building2, 
  Shield,
  LogOut,
  Bell,
  Search,
  Moon,
  Sun,
  Menu,
  X,
  Edit
} from 'lucide-react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '../ui/avatar';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuLabel, 
  DropdownMenuSeparator, 
  DropdownMenuTrigger 
} from '../ui/dropdown-menu';
import { NotificationDropdown } from '../NotificationDropdown'; // <--- Import cái này
import { useState } from 'react';

// --- 1. IMPORT LIÊN QUAN ĐẾN THÔNG BÁO ---
import { Toaster } from 'sonner'; // Thư viện hiển thị Toast đẹp
import { useFirebaseNotifications } from '../../hooks/useFirebaseNotifications'; 

// --- 2. Cấu hình Menu cho từng Role riêng biệt ---
const navConfig: any = {
  ADMIN: [
    { name: 'Overview', href: '/dashboard/overview', icon: LayoutDashboard },
    { name: 'Warehouses', href: '/dashboard/warehouses', icon: Warehouse },
    { name: 'Dispatch', href: '/dashboard/dispatch', icon: MapPin },
    { name: 'Shippers', href: '/dashboard/shippers', icon: Users },
    { name: 'Admin Panel', href: '/dashboard/admin', icon: Shield },
    { name: 'Areas', href: '/dashboard/areas', icon: MapPin },
  ],
  SME_OWNER: [
    { name: 'Overview', href: '/dashboard/overview', icon: LayoutDashboard },
    { name: 'Orders', href: '/dashboard/orders', icon: Package },
    { name: 'Company Profile', href: '/dashboard/profile', icon: Building2 },
  ],
  WAREHOUSE_MANAGER: [
    { name: 'Warehouse Staff', href: '/dashboard/warehousestaff', icon: Users }
  ],
  DISPATCH: [
    { name: 'AI Dispatch', href: '/dashboard/dispatch', icon: MapPin },
    { name: 'Manual Management', href: '/dashboard/dispatch-management', icon: Edit },
    { name: 'Shippers', href: '/dashboard/shippers', icon: Users }

  ]
};

// Hàm helper để lấy menu
const getNavigationByRole = (role: string) => {
    return navConfig[role] || []; // Trả về mảng rỗng nếu không tìm thấy role
};

export function DashboardLayout() {
  const location = useLocation();
  const navigate = useNavigate();
  const [darkMode, setDarkMode] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Lấy thông tin User từ LocalStorage
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const userRole = user.role || 'GUEST'; 
  
  // --- 3. KÍCH HOẠT LẮNG NGHE FIREBASE ---
  // Hook này sẽ tự chạy ngầm. Khi có tin từ Firebase -> Hiện Toast lên.
  useFirebaseNotifications(user.user_id); 

  // Lấy menu dựa trên Role hiện tại
  const currentNavigation = getNavigationByRole(userRole);

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.classList.toggle('dark');
  };

  const handleLogout = () => {
    // Xóa data đăng nhập
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-background">
      {/* --- 4. ĐẶT TOASTER ĐỂ HIỂN THỊ POPUP THÔNG BÁO --- */}
      {/* position="top-right" để thông báo hiện góc phải trên cùng */}
      <Toaster position="top-right" richColors closeButton />

      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside className={`
        fixed top-0 left-0 z-50 h-screen w-64 bg-card border-r border-border
        transition-transform duration-300 ease-in-out
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-16 px-6 border-b border-border">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Package className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-foreground font-bold">Transport Hub</span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden"
              onClick={() => setSidebarOpen(false)}
            >
              <X className="w-5 h-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
            {currentNavigation.map((item: any) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={`
                    flex items-center gap-3 px-3 py-2 rounded-lg transition-colors
                    ${isActive 
                      ? 'bg-primary text-primary-foreground' 
                      : 'text-muted-foreground hover:bg-secondary hover:text-foreground'
                    }
                  `}
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Logout */}
          <div className="p-3 border-t border-border">
            <Button
              variant="ghost"
              className="w-full justify-start gap-3 text-muted-foreground hover:text-foreground"
              onClick={handleLogout}
            >
              <LogOut className="w-5 h-5" />
              <span>Logout</span>
            </Button>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <div className="lg:pl-64">
        {/* Top bar */}
        <header className="sticky top-0 z-30 h-16 bg-card border-b border-border">
          <div className="flex items-center justify-between h-full px-4 sm:px-6">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => setSidebarOpen(true)}
              >
                <Menu className="w-5 h-5" />
              </Button>

              {/* Search */}
              <div className="relative hidden sm:block">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input 
                  placeholder="Search..." 
                  className="pl-9 w-64 bg-background"
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              {/* Dark mode toggle */}
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleDarkMode}
              >
                {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </Button>

              {/* Notifications Icon (Chỉ để làm cảnh hoặc mở lịch sử nếu cần sau này) */}
              <NotificationDropdown />
              
              

              {/* User menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="rounded-full">
                    <Avatar>
                      <AvatarImage src="" />
                      <AvatarFallback>{user.username ? user.username.substring(0,2).toUpperCase() : 'U'}</AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-56">
                  <DropdownMenuLabel>
                    <div className="flex flex-col">
                      <span>{user.username || 'User'}</span>
                      <span className="text-xs text-muted-foreground">{user.email}</span>
                      <span className="text-xs font-bold text-blue-500 mt-1">{userRole}</span>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem>Profile Settings</DropdownMenuItem>
                  <DropdownMenuItem>Company Settings</DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="text-red-500 cursor-pointer">
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}