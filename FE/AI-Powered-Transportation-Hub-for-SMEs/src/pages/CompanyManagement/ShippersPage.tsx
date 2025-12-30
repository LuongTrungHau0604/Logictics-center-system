import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '../../components/ui/avatar';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Plus, Search, MoreVertical, TrendingUp, MapPin, Package, Star, Loader2, AlertCircle } from 'lucide-react';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../../components/ui/dropdown-menu';
import { Progress } from '../../components/ui/progress';
import { employeeService, type Employee, type CreateStaffRequest } from '../../services/employeeService'; // Import service
import { warehouseService } from '../../services/warehouseService'; // Để lấy danh sách kho

// Interface mở rộng cho UI (kết hợp dữ liệu thật và giả lập hiệu suất)
interface ShipperUI extends Employee {
  efficiency: number;     // Mock
  totalDeliveries: number; // Mock
  successRate: number;    // Mock
  rating: number;         // Mock
  vehicle: string;        // Mock hoặc lấy từ backend nếu có
  shift: string;          // Mock
}

export function ShippersPage() {
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [shippers, setShippers] = useState<ShipperUI[]>([]);
  const [selectedShipper, setSelectedShipper] = useState<ShipperUI | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Create Dialog State
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [warehouses, setWarehouses] = useState<any[]>([]); // Danh sách kho để chọn khi tạo shipper
  const [newShipper, setNewShipper] = useState({
    full_name: '',
    phone: '',
    email: '',
    username: '',
    password: '',
    warehouse_id: '',
    vehicle_type: 'MOTORBIKE',
    dob: ''
  });

  // 1. Load dữ liệu khi vào trang
  useEffect(() => {
    loadShippers();
    loadWarehouses();
  }, []);

  const loadShippers = async () => {
    try {
      setIsLoading(true);
      // Gọi API lấy danh sách nhân viên với role = SHIPPER
      // Page 1, Limit 100 (Lấy hết để hiển thị demo)
      const data = await employeeService.getAllEmployees('SHIPPER', undefined, 1, 100);
      
      // Mapping dữ liệu thật sang cấu trúc UI (Bổ sung các trường thiếu bằng mock data)
      const mappedData: ShipperUI[] = data.map((emp: Employee) => ({
        ...emp,
        // Các trường dưới đây backend chưa trả về, ta random tạm để UI đẹp
        efficiency: Math.floor(Math.random() * (100 - 80) + 80), // 80-100%
        totalDeliveries: Math.floor(Math.random() * 500),
        successRate: (Math.random() * (100 - 90) + 90).toFixed(1) as unknown as number,
        rating: (Math.random() * (5 - 4) + 4).toFixed(1) as unknown as number,
        vehicle: 'Motorcycle',
        shift: 'Morning (8AM - 4PM)'
      }));

      setShippers(mappedData);
    } catch (err: any) {
      console.error('Failed to load shippers:', err);
      setError('Failed to load shipper list.');
    } finally {
      setIsLoading(false);
    }
  };

  const loadWarehouses = async () => {
    try {
      const data = await warehouseService.getAllWarehouses();
      setWarehouses(data);
    } catch (err) {
      console.error('Failed to load warehouses', err);
    }
  };

  // 2. Xử lý tạo Shipper mới
  const handleCreateShipper = async () => {
    // Validate cơ bản
    if (!newShipper.full_name || !newShipper.phone || !newShipper.warehouse_id) {
      alert("Please fill in required fields (*)");
      return;
    }

    setIsCreating(true);
    try {
      const requestData: CreateStaffRequest = {
        ...newShipper,
        role: 'SHIPPER',
        // Tự sinh username/pass nếu chưa nhập (Demo logic)
        username: newShipper.username || newShipper.email.split('@')[0] || newShipper.phone,
        password: newShipper.password || '123456',
        vehicle_type: newShipper.vehicle_type as any
      };

      await employeeService.createStaff(requestData);
      
      // Refresh list và đóng dialog
      await loadShippers();
      setIsCreateOpen(false);
      // Reset form
      setNewShipper({ full_name: '', phone: '', email: '', username: '', password: '', warehouse_id: '', vehicle_type: 'MOTORBIKE', dob: '' });
      
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to create shipper");
    } finally {
      setIsCreating(false);
    }
  };

  // 3. Filter Logic (Client-side filtering)
  const filteredShippers = shippers.filter(shipper => {
    const matchesSearch = shipper.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (shipper.email && shipper.email.toLowerCase().includes(searchQuery.toLowerCase())) ||
                         shipper.phone.includes(searchQuery);
    // Backend trả về status viết hoa (ACTIVE), UI select trả về thường (active) -> cần normalize
    const matchesStatus = statusFilter === 'all' || shipper.status === statusFilter.toUpperCase();
    return matchesSearch && matchesStatus;
  });

  // Stats
  const activeShippersCount = shippers.filter(s => s.status === 'ACTIVE').length;
  const avgEfficiency = shippers.length > 0 ? Math.round(shippers.reduce((acc, s) => acc + s.efficiency, 0) / shippers.length) : 0;
  const avgRating = shippers.length > 0 ? (shippers.reduce((acc, s) => acc + Number(s.rating), 0) / shippers.length).toFixed(1) : 0;

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 text-red-600 border border-red-200 rounded-md flex items-center gap-2">
          <AlertCircle className="w-5 h-5" /> {error}
        </div>
      )}

      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-foreground mb-1">Shippers</h1>
          <p className="text-muted-foreground">Manage delivery personnel and their assignments</p>
        </div>
        
        {/* Add Shipper Dialog */}
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild>
            <Button size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Add Shipper
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Add New Shipper</DialogTitle>
              <DialogDescription>Create a new shipper account.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Full Name *</Label>
                <Input 
                  placeholder="Nguyen Van A" 
                  value={newShipper.full_name}
                  onChange={(e) => setNewShipper({...newShipper, full_name: e.target.value})}
                />
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Phone Number *</Label>
                  <Input 
                    placeholder="090..." 
                    value={newShipper.phone}
                    onChange={(e) => setNewShipper({...newShipper, phone: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Email</Label>
                  <Input 
                    type="email" 
                    placeholder="email@example.com" 
                    value={newShipper.email}
                    onChange={(e) => setNewShipper({...newShipper, email: e.target.value})}
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Assigned Warehouse *</Label>
                <Select 
                  value={newShipper.warehouse_id} 
                  onValueChange={(val) => setNewShipper({...newShipper, warehouse_id: val})}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select warehouse" />
                  </SelectTrigger>
                  <SelectContent>
                    {warehouses.map(wh => (
                      <SelectItem key={wh.warehouse_id} value={wh.warehouse_id}>{wh.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Vehicle Type</Label>
                  <Select 
                    value={newShipper.vehicle_type}
                    onValueChange={(val) => setNewShipper({...newShipper, vehicle_type: val})}
                  >
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="MOTORBIKE">Motorcycle</SelectItem>
                      <SelectItem value="VAN">Van</SelectItem>
                      <SelectItem value="TRUCK">Truck</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Date of Birth</Label>
                  <Input 
                    type="date" 
                    value={newShipper.dob}
                    onChange={(e) => setNewShipper({...newShipper, dob: e.target.value})}
                  />
                </div>
              </div>
              
              {/* Optional Login Info */}
              <div className="grid sm:grid-cols-2 gap-4 pt-2 border-t">
                 <div className="space-y-2">
                    <Label>Username (Optional)</Label>
                    <Input placeholder="Auto-generated if empty" value={newShipper.username} onChange={(e) => setNewShipper({...newShipper, username: e.target.value})} />
                 </div>
                 <div className="space-y-2">
                    <Label>Password (Optional)</Label>
                    <Input type="password" placeholder="Default: 123456" value={newShipper.password} onChange={(e) => setNewShipper({...newShipper, password: e.target.value})} />
                 </div>
              </div>

            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsCreateOpen(false)}>Cancel</Button>
              <Button onClick={handleCreateShipper} disabled={isCreating}>
                {isCreating ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Create Shipper'}
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total Shippers</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">{shippers.length}</div>
            <p className="text-sm text-muted-foreground">{activeShippersCount} currently active</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Avg Efficiency</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">{avgEfficiency}%</div>
            <p className="text-sm text-muted-foreground">Mock Data</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Avg Rating</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground flex items-center gap-1">{avgRating} <Star className="w-5 h-5 text-amber-500 fill-amber-500" /></div>
            <p className="text-sm text-muted-foreground">Mock Data</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total Deliveries</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">{shippers.reduce((acc, s) => acc + s.totalDeliveries, 0).toLocaleString()}</div>
            <p className="text-sm text-muted-foreground">Mock Data</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input 
                placeholder="Search by name, phone or email..." 
                className="pl-9"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Shippers Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredShippers.map((shipper) => (
          <Card key={shipper.employee_id} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedShipper(shipper)}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <Avatar className="w-12 h-12">
                    <AvatarImage src="" /> {/* Chưa có ảnh */}
                    <AvatarFallback>{shipper.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                  </Avatar>
                  <div>
                    <CardTitle className="text-base">{shipper.full_name}</CardTitle>
                    <CardDescription className="flex items-center gap-1 text-xs">
                      <MapPin className="w-3 h-3" />
                      {shipper.warehouse_id || 'No Warehouse'}
                    </CardDescription>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                    <Button variant="ghost" size="icon">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={(e) => { e.stopPropagation(); setSelectedShipper(shipper); }}>
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem disabled>Edit Info</DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <Badge variant={shipper.status === 'ACTIVE' ? 'default' : 'secondary'}>
                  {shipper.status}
                </Badge>
                <div className="flex items-center gap-1">
                  <Star className="w-4 h-4 text-amber-500 fill-amber-500" />
                  <span className="text-sm text-foreground">{shipper.rating}</span>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2 text-sm">
                  <span className="text-muted-foreground">Efficiency (Mock)</span>
                  <span className="text-foreground">{shipper.efficiency}%</span>
                </div>
                <Progress value={shipper.efficiency} className="h-2" />
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2 border-t border-border text-sm">
                <div>
                  <div className="text-xs text-muted-foreground">Phone</div>
                  <div className="text-foreground flex items-center gap-1">
                    {shipper.phone}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">Success Rate</div>
                  <div className="text-foreground flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" />
                    {shipper.successRate}%
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Shipper Detail Dialog */}
      {selectedShipper && (
        <Dialog open={!!selectedShipper} onOpenChange={() => setSelectedShipper(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-3">
                <Avatar className="w-12 h-12">
                  <AvatarFallback>{selectedShipper.full_name.split(' ').map(n => n[0]).join('')}</AvatarFallback>
                </Avatar>
                {selectedShipper.full_name}
              </DialogTitle>
              <DialogDescription>Shipper Profile - ID: {selectedShipper.employee_id}</DialogDescription>
            </DialogHeader>
            <div className="space-y-6 py-4">
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-muted-foreground">Status</label>
                  <div><Badge variant={selectedShipper.status === 'ACTIVE' ? 'default' : 'secondary'}>{selectedShipper.status}</Badge></div>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Phone</label>
                  <div className="text-foreground">{selectedShipper.phone}</div>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Email</label>
                  <div className="text-foreground">{selectedShipper.email}</div>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Warehouse</label>
                  <div className="text-foreground">{selectedShipper.warehouse_id}</div>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">User ID (Login)</label>
                  <div className="text-foreground font-mono text-xs">{selectedShipper.user_id || 'N/A'}</div>
                </div>
                <div>
                  <label className="text-sm text-muted-foreground">Created At</label>
                  <div className="text-foreground">{new Date(selectedShipper.created_at).toLocaleDateString()}</div>
                </div>
              </div>

              <div>
                <label className="text-sm text-muted-foreground mb-2 block">Performance Metrics (Mock Data)</label>
                <Card>
                  <CardContent className="pt-6 space-y-4">
                    <div>
                      <div className="flex justify-between mb-2">
                        <span>Efficiency Score</span>
                        <span className="text-foreground">{selectedShipper.efficiency}%</span>
                      </div>
                      <Progress value={selectedShipper.efficiency} />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-muted-foreground">Total Deliveries</div>
                        <div className="text-xl text-foreground">{selectedShipper.totalDeliveries}</div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">Success Rate</div>
                        <div className="text-xl text-foreground">{selectedShipper.successRate}%</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setSelectedShipper(null)}>Close</Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}