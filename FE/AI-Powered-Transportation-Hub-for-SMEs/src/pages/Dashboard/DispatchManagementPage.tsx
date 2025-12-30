// src/pages/Dashboard/DispatchManagementPage.tsx
import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { Input } from '../../components/ui/input'; // [UPDATE] Import Input
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../../components/ui/tabs';
import { Package, User, Warehouse, MapPin, CheckCircle, AlertCircle, Truck, Loader2, ArrowRight, Edit, Trash2, Settings, CheckSquare, Search } from 'lucide-react'; // [UPDATE] Import Search Icon
import { toast } from 'sonner';

// Import service
import { journeyLegService, Order, Shipper, JourneyLeg } from '../../services/journeyLegService';
import { warehouseService, Warehouse as WarehouseType } from '../../services/warehouseService';

interface OrderWithJourney extends Order {
  legs?: JourneyLeg[];
}

interface EditLegData {
  leg: JourneyLeg;
  order: OrderWithJourney;
}

export function DispatchManagementPage() {
  // States
  const [isLoading, setIsLoading] = useState(true);
  const [currentTab, setCurrentTab] = useState<'pickup' | 'transfer' | 'delivery' | 'completed' | 'manage'>('pickup');
  const [searchTerm, setSearchTerm] = useState(''); // [UPDATE] State tìm kiếm
  
  // Tab data
  const [pickupOrders, setPickupOrders] = useState<OrderWithJourney[]>([]);
  const [transferOrders, setTransferOrders] = useState<OrderWithJourney[]>([]);
  const [deliveryOrders, setDeliveryOrders] = useState<OrderWithJourney[]>([]);
  const [completedOrders, setCompletedOrders] = useState<OrderWithJourney[]>([]);
  const [allOrders, setAllOrders] = useState<OrderWithJourney[]>([]);
  
  const [selectedOrder, setSelectedOrder] = useState<OrderWithJourney | null>(null);
  
  // Dialog States
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingLeg, setEditingLeg] = useState<EditLegData | null>(null);
  
  const [availableShippers, setAvailableShippers] = useState<Shipper[]>([]);
  const [warehouses, setWarehouses] = useState<WarehouseType[]>([]);
  
  const [selectedShipper, setSelectedShipper] = useState<string>('');
  const [selectedWarehouse, setSelectedWarehouse] = useState<string>('');
  const [selectedStatus, setSelectedStatus] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Load initial data
  useEffect(() => {
    loadOrdersWithJourney();
    loadWarehouses();
  }, []);

  const loadOrdersWithJourney = async () => {
    setIsLoading(true);
    try {
      const orders = await journeyLegService.getAllOrders(); 
      
      const ordersWithLegs = await Promise.all(
        orders.map(async (order) => {
          try {
            const legs = await journeyLegService.getOrderLegs(order.order_id);
            return { ...order, legs };
          } catch {
            return { ...order, legs: [] };
          }
        })
      );
      
      const pickup: OrderWithJourney[] = [];
      const transfer: OrderWithJourney[] = [];
      const delivery: OrderWithJourney[] = [];
      const completed: OrderWithJourney[] = [];
      
      ordersWithLegs.forEach(order => {
        const deliveryLeg = order.legs?.find(l => l.leg_type === 'DELIVERY');
        if (order.status === 'COMPLETED' || (deliveryLeg && deliveryLeg.status === 'COMPLETED')) {
          completed.push(order);
        }

        if (!order.legs || order.legs.length === 0) {
          pickup.push(order);
          return;
        }
        
        const pickupLeg = order.legs.find(l => l.leg_type === 'PICKUP');
        const transferLeg = order.legs.find(l => l.leg_type === 'TRANSFER');
        
        if (pickupLeg && !pickupLeg.assigned_shipper_id && pickupLeg.status !== 'COMPLETED') {
          pickup.push(order);
        }
        else if (pickupLeg?.assigned_shipper_id && transferLeg && !transferLeg.assigned_shipper_id && transferLeg.status !== 'COMPLETED') {
          transfer.push(order);
        }
        else if (transferLeg?.assigned_shipper_id && deliveryLeg && !deliveryLeg.assigned_shipper_id && deliveryLeg.status !== 'COMPLETED') {
          delivery.push(order);
        }
      });
      
      setPickupOrders(pickup);
      setTransferOrders(transfer);
      setDeliveryOrders(delivery);
      setCompletedOrders(completed);
      setAllOrders(ordersWithLegs.filter(o => o.legs && o.legs.length > 0));
    } catch (error) {
      console.error('Failed to load orders:', error);
      toast.error('Không thể tải danh sách đơn hàng');
    } finally {
      setIsLoading(false);
    }
  };

  const loadWarehouses = async () => {
    try {
      const data = await warehouseService.getAllWarehouses();
      setWarehouses(data);
    } catch (error) {
      console.error('Failed to load warehouses:', error);
    }
  };

  // [UPDATE] Hàm lọc chung cho danh sách
  const filterList = (list: OrderWithJourney[]) => {
    if (!searchTerm) return list;
    const lowerTerm = searchTerm.toLowerCase().trim();
    return list.filter(order => 
      order.order_code.toLowerCase().includes(lowerTerm) || 
      order.receiver_name.toLowerCase().includes(lowerTerm) // Tìm luôn theo tên người nhận cho tiện
    );
  };

  // ... (Giữ nguyên các hàm handlePickupOrder, handleTransferOrder, handleDeliveryOrder, handleEditLeg, handleDeleteLeg, handleSaveEditedLeg, handleAssignOrder)
  // Để tiết kiệm không gian tôi sẽ ẩn chi tiết các hàm logic không đổi, bạn giữ nguyên code logic cũ nhé.
  const handlePickupOrder = async (order: OrderWithJourney) => { setSelectedOrder(order); setSelectedShipper(''); setSelectedWarehouse(''); if (order.area_id) { try { const shippers = await journeyLegService.getShippersByArea(order.area_id); setAvailableShippers(shippers); } catch { toast.error('Không thể tải danh sách shipper'); setAvailableShippers([]); } } else { toast.warning('Đơn hàng chưa có thông tin khu vực'); setAvailableShippers([]); } setIsDialogOpen(true); };
  const handleTransferOrder = async (order: OrderWithJourney) => { setSelectedOrder(order); setSelectedShipper(''); setSelectedWarehouse(''); if (order.area_id) { try { let shippers = await journeyLegService.getShippersByArea(order.area_id); const trucksOnly = shippers.filter(s => ['TRUCK', 'CAR'].includes(s.vehicle_type)); if (trucksOnly.length === 0) toast.error(`Không có xe tải/xe hơi khả dụng trong khu vực ${order.area_id}`); setAvailableShippers(trucksOnly); } catch { toast.error('Không thể tải danh sách shipper'); setAvailableShippers([]); } } setIsDialogOpen(true); };
  const handleDeliveryOrder = async (order: OrderWithJourney) => { setSelectedOrder(order); setSelectedShipper(''); setSelectedWarehouse(''); if (order.area_id) { try { const shippers = await journeyLegService.getShippersByArea(order.area_id); setAvailableShippers(shippers); } catch { toast.error('Không thể tải danh sách shipper'); setAvailableShippers([]); } } else { toast.warning('Đơn hàng chưa có thông tin khu vực'); setAvailableShippers([]); } setIsDialogOpen(true); };
  const handleEditLeg = async (leg: JourneyLeg, order: OrderWithJourney) => { setEditingLeg({ leg, order }); setSelectedShipper(leg.assigned_shipper_id || ''); setSelectedWarehouse(leg.destination_warehouse_id || ''); setSelectedStatus(leg.status); if (order.area_id) { try { const shippers = await journeyLegService.getShippersByArea(order.area_id); let filteredShippers = shippers; if (leg.leg_type === 'TRANSFER') { filteredShippers = shippers.filter(s => ['TRUCK', 'CAR'].includes(s.vehicle_type)); } setAvailableShippers(filteredShippers); } catch { toast.error('Không thể tải danh sách shipper'); setAvailableShippers([]); } } setIsEditDialogOpen(true); };
  const handleDeleteLeg = async (legId: number, orderCode: string) => { if (!confirm(`Bạn có chắc muốn xóa leg này của đơn ${orderCode}?`)) return; try { await journeyLegService.deleteJourneyLeg(legId); toast.success('✅ Đã xóa leg thành công'); await loadOrdersWithJourney(); } catch (error: any) { toast.error(error.response?.data?.detail || 'Không thể xóa leg'); } };
  const handleSaveEditedLeg = async () => { if (!editingLeg) return; setIsProcessing(true); try { const updates: any = {}; if (selectedShipper !== editingLeg.leg.assigned_shipper_id) updates.assigned_shipper_id = selectedShipper || null; if (selectedWarehouse !== editingLeg.leg.destination_warehouse_id) updates.destination_warehouse_id = selectedWarehouse || null; if (selectedStatus !== editingLeg.leg.status) updates.status = selectedStatus; if (Object.keys(updates).length === 0) { toast.info('Không có thay đổi nào'); setIsEditDialogOpen(false); return; } await journeyLegService.updateJourneyLeg(editingLeg.leg.id, updates); toast.success('✅ Cập nhật leg thành công!'); setIsEditDialogOpen(false); await loadOrdersWithJourney(); } catch (error: any) { toast.error(error.response?.data?.detail || 'Lỗi khi cập nhật leg'); } finally { setIsProcessing(false); } };
  const handleAssignOrder = async () => { if (!selectedOrder || !selectedShipper) { toast.error('Vui lòng chọn đầy đủ thông tin'); return; } if (currentTab === 'pickup' && !selectedWarehouse) { toast.error('Vui lòng chọn Kho Hub đích'); return; } setIsProcessing(true); try { if (currentTab === 'pickup') { const result = await journeyLegService.assignShipperToOrder({ order_id: selectedOrder.order_id, shipper_id: selectedShipper, destination_hub_id: selectedWarehouse, destination_satellite_id: selectedWarehouse, }); toast.success(`✅ Tạo thành công! Tổng khoảng cách: ${result.total_distance_km || 0} km`); } else if (currentTab === 'transfer') { const transferLeg = selectedOrder.legs?.find(l => l.leg_type === 'TRANSFER'); if (!transferLeg) { toast.error('Không tìm thấy TRANSFER leg'); return; } await journeyLegService.updateJourneyLeg(transferLeg.id, { assigned_shipper_id: selectedShipper, destination_warehouse_id: selectedWarehouse }); toast.success('✅ Gán shipper TRANSFER thành công!'); } else if (currentTab === 'delivery') { const deliveryLeg = selectedOrder.legs?.find(l => l.leg_type === 'DELIVERY'); if (!deliveryLeg) { toast.error('Không tìm thấy DELIVERY leg'); return; } await journeyLegService.updateJourneyLeg(deliveryLeg.id, { assigned_shipper_id: selectedShipper }); toast.success('✅ Gán shipper DELIVERY thành công!'); } setIsDialogOpen(false); await loadOrdersWithJourney(); } catch (error: any) { toast.error(error.response?.data?.detail || 'Lỗi khi gán thông tin'); } finally { setIsProcessing(false); } };

  // Components Render (OrderCard, ManageOrderCard) giữ nguyên
  const OrderCard = ({ order, onAssign, buttonLabel }: { order: OrderWithJourney; onAssign: () => void; buttonLabel: string }) => (
    <div className="border rounded-lg p-4 hover:bg-muted/50 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 space-y-2">
          <div className="flex items-center gap-3 flex-wrap">
            <h3 className="font-semibold text-lg">{order.order_code}</h3>
            <Badge className="bg-yellow-100 text-yellow-800">{order.status}</Badge>
            {order.area_id && <Badge variant="outline" className="gap-1"><MapPin className="w-3 h-3" />{order.area_id}</Badge>}
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-2"><User className="w-4 h-4" /><span>{order.receiver_name}</span></div>
            <div className="flex items-center gap-2"><MapPin className="w-4 h-4" /><span className="truncate">{order.receiver_address}</span></div>
          </div>
          {order.legs && order.legs.length > 0 && (
            <div className="flex gap-2 items-center mt-3 flex-wrap">
              {order.legs.map((leg, idx) => (
                <div key={leg.id} className="flex items-center gap-2">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${leg.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : leg.assigned_shipper_id ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                    {leg.leg_type}{leg.assigned_shipper_id && ' ✓'}
                  </div>
                  {idx < order.legs.length - 1 && <ArrowRight className="w-4 h-4 text-gray-400" />}
                </div>
              ))}
            </div>
          )}
          <div className="text-xs text-muted-foreground">Tạo: {new Date(order.created_at).toLocaleString('vi-VN')}</div>
        </div>
        <Button size="sm" onClick={onAssign} className="gap-2 whitespace-nowrap"><Truck className="w-4 h-4" />{buttonLabel}</Button>
      </div>
    </div>
  );

  const ManageOrderCard = ({ order }: { order: OrderWithJourney }) => (
    <div className="border rounded-lg p-4 bg-card">
      <div className="flex items-start justify-between mb-4 pb-3 border-b">
        <div className="flex items-center gap-3 flex-wrap">
          <h3 className="font-semibold text-lg">{order.order_code}</h3>
          <Badge className={order.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}>{order.status}</Badge>
          {order.area_id && <Badge variant="outline" className="gap-1"><MapPin className="w-3 h-3" />{order.area_id}</Badge>}
        </div>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm mb-4">
        <div className="flex items-center gap-2 text-muted-foreground"><User className="w-4 h-4" /><span>{order.receiver_name}</span></div>
        <div className="flex items-center gap-2 text-muted-foreground"><MapPin className="w-4 h-4" /><span className="truncate">{order.receiver_address}</span></div>
      </div>
      <div className="space-y-2">
        <h4 className="text-sm font-semibold text-muted-foreground mb-3">Các Chặng Hành Trình:</h4>
        {order.legs && order.legs.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
            {order.legs.map((leg, idx) => (
              <div key={leg.id} className="border rounded-lg p-3 bg-muted/30 hover:bg-muted/50 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <Badge className={leg.leg_type === 'PICKUP' ? 'bg-blue-500' : leg.leg_type === 'TRANSFER' ? 'bg-purple-500' : 'bg-green-500'}>{idx + 1}. {leg.leg_type}</Badge>
                  <Badge variant="outline" className={leg.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : leg.status === 'IN_PROGRESS' ? 'bg-yellow-100 text-yellow-800' : 'bg-gray-100 text-gray-800'}>{leg.status}</Badge>
                </div>
                <div className="space-y-2 mb-3">
                  {leg.estimated_distance && <div className="text-xs text-muted-foreground flex items-center gap-1"><span>📏 {leg.estimated_distance} km</span></div>}
                  {leg.assigned_shipper_id ? <div className="flex items-center gap-1 text-xs"><User className="w-3 h-3" /><span className="truncate">{leg.assigned_shipper_id}</span></div> : <div className="flex items-center gap-1 text-xs text-orange-600"><AlertCircle className="w-3 h-3" /><span>Chưa gán shipper</span></div>}
                  {leg.destination_warehouse_id && <div className="flex items-center gap-1 text-xs"><Warehouse className="w-3 h-3" /><span className="truncate">{leg.destination_warehouse_id}</span></div>}
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" onClick={() => handleEditLeg(leg, order)} className="gap-1 flex-1"><Edit className="w-3 h-3" />Sửa</Button>
                  {leg.status === 'PENDING' && <Button size="sm" variant="destructive" onClick={() => handleDeleteLeg(leg.id, order.order_code)} className="gap-1"><Trash2 className="w-3 h-3" /></Button>}
                </div>
              </div>
            ))}
          </div>
        ) : <p className="text-sm text-muted-foreground text-center py-4">Chưa có chặng nào được tạo</p>}
      </div>
    </div>
  );

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">📋 Quản Lý Điều Phối</h1>
          <p className="text-muted-foreground">Workflow: Pickup → Transfer → Delivery</p>
        </div>
        
        {/* [UPDATE] Thanh Search & Nút Làm Mới */}
        <div className="flex items-center gap-2 w-full md:w-auto">
          <div className="relative w-full md:w-72">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input 
              placeholder="Tìm theo mã vận đơn..." 
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button variant="outline" onClick={loadOrdersWithJourney} disabled={isLoading}>
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Làm mới'}
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={currentTab} onValueChange={(value) => setCurrentTab(value as any)}>
        <TabsList className="inline-flex w-full h-auto flex-wrap justify-start gap-1">
          <TabsTrigger value="pickup" className="flex items-center gap-2 px-4 py-3">
            <Truck className="w-4 h-4" />
            <span className="hidden sm:inline">Pickup</span>
            <Badge variant="secondary" className="ml-1">{pickupOrders.length}</Badge>
          </TabsTrigger>
          <TabsTrigger value="transfer" className="flex items-center gap-2 px-4 py-3">
            <Warehouse className="w-4 h-4" />
            <span className="hidden sm:inline">Transfer</span>
            <Badge variant="secondary" className="ml-1">{transferOrders.length}</Badge>
          </TabsTrigger>
          <TabsTrigger value="delivery" className="flex items-center gap-2 px-4 py-3">
            <Package className="w-4 h-4" />
            <span className="hidden sm:inline">Delivery</span>
            <Badge variant="secondary" className="ml-1">{deliveryOrders.length}</Badge>
          </TabsTrigger>
          
          <TabsTrigger value="completed" className="flex items-center gap-2 px-4 py-3">
            <CheckSquare className="w-4 h-4" />
            <span className="hidden sm:inline">Đã Hoàn Thành</span>
            <Badge variant="secondary" className="ml-1">{completedOrders.length}</Badge>
          </TabsTrigger>

          <TabsTrigger value="manage" className="flex items-center gap-2 px-4 py-3">
            <Settings className="w-4 h-4" />
            <span className="hidden sm:inline">Quản Lý Tất Cả</span>
            <Badge variant="secondary" className="ml-1">{allOrders.length}</Badge>
          </TabsTrigger>
        </TabsList>

        {/* [UPDATE] Áp dụng filterList() cho tất cả các TabsContent */}
        
        {/* PICKUP Tab */}
        <TabsContent value="pickup">
          <Card>
            <CardHeader>
              <CardTitle>Gán Shipper Lấy Hàng (Pickup)</CardTitle>
              <CardDescription>Gán shipper pickup và chọn Kho Hub để lấy hàng từ SME</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
              ) : filterList(pickupOrders).length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>{searchTerm ? 'Không tìm thấy đơn hàng phù hợp' : 'Không có đơn hàng cần gán Pickup'}</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filterList(pickupOrders).map((order) => (
                    <OrderCard key={order.order_id} order={order} onAssign={() => handlePickupOrder(order)} buttonLabel="Gán Pickup" />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* TRANSFER Tab */}
        <TabsContent value="transfer">
          <Card>
            <CardHeader>
              <CardTitle>Gán Xe Vận Chuyển (Transfer)</CardTitle>
              <CardDescription>Gán shipper vận chuyển và chọn Kho Vệ Tinh để chuyển hàng từ Hub</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
              ) : filterList(transferOrders).length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>{searchTerm ? 'Không tìm thấy đơn hàng phù hợp' : 'Không có đơn hàng cần gán Transfer'}</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filterList(transferOrders).map((order) => (
                    <OrderCard key={order.order_id} order={order} onAssign={() => handleTransferOrder(order)} buttonLabel="Gán Transfer" />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* DELIVERY Tab */}
        <TabsContent value="delivery">
          <Card>
            <CardHeader>
              <CardTitle>Gán Shipper Giao Hàng (Delivery)</CardTitle>
              <CardDescription>Gán shipper giao hàng cuối cùng đến tay khách hàng</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
              ) : filterList(deliveryOrders).length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <CheckCircle className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>{searchTerm ? 'Không tìm thấy đơn hàng phù hợp' : 'Không có đơn hàng cần gán Delivery'}</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filterList(deliveryOrders).map((order) => (
                    <OrderCard key={order.order_id} order={order} onAssign={() => handleDeliveryOrder(order)} buttonLabel="Gán Delivery" />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Completed Tab */}
        <TabsContent value="completed">
          <Card>
            <CardHeader>
              <CardTitle>Đơn Hàng Đã Hoàn Thành</CardTitle>
              <CardDescription>Danh sách các đơn hàng đã hoàn tất quy trình giao nhận</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
              ) : filterList(completedOrders).length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <CheckSquare className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>{searchTerm ? 'Không tìm thấy đơn hàng phù hợp' : 'Chưa có đơn hàng nào hoàn thành'}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filterList(completedOrders).map((order) => (
                    <ManageOrderCard key={order.order_id} order={order} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* MANAGE ALL Tab */}
        <TabsContent value="manage">
          <Card>
            <CardHeader>
              <CardTitle>Quản Lý Tất Cả Hành Trình</CardTitle>
              <CardDescription>Xem và chỉnh sửa tất cả các chặng của mọi đơn hàng, kể cả đã được gán</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
              ) : filterList(allOrders).length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Package className="w-12 h-12 mx-auto mb-3 opacity-30" />
                  <p>{searchTerm ? 'Không tìm thấy đơn hàng phù hợp' : 'Chưa có đơn hàng nào có hành trình'}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {filterList(allOrders).map((order) => (
                    <ManageOrderCard key={order.order_id} order={order} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Assignment Dialog */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        {/* ... (Giữ nguyên nội dung Dialog) ... */}
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Truck className="w-5 h-5" />
              {currentTab === 'pickup' && 'Gán Shipper Lấy Hàng'}
              {currentTab === 'transfer' && 'Gán Xe Vận Chuyển'}
              {currentTab === 'delivery' && 'Gán Shipper Giao Hàng'}
            </DialogTitle>
            <DialogDescription>{selectedOrder?.order_code}</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {selectedOrder?.area_id && (<div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-3"><div className="flex items-center gap-2 text-sm"><MapPin className="w-4 h-4 text-blue-600" /><span className="font-medium">Khu vực:</span><Badge variant="outline">{selectedOrder.area_id}</Badge></div></div>)}
            <div className="space-y-2">
              <Label className="text-red-600 font-semibold">Chọn Shipper (*)</Label>
              {availableShippers.length === 0 ? (<div className="border rounded-lg p-4 text-center bg-gray-50"><AlertCircle className="w-8 h-8 mx-auto mb-2 text-orange-500" /><p className="text-sm text-muted-foreground">Không có shipper khả dụng trong khu vực này</p></div>) : (
                <Select value={selectedShipper} onValueChange={setSelectedShipper}>
                  <SelectTrigger><SelectValue placeholder="Chọn tài xế..." /></SelectTrigger>
                  <SelectContent>
                    {availableShippers.map((shipper) => (<SelectItem key={shipper.shipper_id} value={shipper.shipper_id}><div className="flex items-center gap-2"><User className="w-4 h-4" /><span>{shipper.full_name}</span><Badge variant="outline" className="text-xs">{shipper.vehicle_type}</Badge><Badge className="text-xs bg-green-100 text-green-800">★ {shipper.rating.toFixed(1)}</Badge></div></SelectItem>))}
                  </SelectContent>
                </Select>
              )}
            </div>
            {(currentTab === 'pickup' || currentTab === 'transfer' || currentTab === 'delivery') && (
              <div className="space-y-2">
                <Label className="text-red-600 font-semibold">{currentTab === 'pickup' && 'Chọn Kho Hub Đích (*)'}{currentTab === 'transfer' && 'Chọn Kho Vệ Tinh Đích (*)'}{currentTab === 'delivery' && 'Chọn Kho Gửi Hàng (*)'}</Label>
                <Select value={selectedWarehouse} onValueChange={setSelectedWarehouse}>
                  <SelectTrigger><SelectValue placeholder="Chọn kho..." /></SelectTrigger>
                  <SelectContent>
                    {warehouses.filter(wh => wh.status === 'ACTIVE').map((warehouse) => (<SelectItem key={warehouse.warehouse_id} value={warehouse.warehouse_id}><div className="flex items-center gap-2"><Warehouse className="w-4 h-4" /><span>{warehouse.name}</span>{warehouse.area_id && (<Badge variant="outline" className="text-xs">{warehouse.area_id}</Badge>)}</div></SelectItem>))}
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">{currentTab === 'pickup' && 'Shipper sẽ lấy hàng từ SME đến Hub này'}{currentTab === 'transfer' && 'Shipper sẽ chuyển hàng từ Hub chính tới Kho Vệ Tinh này'}{currentTab === 'delivery' && 'Shipper sẽ lấy hàng từ kho này để giao tới khách'}</p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Hủy</Button>
            <Button onClick={handleAssignOrder} disabled={isProcessing || !selectedShipper || !selectedWarehouse}>{isProcessing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Đang xử lý...</> : <><CheckCircle className="w-4 h-4 mr-2" />Xác Nhận</>}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Leg Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        {/* ... (Giữ nguyên nội dung Edit Dialog) ... */}
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle className="flex items-center gap-2"><Edit className="w-5 h-5" />Chỉnh Sửa Chặng Hành Trình</DialogTitle><DialogDescription>{editingLeg?.order.order_code} - {editingLeg?.leg.leg_type} (Chặng {editingLeg?.leg.sequence})</DialogDescription></DialogHeader>
          <div className="space-y-4 py-4">
            {editingLeg && (<div className="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-lg p-3"><div className="flex items-center gap-2 text-sm flex-wrap"><span className="font-medium">Trạng thái hiện tại:</span><Badge variant="outline">{editingLeg.leg.status}</Badge>{editingLeg.leg.estimated_distance && (<Badge variant="outline">📏 {editingLeg.leg.estimated_distance} km</Badge>)}</div></div>)}
            <div className="space-y-2"><Label>Trạng Thái Chặng</Label><Select value={selectedStatus} onValueChange={setSelectedStatus}><SelectTrigger><SelectValue placeholder="Chọn trạng thái..." /></SelectTrigger><SelectContent><SelectItem value="PENDING">⏳ PENDING</SelectItem><SelectItem value="IN_PROGRESS">🚚 IN_PROGRESS</SelectItem><SelectItem value="COMPLETED">✅ COMPLETED</SelectItem><SelectItem value="CANCELLED">❌ CANCELLED</SelectItem></SelectContent></Select></div>
            <div className="space-y-2"><Label>Shipper Phụ Trách</Label>{availableShippers.length === 0 ? (<div className="border rounded-lg p-4 text-center bg-gray-50"><AlertCircle className="w-8 h-8 mx-auto mb-2 text-orange-500" /><p className="text-sm text-muted-foreground">Không có shipper khả dụng</p></div>) : (<Select value={selectedShipper} onValueChange={setSelectedShipper}><SelectTrigger><SelectValue placeholder="Chọn shipper..." /></SelectTrigger><SelectContent><SelectItem value="__none__">-- Không gán --</SelectItem>{availableShippers.map((shipper) => (<SelectItem key={shipper.shipper_id} value={shipper.shipper_id}><div className="flex items-center gap-2"><User className="w-4 h-4" /><span>{shipper.full_name}</span><Badge variant="outline" className="text-xs">{shipper.vehicle_type}</Badge></div></SelectItem>))}</SelectContent></Select>)}</div>
            {editingLeg?.leg.leg_type !== 'DELIVERY' && (<div className="space-y-2"><Label>Kho Đích</Label><Select value={selectedWarehouse} onValueChange={setSelectedWarehouse}><SelectTrigger><SelectValue placeholder="Chọn kho đích..." /></SelectTrigger><SelectContent><SelectItem value="__none__">-- Không chọn --</SelectItem>{warehouses.filter(wh => wh.status === 'ACTIVE').map((warehouse) => (<SelectItem key={warehouse.warehouse_id} value={warehouse.warehouse_id}><div className="flex items-center gap-2"><Warehouse className="w-4 h-4" /><span>{warehouse.name}</span><Badge variant="outline" className="text-xs">{warehouse.type}</Badge></div></SelectItem>))}</SelectContent></Select></div>)}
            <div className="bg-yellow-50 dark:bg-yellow-950/30 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3"><div className="flex gap-2 text-sm text-yellow-800 dark:text-yellow-200"><AlertCircle className="w-4 h-4 shrink-0 mt-0.5" /><span>Thay đổi kho sẽ tự động tính lại khoảng cách. Thay đổi shipper sẽ cập nhật trạng thái của họ.</span></div></div>
          </div>
          <DialogFooter><Button variant="outline" onClick={() => setIsEditDialogOpen(false)}>Hủy</Button><Button onClick={handleSaveEditedLeg} disabled={isProcessing}>{isProcessing ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Đang lưu...</> : <><CheckCircle className="w-4 h-4 mr-2" />Lưu Thay Đổi</>}</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}