import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Package, Loader2 } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { authService, type SmeOwnerRegistrationRequest } from '../../services/authService';
import { aiServiceClient } from '../../services/api';

// Interface cho form data
interface FormData {
  companyName: string;      // business_name
  taxId: string;           // tax_code  
  email: string;
  phone: string;
  address: string;
  businessType: string;    // Không gửi lên API (chỉ để UI)
  userName: string;        // username
  password: string;
  confirmPassword: string; // Không gửi lên API
}

export function RegisterPage() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  // 1. Thêm state cho suggestions
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null); // Để xử lý click outside
  
  const [formData, setFormData] = useState<FormData>({
    companyName: '',
    taxId: '',
    email: '',
    phone: '',
    address: '',
    businessType: '',
    userName: '',
    password: '',
    confirmPassword: '',
  });

  // Validation functions
  const validateForm = (): string | null => {
    if (!formData.companyName.trim()) return 'Company name is required';
    if (!formData.taxId.trim()) return 'Tax ID is required';
    if (!formData.email.trim()) return 'Email is required';
    if (!formData.phone.trim()) return 'Phone number is required';
    if (!formData.address.trim()) return 'Address is required';
    if (!formData.userName.trim()) return 'Username is required';
    if (!formData.password) return 'Password is required';
    if (formData.password !== formData.confirmPassword) {
      return 'Passwords do not match';
    }
    if (formData.password.length < 6) return 'Password must be at least 6 characters';
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) return 'Invalid email format';
    
    return null;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Clear previous messages
    setError(null);
    setSuccess(null);
    
    // Validate form
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setIsLoading(true);
    
    try {
      // Chuẩn bị data để gửi lên API (khớp với SmeOwnerRegistrationRequest)
      const registrationData: SmeOwnerRegistrationRequest = {
        username: formData.userName,
        password: formData.password,
        business_name: formData.companyName,
        tax_code: formData.taxId,
        address: formData.address,
        email: formData.email,
        phone: formData.phone,
      };

      console.log('📤 Submitting registration data:', registrationData);
      
      // Gọi API đăng ký
      const response = await authService.registerSmeOwner(registrationData);
      
      console.log('✅ Registration successful:', response);
      
      // Success - redirect to dashboard hoặc success page
      setSuccess('Registration successful! Redirecting to dashboard...');
      
      // Optional: Save user info to localStorage
      localStorage.setItem('user', JSON.stringify(response));
      
      // Redirect after 2 seconds
      setTimeout(() => {
        navigate('/login');
      }, 2000);
      
    } catch (error: any) {
      console.error('❌ Registration error:', error);
      
      // Handle different types of errors
      if (error.detail) {
        setError(error.detail);
      } else if (error.message) {
        setError(error.message);
      } else {
        setError('Registration failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (error) setError(null);
  };

  useEffect(() => {
    // Chỉ gọi API khi người dùng gõ > 2 ký tự
    if (formData.address.length < 3) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        // Gọi endpoint chúng ta vừa tạo ở Bước 2
        const response = await aiServiceClient.get('/geocoding/autocomplete', {
          params: { text: formData.address }
        });
        if (response.data && response.data.suggestions) {
          setSuggestions(response.data.suggestions);
          setShowSuggestions(true);
        }
      } catch (err) {
        console.error("Autocomplete error:", err);
      }
    }, 500); // Delay 500ms sau khi ngừng gõ

    return () => clearTimeout(timer);
  }, [formData.address]);

  // 3. Xử lý khi chọn một địa chỉ từ list
  const handleSelectAddress = (suggestion: any) => {
    // Điền địa chỉ vào ô input
    handleChange('address', suggestion.label);
    
    // Tắt suggestion
    setShowSuggestions(false);
    
    // (Optional) Bạn có thể lưu luôn tọa độ lat/lon vào state nếu cần gửi lên server
    // setFormData(prev => ({ ...prev, lat: suggestion.latitude, lon: suggestion.longitude }));
  };

  // 4. Tắt dropdown khi click ra ngoài
  useEffect(() => {
    function handleClickOutside(event: any) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-accent/5 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl">
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
            <CardTitle>Register Your Business</CardTitle>
            <CardDescription>Create an account to start optimizing your deliveries</CardDescription>
          </CardHeader>
          <CardContent>
            {/* Success Message */}
            {success && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <p className="text-green-700 text-sm">{success}</p>
              </div>
            )}

            {/* Error Message */}
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-700 text-sm">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="companyName">Company Name *</Label>
                  <Input 
                    id="companyName" 
                    placeholder="Acme Corporation"
                    value={formData.companyName}
                    onChange={(e) => handleChange('companyName', e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="taxId">Tax ID / Registration Number *</Label>
                  <Input 
                    id="taxId" 
                    placeholder="123456789"
                    value={formData.taxId}
                    onChange={(e) => handleChange('taxId', e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>

              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email">Business Email *</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    placeholder="admin@company.com"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number *</Label>
                  <Input 
                    id="phone" 
                    type="tel" 
                    placeholder="0123456789"
                    value={formData.phone}
                    onChange={(e) => handleChange('phone', e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2 relative" ref={wrapperRef}>
                <Label htmlFor="address">Business Address *</Label>
                <Input 
                  id="address" 
                  placeholder="Start typing your address..."
                  value={formData.address}
                  onChange={(e) => {
                    handleChange('address', e.target.value);
                    setShowSuggestions(true); // Hiện lại khi gõ tiếp
                  }}
                  disabled={isLoading}
                  required
                  autoComplete="off" // Tắt autocomplete mặc định của trình duyệt
                />
                {/* Dropdown Suggestions */}
                {showSuggestions && suggestions.length > 0 && (
                  <div className="absolute z-50 w-full bg-white border border-gray-200 rounded-md shadow-lg mt-1 max-h-60 overflow-y-auto">
                    {suggestions.map((item, index) => (
                      <div
                        key={index}
                        className="p-3 hover:bg-gray-100 cursor-pointer text-sm text-gray-700 border-b border-gray-50 last:border-b-0"
                        onClick={() => handleSelectAddress(item)}
                      >
                        <div className="flex items-center gap-2">
                          {/* Icon định vị nhỏ cho đẹp */}
                          <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                          </svg>
                          {item.label}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="businessType">Business Type *</Label>
                <Select 
                  onValueChange={(value: string) => handleChange('businessType', value)}
                  disabled={isLoading}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select business type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="retail">Retail / E-commerce</SelectItem>
                    <SelectItem value="wholesale">Wholesale Distribution</SelectItem>
                    <SelectItem value="manufacturing">Manufacturing</SelectItem>
                    <SelectItem value="food">Food & Beverage</SelectItem>
                    <SelectItem value="logistics">Logistics Provider</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="userName">User Name *</Label>
                <Input 
                  id="userName" 
                  placeholder="acme_corporation_123"
                  value={formData.userName}
                  onChange={(e) => handleChange('userName', e.target.value)}
                  disabled={isLoading}
                  required
                />
              </div>
              
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="password">Password *</Label>
                  <Input 
                    id="password" 
                    type="password"
                    placeholder="At least 6 characters"
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password *</Label>
                  <Input 
                    id="confirmPassword" 
                    type="password"
                    placeholder="Confirm your password"
                    value={formData.confirmPassword}
                    onChange={(e) => handleChange('confirmPassword', e.target.value)}
                    disabled={isLoading}
                    required
                  />
                </div>
              </div>

              <div className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" required disabled={isLoading} />
                <span className="text-sm text-muted-foreground">
                  I agree to the{' '}
                  <Link to="/" className="text-primary hover:underline">Terms of Service</Link>
                  {' '}and{' '}
                  <Link to="/" className="text-primary hover:underline">Privacy Policy</Link>
                </span>
              </div>

              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Registering Business...
                  </>
                ) : (
                  'Register Business'
                )}
              </Button>
            </form>

            <div className="mt-6 text-center text-sm text-muted-foreground">
              Already have an account?{' '}
              <Link to="/login" className="text-primary hover:underline">
                Sign in
              </Link>
            </div>
          </CardContent>
        </Card>

        <div className="mt-6 text-center text-sm text-muted-foreground">
          <Link to="/" className="text-primary hover:underline">
            Back to home
          </Link>
        </div>
      </div>
    </div>
  );
}
