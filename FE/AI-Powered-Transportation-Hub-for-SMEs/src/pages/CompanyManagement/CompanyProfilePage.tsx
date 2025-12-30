import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Separator } from '../../components/ui/separator';
import { Building2, Edit, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { smeService, type SME } from '../../services/smeService';

export function CompanyProfilePage() {
  const [profile, setProfile] = useState<SME | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // Dialog & Form State
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [editForm, setEditForm] = useState({
    business_name: '',
    tax_code: '',
    address: '',
    contact_phone: '',
    email: '',
    website: ''
  });

  // 1. Load Data
  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setIsLoading(true);
      const data = await smeService.getMyProfile();
      setProfile(data);
      // Init form data
      setEditForm({
        business_name: data.business_name,
        tax_code: data.tax_code,
        address: data.address,
        contact_phone: data.contact_phone,
        email: data.email,
        website: data.website || ''
      });
    } catch (error) {
      console.error("Failed to load profile:", error);
      toast.error("Không thể tải thông tin công ty");
    } finally {
      setIsLoading(false);
    }
  };

  // 2. Handle Update
  const handleUpdateProfile = async () => {
    if (!editForm.business_name || !editForm.tax_code) {
      toast.error("Vui lòng điền các trường bắt buộc");
      return;
    }

    setIsUpdating(true);
    try {
      const updatedData = await smeService.updateProfile(editForm);
      setProfile(updatedData);
      toast.success("Cập nhật thông tin thành công!");
      setIsEditDialogOpen(false);
    } catch (error: any) {
      console.error("Update failed:", error);
      toast.error(error.response?.data?.detail || "Cập nhật thất bại");
    } finally {
      setIsUpdating(false);
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-10"><Loader2 className="w-8 h-8 animate-spin text-primary"/></div>;
  }

  if (!profile) {
    return <div className="text-center py-10">Không tìm thấy thông tin doanh nghiệp.</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-foreground mb-1 text-2xl font-bold">Hồ Sơ Doanh Nghiệp</h1>
          <p className="text-muted-foreground">Quản lý thông tin và cài đặt công ty của bạn</p>
        </div>
        
        {/* Edit Dialog */}
        <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Edit className="w-4 h-4 mr-2" />
              Chỉnh Sửa Thông Tin
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Chỉnh Sửa Thông Tin Công Ty</DialogTitle>
              <DialogDescription>Cập nhật các chi tiết về doanh nghiệp của bạn.</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Tên Doanh Nghiệp *</Label>
                <Input 
                  value={editForm.business_name}
                  onChange={(e) => setEditForm({...editForm, business_name: e.target.value})}
                />
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Mã Số Thuế *</Label>
                  <Input 
                    value={editForm.tax_code}
                    onChange={(e) => setEditForm({...editForm, tax_code: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Website</Label>
                  <Input 
                    value={editForm.website}
                    onChange={(e) => setEditForm({...editForm, website: e.target.value})}
                    placeholder="https://..."
                  />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Địa Chỉ *</Label>
                <Input 
                  value={editForm.address}
                  onChange={(e) => setEditForm({...editForm, address: e.target.value})}
                />
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Email Liên Hệ</Label>
                  <Input 
                    type="email"
                    value={editForm.email}
                    onChange={(e) => setEditForm({...editForm, email: e.target.value})}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Số Điện Thoại</Label>
                  <Input 
                    value={editForm.contact_phone}
                    onChange={(e) => setEditForm({...editForm, contact_phone: e.target.value})}
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setIsEditDialogOpen(false)} disabled={isUpdating}>Hủy</Button>
              <Button onClick={handleUpdateProfile} disabled={isUpdating}>
                {isUpdating ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
                Lưu Thay Đổi
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Company Info Card */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Building2 className="w-5 h-5 text-primary" />
              <CardTitle>Thông Tin Chung</CardTitle>
            </div>
            <CardDescription>Chi tiết liên hệ và pháp lý</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-4">
              <div>
                <Label className="text-sm text-muted-foreground">Tên Công Ty</Label>
                <div className="text-foreground mt-1 font-medium text-lg">{profile.business_name}</div>
              </div>
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm text-muted-foreground">Mã Số Thuế</Label>
                  <div className="text-foreground mt-1 font-mono">{profile.tax_code}</div>
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">Website</Label>
                  <div className="text-foreground mt-1">
                    {profile.website ? (
                      <a href={profile.website} className="text-primary hover:underline" target="_blank" rel="noopener noreferrer">
                        {profile.website}
                      </a>
                    ) : 'Chưa cập nhật'}
                  </div>
                </div>
              </div>
              <div>
                <Label className="text-sm text-muted-foreground">Địa Chỉ Trụ Sở</Label>
                <div className="text-foreground mt-1">{profile.address}</div>
              </div>
              <Separator />
              <div className="grid sm:grid-cols-2 gap-4">
                <div>
                  <Label className="text-sm text-muted-foreground">Email</Label>
                  <div className="text-foreground mt-1">{profile.email}</div>
                </div>
                <div>
                  <Label className="text-sm text-muted-foreground">Điện Thoại</Label>
                  <div className="text-foreground mt-1">{profile.contact_phone}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* System Info Card */}
        <Card>
          <CardHeader>
            <CardTitle>Thông Tin Hệ Thống</CardTitle>
            <CardDescription>Trạng thái tài khoản và phân quyền</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
             <div className="flex justify-between items-center p-3 bg-muted rounded-lg">
                <span className="text-sm font-medium">Trạng Thái Hoạt Động</span>
                <span className={`px-2 py-1 rounded text-xs font-bold ${
                  profile.status === 'ACTIVE' ? 'bg-green-100 text-green-800' : 
                  profile.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'
                }`}>
                  {profile.status}
                </span>
             </div>
             <div className="p-3 border rounded-lg">
                <div className="text-sm text-muted-foreground mb-1">SME ID (Dùng cho API)</div>
                <div className="font-mono text-xs break-all">{profile.sme_id}</div>
             </div>
             <div className="p-3 border rounded-lg">
                <div className="text-sm text-muted-foreground mb-1">Ngày Tham Gia</div>
                <div>{new Date(profile.created_at).toLocaleDateString('vi-VN')}</div>
             </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}