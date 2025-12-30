import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Package, Loader2, AlertCircle } from 'lucide-react';
import { useState } from 'react';
import { authService } from '../../services/authService';

export function LoginPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Form validation
  const validateForm = () => {
    if (!formData.username.trim()) return 'Username is required';
    if (!formData.password) return 'Password is required';
    return null;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(null);
    
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    
    try {
      console.log('🔐 Attempting login with username:', formData.username);
      
      const loginResponse = await authService.login({
        username: formData.username,
        password: formData.password,
      });
      
      console.log('✅ Login successful:', loginResponse.user);
      
      const user = loginResponse.user;

      // 1. QUAN TRỌNG: Lưu user vào localStorage để DashboardLayout đọc được Role
      localStorage.setItem('user', JSON.stringify(user));
      // localStorage.setItem('token', loginResponse.token); // Nếu có token thì lưu thêm dòng này

      // 2. Điều hướng dựa trên `navConfig` bạn đã định nghĩa
      switch (user.role) {
        case 'ADMIN':
          // NavConfig: Admin -> Overview đầu tiên
          navigate('/dashboard/overview');
          break;

        case 'SME_OWNER':
          // NavConfig: SME -> Overview đầu tiên
          navigate('/dashboard/overview');
          break;

        case 'WAREHOUSE_MANAGER':
        case 'WAREHOUSE_STAFF': // Gộp chung staff vào đây nếu logic giống nhau
          // NavConfig: Manager -> Warehouse Staff đầu tiên
          navigate('/dashboard/warehousestaff');
          break;

        case 'SHIPPER':
          // Mặc định cho Shipper (thường là My Orders)
          navigate('/dashboard/orders');
          break;
        case 'DISPATCH':
          navigate('/dashboard/dispatch');
          break;
        default:
          // Role không xác định
          await authService.logout();
          localStorage.removeItem('user'); // Xóa rác nếu có
          setError('Invalid user role. Please contact support.');
      }
      
    } catch (error) {
      console.error('❌ Login error:', error);
      setError(error.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (error) setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-accent/5 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="flex justify-center mb-8">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
              <Package className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-xl text-foreground">AI Transport Hub</span>
          </Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Welcome Back</CardTitle>
            <CardDescription>Sign in to your account to continue</CardDescription>
          </CardHeader>
          <CardContent>
            {/* Error Message */}
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md flex items-center gap-2">
                <AlertCircle className="w-5 h-5 text-red-600" />
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            <Tabs defaultValue="login" className="w-full">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login">Login</TabsTrigger>
                <TabsTrigger value="register" onClick={() => navigate('/register')}>Register</TabsTrigger>
              </TabsList>
              <TabsContent value="login">
                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username">Username or Email</Label>
                    <Input 
                      id="username" 
                      type="text" 
                      placeholder="Enter username or email"
                      value={formData.username}
                      onChange={(e) => handleChange('username', e.target.value)}
                      disabled={isLoading}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="password">Password</Label>
                    <Input 
                      id="password" 
                      type="password"
                      placeholder="Enter your password"
                      value={formData.password}
                      onChange={(e) => handleChange('password', e.target.value)}
                      disabled={isLoading}
                      required
                    />
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <label className="flex items-center gap-2">
                      <input type="checkbox" className="rounded" disabled={isLoading} />
                      <span className="text-muted-foreground">Remember me</span>
                    </label>
                    <Link to="/forgot-password" className="text-primary hover:underline">
                      Forgot password?
                    </Link>
                  </div>
                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Signing in...
                      </>
                    ) : (
                      'Sign In'
                    )}
                  </Button>
                </form>
              </TabsContent>
            </Tabs>

            <div className="mt-6 text-center text-sm text-muted-foreground">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary hover:underline">
                Register your business
              </Link>
            </div>
          </CardContent>
        </Card>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          <Link to="/tracking" className="text-primary hover:underline">
            Track an order
          </Link>
          {' · '}
          <Link to="/" className="text-primary hover:underline">
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}