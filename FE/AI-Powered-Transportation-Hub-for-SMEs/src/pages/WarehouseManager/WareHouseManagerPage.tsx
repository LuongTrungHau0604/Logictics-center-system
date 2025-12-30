import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../components/ui/table';
import { Badge } from '../../components/ui/badge';
import { Plus, Search, Loader2, Truck, Package, User, Pencil } from 'lucide-react'; // Thêm icon Pencil
import { employeeService, Employee, CreateStaffRequest } from '../../services/employeeService';
import { warehouseService } from '../../services/warehouseService'; 
import { authService } from '../../services/authService';
import { toast } from 'sonner';

export function WarehouseStaffPage() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [warehouses, setWarehouses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('ALL');
  const [currentUser, setCurrentUser] = useState<any>(null);

  // Dialog & Form State
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null); // State mới để track ID đang sửa

  const defaultFormData: CreateStaffRequest = {
    username: '', password: '', full_name: '', email: '', phone: '',
    role: 'WAREHOUSE_STAFF', warehouse_id: '', dob: '', vehicle_type: 'MOTORBIKE'
  };

  // Thêm field status vào state form (dù CreateStaffRequest ko có, ta dùng tạm để handle UI edit)
  const [formData, setFormData] = useState<CreateStaffRequest & { status?: string }>(defaultFormData);

  useEffect(() => {
    const user = authService.getCurrentUser();
    setCurrentUser(user);
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [empRes, whRes] = await Promise.all([
        employeeService.getAllEmployees(),
        warehouseService.getAllWarehouses() 
      ]);
      setEmployees(empRes);
      setWarehouses(whRes);
    } catch (error) {
      toast.error("Failed to load data");
    } finally {
      setIsLoading(false);
    }
  };

  // Hàm reset form về trạng thái thêm mới
  const resetForm = () => {
    setFormData(defaultFormData);
    setEditingId(null);
  };

  // Hàm xử lý khi bấm nút Edit
  const handleEdit = (emp: Employee) => {
    setEditingId(emp.employee_id);
    setFormData({
      username: 'READONLY', // Username không sửa được
      password: '',        // Password không sửa ở đây
      full_name: emp.full_name,
      email: emp.email,
      phone: emp.phone,
      role: emp.role as 'WAREHOUSE_STAFF' | 'SHIPPER',
      warehouse_id: emp.warehouse_id || '',
      dob: emp.dob ? emp.dob.split('T')[0] : '', // Format date nếu cần
      status: emp.status, // Load status hiện tại
      vehicle_type: 'MOTORBIKE' // Mặc định hoặc lấy từ API nếu backend trả về (hiện tại interface Employee chưa thấy field này)
    });
    setIsDialogOpen(true);
  };

  // Hàm mở dialog thêm mới
  const handleCreateOpen = () => {
    resetForm();
    setIsDialogOpen(true);
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (editingId) {
        // --- LOGIC UPDATE ---
        await employeeService.updateEmployee(editingId, {
          full_name: formData.full_name,
          dob: formData.dob,
          role: formData.role,
          phone: formData.phone,
          status: formData.status, // Gửi status cập nhật
          warehouse_id: formData.warehouse_id
        });
        toast.success("Staff updated successfully!");
      } else {
        // --- LOGIC CREATE ---
        await employeeService.createStaff(formData);
        toast.success("Staff created successfully!");
      }

      setIsDialogOpen(false);
      resetForm();
      loadData(); 
    } catch (error: any) {
      console.error(error);
      toast.error(error.response?.data?.detail || `Failed to ${editingId ? 'update' : 'create'} staff`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const filteredEmployees = employees.filter(emp => {
    const searchLower = searchQuery.toLowerCase();
    const matchesSearch = emp.full_name.toLowerCase().includes(searchLower) || 
                          emp.email.toLowerCase().includes(searchLower) ||
                          emp.phone.includes(searchLower);
    const matchesRole = roleFilter === 'ALL' || emp.role === roleFilter;
    const isOperational = ['WAREHOUSE_STAFF', 'SHIPPER'].includes(emp.role);
    return matchesSearch && matchesRole && isOperational;
  });

  const isManager = currentUser?.role === 'WAREHOUSE_MANAGER';

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Operational Staff</h1>
          <p className="text-muted-foreground">Manage warehouse staff and delivery shippers.</p>
        </div>
        
        <Dialog open={isDialogOpen} onOpenChange={(open) => {
            setIsDialogOpen(open);
            if (!open) resetForm(); // Reset khi đóng dialog
        }}>
          <DialogTrigger asChild>
            <Button onClick={handleCreateOpen}>
              <Plus className="w-4 h-4 mr-2" />
              Add Staff / Shipper
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>{editingId ? 'Edit Personnel' : 'Add New Personnel'}</DialogTitle>
              <DialogDescription>
                {editingId ? 'Update employee details and status.' : 'Create account and assign role for warehouse operations.'}
              </DialogDescription>
            </DialogHeader>

            <form onSubmit={handleSubmit} className="space-y-4 py-2">
              {/* Account Info - Chỉ hiện khi Thêm mới */}
              {!editingId && (
                <div className="grid grid-cols-2 gap-4 p-4 bg-muted/30 rounded-lg border">
                  <div className="space-y-2">
                    <Label>Username <span className="text-red-500">*</span></Label>
                    <Input required minLength={3}
                      value={formData.username}
                      onChange={e => setFormData({...formData, username: e.target.value})}
                      placeholder="e.g. john_doe"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Password <span className="text-red-500">*</span></Label>
                    <Input type="password" required minLength={6}
                      value={formData.password}
                      onChange={e => setFormData({...formData, password: e.target.value})}
                      placeholder="******"
                    />
                  </div>
                </div>
              )}

              {/* Personal Info */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Full Name <span className="text-red-500">*</span></Label>
                  <Input required 
                    value={formData.full_name}
                    onChange={e => setFormData({...formData, full_name: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Date of Birth</Label>
                  <Input type="date" 
                    value={formData.dob}
                    onChange={e => setFormData({...formData, dob: e.target.value})}
                  />
                </div>
                {/* Email thường không cho sửa trực tiếp để tránh lỗi auth */}
                <div className="space-y-2">
                  <Label>Email <span className="text-red-500">*</span></Label>
                  <Input type="email" required disabled={!!editingId}
                    value={formData.email}
                    onChange={e => setFormData({...formData, email: e.target.value})}
                    className={editingId ? "bg-muted text-muted-foreground" : ""}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Phone <span className="text-red-500">*</span></Label>
                  <Input required 
                    value={formData.phone}
                    onChange={e => setFormData({...formData, phone: e.target.value})}
                  />
                </div>
              </div>

              {/* Role & Status Selection */}
              <div className="grid grid-cols-2 gap-4 border-t pt-4">
                <div className="space-y-2">
                  <Label>Role <span className="text-red-500">*</span></Label>
                  <Select 
                    value={formData.role}
                    onValueChange={(val: any) => setFormData({...formData, role: val})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="WAREHOUSE_STAFF">Warehouse Staff</SelectItem>
                      <SelectItem value="SHIPPER">Shipper</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Warehouse <span className="text-red-500">*</span></Label>
                  {isManager ? (
                    <div className="h-10 px-3 py-2 w-full border rounded-md bg-muted text-muted-foreground text-sm flex items-center cursor-not-allowed">
                       {/* Hiển thị tên kho hiện tại nếu tìm thấy, hoặc text */}
                       Current Warehouse
                    </div>
                  ) : (
                    <Select 
                      value={formData.warehouse_id}
                      onValueChange={(val) => setFormData({...formData, warehouse_id: val})}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select warehouse" />
                      </SelectTrigger>
                      <SelectContent>
                        {warehouses.map(wh => (
                          <SelectItem key={wh.warehouse_id} value={wh.warehouse_id}>
                            {wh.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  )}
                </div>
              </div>
              
              {/* Chỉ hiện Status khi đang Edit */}
              {editingId && (
                <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                    <Label>Status</Label>
                    <Select 
                        value={formData.status || 'ACTIVE'}
                        onValueChange={(val: any) => setFormData({...formData, status: val})}
                    >
                        <SelectTrigger>
                        <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                        <SelectItem value="ACTIVE">Active</SelectItem>
                        <SelectItem value="INACTIVE">Inactive</SelectItem>
                        <SelectItem value="LOCKED">Locked</SelectItem>
                        </SelectContent>
                    </Select>
                    </div>
                </div>
              )}

              {/* Shipper Specific Fields - Chỉ hiện khi chọn Shipper và đang KHÔNG edit (hoặc Edit nếu BE hỗ trợ update xe) */}
              {formData.role === 'SHIPPER' && !editingId && (
                <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg border border-blue-100 dark:border-blue-800 space-y-3 animate-in slide-in-from-top-2">
                  <div className="flex items-center gap-2 text-blue-700 dark:text-blue-400 font-medium text-sm">
                    <Truck className="w-4 h-4" /> Shipper Details
                  </div>
                  <div className="space-y-2">
                    <Label>Vehicle Type</Label>
                    <Select 
                      value={formData.vehicle_type}
                      onValueChange={(val: any) => setFormData({...formData, vehicle_type: val})}
                    >
                      <SelectTrigger className="bg-white dark:bg-background">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MOTORBIKE">Motorbike</SelectItem>
                        <SelectItem value="TRUCK">Truck</SelectItem>
                        <SelectItem value="VAN">Van</SelectItem>
                        <SelectItem value="BICYCLE">Bicycle</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}

              <div className="flex justify-end gap-2 pt-4">
                <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {editingId ? 'Update Changes' : 'Create Employee'}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        {/* ... (Phần Header Search giữ nguyên) ... */}
        <CardHeader>
          <div className="flex items-center gap-4">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name, email or phone..."
                className="pl-9"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by Role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="ALL">All Roles</SelectItem>
                <SelectItem value="WAREHOUSE_STAFF">Warehouse Staff</SelectItem>
                <SelectItem value="SHIPPER">Shipper</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>

        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Employee</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Contact Info</TableHead>
                <TableHead>Warehouse</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Action</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center h-32">
                    <Loader2 className="w-8 h-8 animate-spin mx-auto text-muted-foreground" />
                  </TableCell>
                </TableRow>
              ) : filteredEmployees.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center h-32 text-muted-foreground">
                    No staff found match your criteria.
                  </TableCell>
                </TableRow>
              ) : (
                filteredEmployees.map((emp) => (
                  <TableRow key={emp.employee_id}>
                    <TableCell>
                      <div className="font-medium text-foreground">{emp.full_name}</div>
                      <div className="text-xs text-muted-foreground flex items-center gap-1">
                        <User className="w-3 h-3" /> {emp.employee_id}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={emp.role === 'SHIPPER' ? 'secondary' : 'outline'} className="font-normal">
                        {emp.role === 'SHIPPER' ? <Truck className="w-3 h-3 mr-1" /> : <Package className="w-3 h-3 mr-1" />}
                        {emp.role.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">{emp.email}</div>
                      <div className="text-xs text-muted-foreground">{emp.phone}</div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline" className="bg-muted/50 font-mono text-xs border-dashed">
                        {warehouses.find(w => w.warehouse_id === emp.warehouse_id)?.name || emp.warehouse_id || 'N/A'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={emp.status === 'ACTIVE' ? 'default' : 'destructive'} className="text-[10px]">
                        {emp.status}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      {/* Đã thêm sự kiện onClick vào nút Edit */}
                      <Button variant="ghost" size="sm" onClick={() => handleEdit(emp)}>
                        <Pencil className="w-4 h-4 mr-1"/> Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}