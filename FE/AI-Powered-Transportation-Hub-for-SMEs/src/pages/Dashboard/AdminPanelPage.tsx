import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Search, CheckCircle, XCircle, Edit, Trash2, Plus, Building2, Users, RefreshCw, Filter, Shield, Truck, Package, Loader2, Radio } from 'lucide-react';
import { toast } from 'sonner';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { employeeService, Employee, EmployeeUpdate } from '../../services/employeeService';
import { warehouseService, Warehouse } from '../../services/warehouseService';
import { smeService, SME } from '../../services/smeService';

export function AdminPanelPage() {
  const navigate = useNavigate();

  // --- 1. QUẢN LÝ TAB ---
  const [activeTab, setActiveTab] = useState("businesses");

  // State: SME Management
  const [pendingSmes, setPendingSmes] = useState<SME[]>([]);
  const [activeSmeCount, setActiveSmeCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedCompany, setSelectedCompany] = useState<SME | null>(null);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [hasMore, setHasMore] = useState(true);

  // State: Active SME (Reports Tab)
  const [activeSmes, setActiveSmes] = useState<SME[]>([]);
  const [activePage, setActivePage] = useState(1);
  const [activeHasMore, setActiveHasMore] = useState(true);

  // State: Personnel (ALL EMPLOYEES)
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [empPage, setEmpPage] = useState(1);
  const [empLimit] = useState(10);
  const [empHasMore, setEmpHasMore] = useState(true);
  const [empSearchQuery, setEmpSearchQuery] = useState('');
  
  // State: Filter Role cho nhân sự
  const [selectedRoleFilter, setSelectedRoleFilter] = useState<string>('ALL'); 

  // State: Form Create Employee
  const [isAddEmpOpen, setIsAddEmpOpen] = useState(false);
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [newEmp, setNewEmp] = useState({
    full_name: '', 
    email: '', 
    phone: '', 
    dob: '', 
    warehouse_id: '', 
    username: '', 
    password: '', 
    role: 'WAREHOUSE_MANAGER',
    vehicle_type: 'MOTORBIKE' // Thêm cho Shipper
  });

  // --- STATE MỚI CHO EDIT EMPLOYEE ---
  const [isEditEmpOpen, setIsEditEmpOpen] = useState(false);
  const [editingEmp, setEditingEmp] = useState<Employee | null>(null);
  const [isUpdating, setIsUpdating] = useState(false);
  const [updateForm, setUpdateForm] = useState<EmployeeUpdate>({
    full_name: '',
    phone: '',
    status: 'ACTIVE',
    warehouse_id: undefined
  });

  // --- API CALLS ---

  const fetchWarehouses = async () => {
    try {
      const data = await warehouseService.getAllWarehouses();
      setWarehouses(data);
    } catch (error) {
      console.error("Failed to fetch warehouses", error);
    }
  };

  // FETCH TẤT CẢ NHÂN SỰ
  const fetchEmployeeData = async () => {
    if (activeTab === 'personnel') setIsLoading(true);
    try {
      const roleToFetch = selectedRoleFilter === 'ALL' ? undefined : selectedRoleFilter;

      const data = await employeeService.getAllEmployees(
        roleToFetch,  
        undefined,    
        empPage,      
        empLimit      
      );

      setEmployees(data);
      setEmpHasMore(data.length >= empLimit);
    } catch (error) {
      console.error("Failed to fetch Employees", error);
      toast.error("Lỗi tải danh sách nhân viên");
    } finally {
      if (activeTab === 'personnel') setIsLoading(false);
    }
  };

  const fetchPendingSmeData = async () => {
    if (activeTab === 'businesses') setIsLoading(true);
    try {
      const pending = await smeService.getSmesByStatus('PENDING', page, limit);
      setPendingSmes(pending);
      setHasMore(pending.length >= limit);
      const active = await smeService.getSmesByStatus('ACTIVE', 1, 1000);
      setActiveSmeCount(active.length);
    } catch (error) {
      toast.error("Không thể tải danh sách doanh nghiệp");
    } finally {
      if (activeTab === 'businesses') setIsLoading(false);
    }
  };

  const fetchActiveSmeData = async () => {
    if (activeTab === 'reports') setIsLoading(true);
    try {
      const activeList = await smeService.getSmesByStatus('ACTIVE', activePage, limit);
      setActiveSmes(activeList);
      setActiveHasMore(activeList.length >= limit);
    } catch (error) {
      toast.error("Lỗi tải danh sách đã duyệt");
    } finally {
      if (activeTab === 'reports') setIsLoading(false);
    }
  };

  // --- EFFECT ---
  useEffect(() => {
    if (activeTab === 'businesses') {
      fetchPendingSmeData();
    } else if (activeTab === 'personnel') {
      fetchWarehouses();
      fetchEmployeeData();
    } else if (activeTab === 'reports') {
      fetchActiveSmeData();
    }
  }, [activeTab, page, activePage, empPage, selectedRoleFilter]); 

  // --- HANDLERS ---
  const handleCreateEmployee = async () => {
    // Validation cơ bản
    if (!newEmp.full_name || !newEmp.email || !newEmp.phone || !newEmp.dob) {
      toast.error("Vui lòng điền đầy đủ thông tin bắt buộc (*)");
      return;
    }

    // Warehouse_id bắt buộc cho WAREHOUSE_MANAGER và WAREHOUSE_STAFF
    if (['WAREHOUSE_MANAGER', 'WAREHOUSE_STAFF', 'SHIPPER'].includes(newEmp.role) && !newEmp.warehouse_id) {
      toast.error("Vui lòng chọn kho cho vai trò này");
      return;
    }

    const finalUsername = newEmp.username.trim() || newEmp.email;
    const finalPassword = newEmp.password.trim() || "123456";

    try {
      setIsLoading(true);

      // Gọi API tùy theo role
      if (newEmp.role === 'WAREHOUSE_MANAGER') {
        await employeeService.createWarehouseManager({
          username: finalUsername,
          password: finalPassword,
          employee_data: {
            full_name: newEmp.full_name,
            email: newEmp.email,
            phone: newEmp.phone,
            dob: newEmp.dob,
            warehouse_id: newEmp.warehouse_id,
            role: newEmp.role,
          }
        });
      } else if (newEmp.role === 'DISPATCH') {
        await employeeService.createDispatch({
          username: finalUsername,
          password: finalPassword,
          employee_data: {
            full_name: newEmp.full_name,
            email: newEmp.email,
            phone: newEmp.phone,
            dob: newEmp.dob,
            warehouse_id: newEmp.warehouse_id || undefined,
            role: newEmp.role,
          }
        });
      } else if (['WAREHOUSE_STAFF', 'SHIPPER'].includes(newEmp.role)) {
        await employeeService.createStaff({
          username: finalUsername,
          password: finalPassword,
          full_name: newEmp.full_name,
          email: newEmp.email,
          phone: newEmp.phone,
          role: newEmp.role as 'WAREHOUSE_STAFF' | 'SHIPPER',
          warehouse_id: newEmp.warehouse_id,
          dob: newEmp.dob,
          vehicle_type: newEmp.role === 'SHIPPER' ? (newEmp.vehicle_type as 'MOTORBIKE' | 'TRUCK' | 'VAN') : undefined
        });
      }

      toast.success("Tạo nhân viên thành công!");
      setIsAddEmpOpen(false);
      setNewEmp({ 
        full_name: '', 
        email: '', 
        phone: '', 
        dob: '', 
        warehouse_id: '', 
        username: '', 
        password: '', 
        role: 'WAREHOUSE_MANAGER',
        vehicle_type: 'MOTORBIKE'
      });
      fetchEmployeeData(); 
    } catch (error: any) {
      toast.error(error.response?.data?.detail || "Lỗi khi tạo nhân viên");
    } finally {
      setIsLoading(false);
    }
  };

  // --- HANDLER MỚI: MỞ FORM EDIT ---
  const handleOpenEdit = (emp: Employee) => {
    setEditingEmp(emp);
    setUpdateForm({
      full_name: emp.full_name,
      phone: emp.phone,
      status: emp.status,
      warehouse_id: emp.warehouse_id || undefined
    });
    setIsEditEmpOpen(true);
  };

  // --- HANDLER MỚI: SUBMIT EDIT ---
  const handleUpdateEmployee = async () => {
    if (!editingEmp) return;
    setIsUpdating(true);
    try {
        await employeeService.updateEmployee(editingEmp.employee_id, updateForm);
        toast.success("Cập nhật thông tin thành công");
        
        // Cập nhật UI Local để không cần load lại API
        setEmployees(prev => prev.map(e => 
            e.employee_id === editingEmp.employee_id 
            ? { ...e, ...updateForm, warehouse_id: updateForm.warehouse_id || null } 
            : e
        ));
        
        setIsEditEmpOpen(false);
    } catch (error: any) {
        console.error(error);
        toast.error(error.response?.data?.detail || "Lỗi khi cập nhật");
    } finally {
        setIsUpdating(false);
    }
  };

  const handleApprove = async (sme: SME) => {
    try {
      await smeService.updateSmeStatus(sme.sme_id, 'ACTIVE');
      toast.success(`Đã duyệt: ${sme.business_name}`);
      fetchPendingSmeData();
      if (activeTab === 'reports') fetchActiveSmeData();
    } catch (error) { toast.error("Lỗi khi duyệt"); }
  };

  const handleReject = async (sme: SME) => {
    try {
      await smeService.updateSmeStatus(sme.sme_id, 'INACTIVE');
      toast.error(`Đã từ chối/khóa: ${sme.business_name}`);
      fetchPendingSmeData();
      if (activeTab === 'reports') fetchActiveSmeData();
    } catch (error) { toast.error("Lỗi khi thao tác"); }
  };

  // Pagination Handlers
  const handlePrevPage = () => setPage(p => Math.max(1, p - 1));
  const handleNextPage = () => setHasMore(prev => { if(prev) setPage(p => p + 1); return prev; });
  const handleActivePrev = () => setActivePage(p => Math.max(1, p - 1));
  const handleActiveNext = () => setActiveHasMore(prev => { if(prev) setActivePage(p => p + 1); return prev; });
  const handleEmpPrev = () => setEmpPage(p => Math.max(1, p - 1));
  const handleEmpNext = () => setEmpHasMore(prev => { if(prev) setEmpPage(p => p + 1); return prev; });

  const formatDate = (dateString: string) => dateString ? new Date(dateString).toLocaleDateString('vi-VN') : 'N/A';

  // Helper để hiển thị Role đẹp hơn - THÊM DISPATCH
  const getRoleBadge = (role: string) => {
    switch (role) {
      case 'ADMIN': return <Badge className="bg-red-100 text-red-800 border-red-200">ADMIN</Badge>;
      case 'WAREHOUSE_MANAGER': return <Badge className="bg-blue-100 text-blue-800 border-blue-200">MANAGER</Badge>;
      case 'WAREHOUSE_STAFF': return <Badge className="bg-cyan-100 text-cyan-800 border-cyan-200">STAFF</Badge>;
      case 'SHIPPER': return <Badge className="bg-orange-100 text-orange-800 border-orange-200">SHIPPER</Badge>;
      case 'DISPATCH': return <Badge className="bg-green-100 text-green-800 border-green-200">DISPATCH</Badge>;
      case 'SME_OWNER': return <Badge className="bg-purple-100 text-purple-800 border-purple-200">SME</Badge>;
      default: return <Badge variant="outline">{role}</Badge>;
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'ADMIN': return <Shield className="w-4 h-4 text-red-500" />;
      case 'SHIPPER': return <Truck className="w-4 h-4 text-orange-500" />;
      case 'DISPATCH': return <Radio className="w-4 h-4 text-green-500" />;
      case 'WAREHOUSE_MANAGER': 
      case 'WAREHOUSE_STAFF': return <Package className="w-4 h-4 text-blue-500" />;
      default: return <Users className="w-4 h-4 text-gray-500" />;
    }
  };

  // Filter tìm kiếm local
  const filteredEmployees = employees.filter(emp => 
    emp.full_name.toLowerCase().includes(empSearchQuery.toLowerCase()) ||
    emp.email.toLowerCase().includes(empSearchQuery.toLowerCase()) ||
    (emp.username && emp.username.toLowerCase().includes(empSearchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-foreground mb-1 text-2xl font-bold">Admin Panel</h1>
          <p className="text-muted-foreground">Hệ thống quản trị tập trung</p>
        </div>
        <Button variant="outline" size="icon" onClick={() => {
            if (activeTab === 'businesses') fetchPendingSmeData();
            if (activeTab === 'personnel') fetchEmployeeData();
            if (activeTab === 'reports') fetchActiveSmeData();
        }} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Chờ Duyệt</CardTitle></CardHeader>
          <CardContent><div className="text-2xl text-foreground font-bold">{pendingSmes.length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">SME Hoạt Động</CardTitle></CardHeader>
          <CardContent><div className="text-2xl text-foreground font-bold">{activeSmeCount}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Tổng Tài Khoản</CardTitle></CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground font-bold">{employees.length} +</div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="businesses" className="flex items-center gap-2">
            <Building2 className="w-4 h-4" /> Duyệt Doanh Nghiệp
          </TabsTrigger>
          <TabsTrigger value="personnel" className="flex items-center gap-2">
            <Users className="w-4 h-4" /> Tất Cả Nhân Sự
          </TabsTrigger>
          <TabsTrigger value="reports" className="flex items-center gap-2" >
            <Building2 className="w-4 h-4" /> Danh Sách SME
          </TabsTrigger>
        </TabsList>

        {/* --- TAB 1: PENDING SME --- */}
        <TabsContent value="businesses" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <CardTitle>Yêu Cầu Đăng Ký</CardTitle>
                  <CardDescription>Trang {page}</CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm" onClick={handlePrevPage} disabled={page === 1 || isLoading}><ChevronLeft className="h-4 w-4 mr-1"/>Trước</Button>
                  <Button variant="outline" size="sm" onClick={handleNextPage} disabled={!hasMore || isLoading}>Sau<ChevronRight className="h-4 w-4 ml-1"/></Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {isLoading && activeTab === 'businesses' ? <div className="text-center py-8">Đang tải...</div> : 
               pendingSmes.length === 0 ? <div className="text-center py-8 text-muted-foreground">Không có dữ liệu.</div> : 
               <div className="space-y-4">
                  {pendingSmes.map((company) => (
                    <Card key={company.sme_id} className="border shadow-sm">
                      <CardContent className="pt-6">
                        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-4">
                          <div className="flex-1 space-y-3">
                            <h3 className="text-foreground text-lg font-semibold">{company.business_name}</h3>
                            <div className="text-sm text-muted-foreground">{company.email} | MST: {company.tax_code}</div>
                            <div className="text-sm">Ngày tạo: {formatDate(company.created_at)}</div>
                          </div>
                          <div className="flex gap-2">
                            <Button variant="destructive" size="sm" onClick={() => handleReject(company)}>Từ chối</Button>
                            <Button variant="outline" size="sm" onClick={() => handleApprove(company)}>Duyệt</Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
               </div>
              }
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- TAB 2: ALL PERSONNEL - CẬP NHẬT DISPATCH --- */}
        <TabsContent value="personnel" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <CardTitle>Danh Sách Nhân Sự & Tài Khoản</CardTitle>
                  <CardDescription>Quản lý toàn bộ người dùng trong hệ thống (Trang {empPage})</CardDescription>
                </div>
                
                <div className="flex gap-2">
                    {/* Filter Role Dropdown - THÊM DISPATCH */}
                    <Select value={selectedRoleFilter} onValueChange={(val) => {
                        setSelectedRoleFilter(val);
                        setEmpPage(1);
                    }}>
                        <SelectTrigger className="w-[180px]">
                            <Filter className="w-4 h-4 mr-2" />
                            <SelectValue placeholder="Lọc theo Role" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="ALL">Tất cả Roles</SelectItem>
                            <SelectItem value="ADMIN">Admin</SelectItem>
                            <SelectItem value="WAREHOUSE_MANAGER">Quản lý kho</SelectItem>
                            <SelectItem value="WAREHOUSE_STAFF">Nhân viên kho</SelectItem>
                            <SelectItem value="SHIPPER">Tài xế (Shipper)</SelectItem>
                            <SelectItem value="DISPATCH">Điều phối viên</SelectItem>
                            <SelectItem value="SME_OWNER">Chủ hàng (SME)</SelectItem>
                        </SelectContent>
                    </Select>

                    <Button size="sm" onClick={() => setIsAddEmpOpen(true)}>
                    <Plus className="w-4 h-4 mr-2" /> Tạo Mới
                    </Button>
                </div>

                {/* Dialog CREATE Form - CẬP NHẬT */}
                <Dialog open={isAddEmpOpen} onOpenChange={setIsAddEmpOpen}>
                  <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto">
                    <DialogHeader>
                      <DialogTitle>Tạo Tài Khoản Nhân Viên Mới</DialogTitle>
                      <DialogDescription>Hỗ trợ tạo: Manager, Staff, Shipper, Dispatch</DialogDescription>
                    </DialogHeader>
                     <div className="space-y-4 py-4">
                      {/* Chọn Role trước */}
                      <div className="space-y-2">
                        <Label className="text-red-600">Loại Nhân Viên (*)</Label>
                        <Select value={newEmp.role} onValueChange={(value) => setNewEmp({...newEmp, role: value})}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="WAREHOUSE_MANAGER">Quản Lý Kho (Manager)</SelectItem>
                            <SelectItem value="WAREHOUSE_STAFF">Nhân Viên Kho (Staff)</SelectItem>
                            <SelectItem value="SHIPPER">Tài Xế (Shipper)</SelectItem>
                            <SelectItem value="DISPATCH">Điều Phối Viên (Dispatch)</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-red-600">Họ và tên (*)</Label>
                          <Input value={newEmp.full_name} onChange={(e) => setNewEmp({...newEmp, full_name: e.target.value})} />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-red-600">Ngày sinh (*)</Label>
                          <Input type="date" value={newEmp.dob} onChange={(e) => setNewEmp({...newEmp, dob: e.target.value})} />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label className="text-red-600">Email (*)</Label>
                          <Input type="email" value={newEmp.email} onChange={(e) => setNewEmp({...newEmp, email: e.target.value})} />
                        </div>
                        <div className="space-y-2">
                          <Label className="text-red-600">SĐT (*)</Label>
                          <Input value={newEmp.phone} onChange={(e) => setNewEmp({...newEmp, phone: e.target.value})} />
                        </div>
                      </div>

                      {/* Warehouse - Chỉ hiện với Manager, Staff, Shipper */}
                      {['WAREHOUSE_MANAGER', 'WAREHOUSE_STAFF', 'SHIPPER'].includes(newEmp.role) && (
                        <div className="space-y-2">
                          <Label className="text-red-600">Kho Làm Việc (*)</Label>
                          <Select value={newEmp.warehouse_id} onValueChange={(value) => setNewEmp({...newEmp, warehouse_id: value})}>
                            <SelectTrigger><SelectValue placeholder="Chọn kho" /></SelectTrigger>
                            <SelectContent>
                              {warehouses.map((wh) => (
                                <SelectItem key={wh.warehouse_id} value={wh.warehouse_id}>{wh.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      )}

                      {/* Dispatch có thể chọn kho hoặc không */}
                      {newEmp.role === 'DISPATCH' && (
                        <div className="space-y-2">
                          <Label>Kho Phụ Trách (Tùy chọn)</Label>
                          <Select 
                            value={newEmp.warehouse_id || "NONE"} 
                            onValueChange={(value) => setNewEmp({...newEmp, warehouse_id: value === "NONE" ? "" : value})}
                          >
                            <SelectTrigger><SelectValue placeholder="Không gán kho" /></SelectTrigger>
                            <SelectContent>
                              <SelectItem value="NONE">Không gán</SelectItem>
                              {warehouses.map((wh) => (
                                <SelectItem key={wh.warehouse_id} value={wh.warehouse_id}>{wh.name}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      )}

                      {/* Vehicle Type - Chỉ cho Shipper */}
                      {newEmp.role === 'SHIPPER' && (
                        <div className="space-y-2">
                          <Label className="text-red-600">Loại Phương Tiện (*)</Label>
                          <Select value={newEmp.vehicle_type} onValueChange={(value) => setNewEmp({...newEmp, vehicle_type: value})}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent>
                              <SelectItem value="MOTORBIKE">Xe Máy</SelectItem>
                              <SelectItem value="VAN">Xe Van</SelectItem>
                              <SelectItem value="TRUCK">Xe Tải</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      )}

                      <hr className="border-t border-dashed my-2" />
                      
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Username (Tùy chọn)</Label>
                          <Input placeholder="Mặc định: Email" value={newEmp.username} onChange={(e) => setNewEmp({...newEmp, username: e.target.value})} />
                        </div>
                        <div className="space-y-2">
                          <Label>Password (Tùy chọn)</Label>
                          <Input type="password" placeholder="Mặc định: 123456" value={newEmp.password} onChange={(e) => setNewEmp({...newEmp, password: e.target.value})} />
                        </div>
                      </div>
                    </div>
                    <div className="flex justify-end gap-2">
                      <Button variant="outline" onClick={() => setIsAddEmpOpen(false)}>Hủy</Button>
                      <Button onClick={handleCreateEmployee} disabled={isLoading}>
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Tạo Mới'}
                      </Button>
                    </div>
                  </DialogContent>
                </Dialog>

                {/* --- DIALOG EDIT EMPLOYEE --- */}
                <Dialog open={isEditEmpOpen} onOpenChange={setIsEditEmpOpen}>
                    <DialogContent className="max-w-md">
                        <DialogHeader>
                            <DialogTitle>Chỉnh Sửa Nhân Viên</DialogTitle>
                            <DialogDescription>Cập nhật trạng thái và thông tin</DialogDescription>
                        </DialogHeader>
                        
                        <div className="space-y-4 py-2">
                            <div className="space-y-2">
                                <Label>Họ Tên</Label>
                                <Input 
                                    value={updateForm.full_name} 
                                    onChange={(e) => setUpdateForm({...updateForm, full_name: e.target.value})}
                                />
                            </div>
                            <div className="space-y-2">
                                <Label>Số Điện Thoại</Label>
                                <Input 
                                    value={updateForm.phone} 
                                    onChange={(e) => setUpdateForm({...updateForm, phone: e.target.value})}
                                />
                            </div>
                            
                            <div className="space-y-2">
                                <Label>Kho Phụ Trách (Optional)</Label>
                                <Select 
                                    value={updateForm.warehouse_id || "none"} 
                                    onValueChange={(val) => setUpdateForm({...updateForm, warehouse_id: val === "none" ? undefined : val})}
                                >
                                    <SelectTrigger><SelectValue placeholder="Chọn kho" /></SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="none">Không gán kho</SelectItem>
                                        {warehouses.map((wh) => (
                                            <SelectItem key={wh.warehouse_id} value={wh.warehouse_id}>{wh.name}</SelectItem>
                                        ))}
                                    </SelectContent>
                                </Select>
                            </div>

                            <div className="space-y-2">
                                <Label>Trạng Thái Hoạt Động</Label>
                                <Select 
                                    value={updateForm.status} 
                                    onValueChange={(val) => setUpdateForm({...updateForm, status: val})}
                                >
                                    <SelectTrigger>
                                        <SelectValue />
                                    </SelectTrigger>
                                    <SelectContent>
                                        <SelectItem value="ACTIVE">
                                            <div className="flex items-center gap-2 text-green-600">
                                                <CheckCircle className="w-4 h-4" /> Hoạt Động (Active)
                                            </div>
                                        </SelectItem>
                                        <SelectItem value="INACTIVE">
                                            <div className="flex items-center gap-2 text-red-600">
                                                <XCircle className="w-4 h-4" /> Vô Hiệu Hóa (Inactive)
                                            </div>
                                        </SelectItem>
                                    </SelectContent>
                                </Select>
                            </div>
                        </div>

                        <DialogFooter>
                            <Button variant="outline" onClick={() => setIsEditEmpOpen(false)}>Hủy</Button>
                            <Button onClick={handleUpdateEmployee} disabled={isUpdating}>
                                {isUpdating ? <Loader2 className="w-4 h-4 animate-spin" /> : "Lưu Thay Đổi"}
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>

              </div>
            </CardHeader>

            <CardContent>
               <div className="flex justify-between items-center mb-4 gap-4">
                 <div className="relative flex-1 max-w-sm">
                   <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                   <Input placeholder="Tìm tên, email, username..." className="pl-9" value={empSearchQuery} onChange={(e) => setEmpSearchQuery(e.target.value)} />
                 </div>
                 <div className="flex gap-2">
                   <Button variant="outline" size="sm" onClick={handleEmpPrev} disabled={empPage === 1 || isLoading}><ChevronLeft className="w-4 h-4"/></Button>
                   <Button variant="outline" size="sm" onClick={handleEmpNext} disabled={!empHasMore || isLoading}><ChevronRight className="w-4 h-4"/></Button>
                 </div>
               </div>

              <div className="overflow-x-auto border rounded-md">
                 <table className="w-full text-sm">
                  <thead className="bg-muted/50">
                    <tr className="border-b">
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Nhân Sự</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Vai Trò (Role)</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Liên Hệ</th>
                      <th className="text-left py-3 px-4 font-medium text-muted-foreground">Trạng Thái</th>
                      <th className="text-right py-3 px-4 font-medium text-muted-foreground">Hành Động</th>
                    </tr>
                  </thead>
                  <tbody>
                    {isLoading && activeTab === 'personnel' ? (
                      <tr><td colSpan={5} className="text-center py-8">Đang tải dữ liệu...</td></tr>
                    ) : filteredEmployees.length === 0 ? (
                      <tr><td colSpan={5} className="text-center py-8 text-muted-foreground">Không tìm thấy nhân sự nào.</td></tr>
                    ) : (
                      filteredEmployees.map((emp) => (
                        <tr key={emp.employee_id} className="border-b hover:bg-muted/50">
                           <td className="py-3 px-4">
                             <div className="font-medium flex items-center gap-2">
                                {getRoleIcon(emp.role)}
                                {emp.full_name}
                             </div>
                             <div className="text-xs text-muted-foreground ml-6">User: {emp.username}</div>
                           </td>
                           <td className="py-3 px-4">
                              {getRoleBadge(emp.role)}
                              {emp.warehouse_id && <div className="text-xs text-muted-foreground mt-1">Kho: {emp.warehouse_id}</div>}
                           </td>
                           <td className="py-3 px-4">
                             <div>{emp.email}</div>
                             <div className="text-xs text-muted-foreground">{emp.phone}</div>
                           </td>
                           <td className="py-3 px-4">
                              <Badge className={emp.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                                {emp.status}
                              </Badge>
                           </td>
                           <td className="py-3 px-4 text-right">
                                <Button 
                                    variant="ghost" 
                                    size="icon" 
                                    onClick={() => handleOpenEdit(emp)}
                                >
                                    <Edit className="w-4 h-4 text-blue-600" />
                                </Button>
                           </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                 </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* --- TAB 3: REPORTS (ACTIVE BUSINESSES) --- */}
        <TabsContent value="reports" className="space-y-4">
           <Card>
            <CardHeader>
              <div className="flex justify-between items-center">
                <CardTitle>Doanh Nghiệp Đang Hoạt Động</CardTitle>
                <div className="flex gap-2">
                   <Button variant="outline" size="sm" onClick={handleActivePrev} disabled={activePage === 1}><ChevronLeft className="w-4 h-4"/></Button>
                   <Button variant="outline" size="sm" onClick={handleActiveNext} disabled={!activeHasMore}><ChevronRight className="w-4 h-4"/></Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
               {isLoading && activeTab === 'reports' ? <div>Đang tải...</div> : 
                 <div className="space-y-4">
                    {activeSmes.map(company => (
                       <Card key={company.sme_id} className="border-green-200 border">
                          <CardContent className="pt-4 pb-4">
                             <div className="flex justify-between">
                                <span className="font-bold">{company.business_name}</span>
                                <Badge className="bg-green-100 text-green-800">ACTIVE</Badge>
                             </div>
                             <div className="text-sm text-muted-foreground mt-1">{company.email}</div>
                          </CardContent>
                       </Card>
                    ))}
                 </div>
               }
            </CardContent>
           </Card>
        </TabsContent>
      </Tabs>

      {/* Dialog Detail */}
      {selectedCompany && (
        <Dialog open={!!selectedCompany} onOpenChange={() => setSelectedCompany(null)}>
           <DialogContent><DialogTitle>{selectedCompany.business_name}</DialogTitle>
             <div className="py-4">Chi tiết: {selectedCompany.address} - {selectedCompany.phone}</div>
           </DialogContent>
        </Dialog>
      )}
    </div>
  );
}