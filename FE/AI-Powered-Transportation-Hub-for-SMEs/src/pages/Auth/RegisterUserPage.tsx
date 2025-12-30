import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Package } from 'lucide-react';
import { useState } from 'react';

export function RegisterUserPage() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    phone: '',
    userName: '',
    password: '',
    confirmPassword: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/dashboard/overview');
  };

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

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
            <CardTitle>Register Your Account</CardTitle>
            <CardDescription>Create an account to start optimizing your deliveries</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="email"> Email *</Label>
                  <Input 
                    id="email" 
                    type="email" 
                    placeholder="admin@company.com"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone Number *</Label>
                  <Input 
                    id="phone" 
                    type="tel" 
                    placeholder="+1 (555) 000-0000"
                    value={formData.phone}
                    onChange={(e) => handleChange('phone', e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="userName">User Name *</Label>
                <Input 
                  id="userName" 
                  placeholder="acme_corporation_123"
                  value={formData.userName}
                  onChange={(e) => handleChange('userName', e.target.value)}
                  required
                />
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="password">Password *</Label>
                  <Input 
                    id="password" 
                    type="password"
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Confirm Password *</Label>
                  <Input 
                    id="confirmPassword" 
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => handleChange('confirmPassword', e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="flex items-start gap-2">
                <input type="checkbox" className="mt-1" required />
                <span className="text-sm text-muted-foreground">
                  I agree to the{' '}
                  <Link to="/" className="text-primary hover:underline">Terms of Service</Link>
                  {' '}and{' '}
                  <Link to="/" className="text-primary hover:underline">Privacy Policy</Link>
                </span>
              </div>

              <Button type="submit" className="w-full">
                Register Business
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
