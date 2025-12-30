import { useState, useEffect, useRef } from 'react'; 
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Plus, Download, Search, MoreVertical, Package, CheckCircle, Clock, XCircle, Truck, Loader2, AlertCircle, MapPin } from 'lucide-react'; 
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../../components/ui/dropdown-menu';
import { orderService, type CreateOrderRequest, type OrderResponse } from '../../services/orderService';
import { authService } from '../../services/authService';
import { aiServiceClient } from '../../services/api'; 

const statusConfig = {
  PENDING: { label: 'Pending', color: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-400', icon: Package },
  IN_TRANSIT: { label: 'In Transit', color: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-400', icon: Truck },
  AT_WAREHOUSE: { label: 'At Warehouse', color: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-400', icon: Clock },
  DELIVERING: { label: 'Delivering', color: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-400', icon: Truck },
  COMPLETED: { label: 'Completed', color: 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-400', icon: CheckCircle },
  CANCELLED: { label: 'Cancelled', color: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-400', icon: XCircle },
};

interface OrderFormData {
  receiver_name: string;
  receiver_phone: string;
  receiver_address: string;
  weight: string;
  package_type: string;
  special_instructions: string;
}

export function OrdersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedOrder, setSelectedOrder] = useState<OrderResponse | null>(null);
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Dialog State (Create)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  
  // Dialog State (Edit)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const [createError, setCreateError] = useState<string | null>(null);
  const [createSuccess, setCreateSuccess] = useState<string | null>(null);

  // Barcode State
  const [barcodeImage, setBarcodeImage] = useState<string | null>(null);
  const [isBarcodeLoading, setIsBarcodeLoading] = useState(false);
  const [barcodeError, setBarcodeError] = useState<string | null>(null);

  // Dimensions State
  const [dimL, setDimL] = useState('');
  const [dimW, setDimW] = useState('');
  const [dimH, setDimH] = useState('');

  // Autocomplete State
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Form state
  const [formData, setFormData] = useState<OrderFormData>({
    receiver_name: '',
    receiver_phone: '',
    receiver_address: '',
    weight: '',
    package_type: '',
    special_instructions: '',
  });

  useEffect(() => {
    loadOrders();
  }, []);

  // --- LOGIC AUTOCOMPLETE ---
  useEffect(() => {
    if (formData.receiver_address.length < 3) {
      setSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const response = await aiServiceClient.get('/geocoding/autocomplete', {
          params: { text: formData.receiver_address }
        });
        if (response.data && response.data.suggestions) {
          setSuggestions(response.data.suggestions);
          setShowSuggestions(true);
        }
      } catch (err) {
        console.error("Autocomplete error:", err);
      }
    }, 500); 
    return () => clearTimeout(timer);
  }, [formData.receiver_address]);

  useEffect(() => {
    function handleClickOutside(event: any) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  const handleSelectAddress = (suggestion: any) => {
    handleInputChange('receiver_address', suggestion.label);
    setShowSuggestions(false);
  };

  // --- LOGIC BARCODE ---
  useEffect(() => {
    if (selectedOrder) {
        fetchBarcode(selectedOrder.order_id);
    } else {
        setBarcodeImage(null);
        setBarcodeError(null);
    }
  }, [selectedOrder]);

  // Reset form khi đóng dialog (cả Create và Edit)
  useEffect(() => {
    if (!isCreateDialogOpen && !isEditDialogOpen) {
        setFormData({
            receiver_name: '',
            receiver_phone: '',
            receiver_address: '',
            weight: '',
            package_type: '',
            special_instructions: '',
        });
        setDimL(''); setDimW(''); setDimH('');
        setCreateError(null);
        setCreateSuccess(null);
        // Reset selected order nếu đang không ở dialog nào (trừ view details)
        // Lưu ý: logic này cần cẩn thận để không reset nhầm khi đang view details
    }
  }, [isCreateDialogOpen, isEditDialogOpen]);

  // --- HANDLERS ---

  const handleOpenEdit = (order: OrderResponse) => {
    setSelectedOrder(order);
    setFormData({
        receiver_name: order.receiver_name,
        receiver_phone: order.receiver_phone,
        receiver_address: order.receiver_address,
        weight: order.weight.toString(),
        package_type: '', 
        special_instructions: order.note || '',
    });
    
    if (order.dimensions) {
        const dims = order.dimensions.split('x');
        setDimL(dims[0] || '');
        setDimW(dims[1] || '');
        setDimH(dims[2] || '');
    } else {
        setDimL(''); setDimW(''); setDimH('');
    }
    setIsEditDialogOpen(true);
  };

  const fetchBarcode = async (orderId: string) => {
      if (!orderId) return;
      setIsBarcodeLoading(true);
      setBarcodeError(null);
      try {
          const rawBase64 = await orderService.getOrderBarcode(orderId);
          if (!rawBase64) throw new Error("Received empty barcode data");
          let finalImage = rawBase64;
          if (!rawBase64.startsWith('data:image')) {
              finalImage = `data:image/png;base64,${rawBase64}`;
          }
          setBarcodeImage(finalImage);
      } catch (error: any) {
          setBarcodeError('Failed to load barcode image.');
      } finally {
          setIsBarcodeLoading(false);
      }
  };

  const loadOrders = async () => {
    setIsLoading(true);
    try {
      const ordersData = await orderService.getOrders();
      setOrders(ordersData);
    } catch (error: any) {
      setOrders([]);
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = (): string | null => {
    if (!formData.receiver_name.trim()) return 'Receiver name is required';
    if (!formData.receiver_phone.trim()) return 'Receiver phone is required';
    if (!formData.receiver_address.trim()) return 'Delivery address is required';
    if (!formData.weight.trim()) return 'Weight is required';
    const weight = parseFloat(formData.weight);
    if (isNaN(weight) || weight <= 0) return 'Weight must be a positive number';
    if (weight > 1000) return 'Weight cannot exceed 1000kg';
    const phoneRegex = /^[0-9+\-\s()]{10,15}$/;
    if (!phoneRegex.test(formData.receiver_phone)) return 'Invalid phone number format';
    return null;
  };

  const handleCreateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError(null);
    setCreateSuccess(null);
    
    // 1. Validate Form
    const validationError = validateForm();
    if (validationError) { setCreateError(validationError); return; }

    // 2. Validate User
    const currentUser = authService.getCurrentUser();
    if (!currentUser?.sme_id) { setCreateError('Please login as SME owner.'); return; }

    setIsCreating(true);
    try {
      // 3. Prepare Data
      let dimensionsString = undefined;
      if (dimL && dimW && dimH) dimensionsString = `${dimL}x${dimW}x${dimH}`;

      const orderData: CreateOrderRequest = {
        receiver_name: formData.receiver_name.trim(),
        receiver_phone: formData.receiver_phone.trim(),
        receiver_address: formData.receiver_address.trim(),
        weight: parseFloat(formData.weight),
        dimensions: dimensionsString,
        note: [
          formData.package_type ? `Package Type: ${formData.package_type}` : '',
          formData.special_instructions ? `Instructions: ${formData.special_instructions}` : ''
        ].filter(Boolean).join('; ') || undefined
      };

      // 4. Call Service
      // Lưu ý: Đảm bảo orderService.createOrder KHÔNG có try/catch chặn lỗi
      const newOrder = await orderService.createOrder(orderData);
      
      // 5. Success Handling
      setCreateSuccess(`Order ${newOrder.order_code} created successfully!`);
      setOrders(prev => [newOrder, ...prev]);
      
      // Đóng dialog sau 2 giây
      setTimeout(() => setIsCreateDialogOpen(false), 2000);

    } catch (error: any) {
      console.error("Create Order Error:", error);

      // --- LOGIC HIỂN THỊ LỖI ---
      // 1. Thử lấy trực tiếp từ response backend (nếu có)
      // 2. Nếu không, lấy error.message (đã được api.ts xử lý sang tiếng Việt)
      // 3. Cuối cùng mới dùng message mặc định
      const displayMessage = 
        error.response?.data?.detail || 
        error.message || 
        'Failed to create order';

      setCreateError(displayMessage);
      
    } finally {
      setIsCreating(false);
    }
  };

  const handleUpdateOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateError(null);
    setCreateSuccess(null);
    
    if (!selectedOrder) return;
    
    const validationError = validateForm();
    if (validationError) { setCreateError(validationError); return; }

    setIsUpdating(true);
    try {
        let dimensionsString = undefined;
        if (dimL && dimW && dimH) dimensionsString = `${dimL}x${dimW}x${dimH}`;

        const updateData = {
            receiver_name: formData.receiver_name.trim(),
            receiver_phone: formData.receiver_phone.trim(),
            receiver_address: formData.receiver_address.trim(),
            weight: parseFloat(formData.weight),
            dimensions: dimensionsString,
            note: formData.special_instructions
        };

        const updatedOrder = await orderService.updateOrder(selectedOrder.order_id, updateData);
        
        setOrders(prev => prev.map(o => o.order_id === updatedOrder.order_id ? updatedOrder : o));
        setCreateSuccess(`Order updated successfully!`);
        setTimeout(() => setIsEditDialogOpen(false), 1500);
    } catch (error: any) {
        const errorMessage = error.response?.data?.detail || error.message || 'Failed to update order';
        setCreateError(errorMessage);
    } finally {
        setIsUpdating(false);
    }
  };

  const handleCancelOrder = async (order: OrderResponse) => {
    if (!confirm(`Are you sure you want to cancel order ${order.order_code}?`)) return;
    try {
        await orderService.cancelOrder(order.order_id);
        setOrders(prev => prev.map(o => 
            o.order_id === order.order_id ? { ...o, status: 'CANCELLED' } : o
        ));
    } catch (error: any) {
        alert(error.message || 'Failed to cancel order');
    }
  };

  const handleInputChange = (field: keyof OrderFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (createError) setCreateError(null);
    if (field === 'receiver_address') setShowSuggestions(true);
  };

  const filteredOrders = orders.filter(order => {
    const matchesSearch = order.order_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         order.receiver_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         order.receiver_address.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const handlePrintLabel = () => {
    if (!selectedOrder || !barcodeImage) return;
    const printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Shipping Label - ${selectedOrder.order_code}</title>
            <style>
                body { font-family: sans-serif; margin: 0; padding: 20px; }
                .label-container { width: 4in; padding: 10px; border: 1px solid #000; }
                .barcode-img { max-width: 100%; height: auto; margin: 10px 0; display: block; }
                .header { font-size: 16px; font-weight: bold; margin-bottom: 5px; }
                .details { font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="label-container">
                <div class="header">Order: ${selectedOrder.order_code}</div>
                <img src="${barcodeImage}" class="barcode-img" alt="Barcode Image" />
                <div class="details">
                    <p><strong>To:</strong> ${selectedOrder.receiver_name}</p>
                    <p><strong>Phone:</strong> ${selectedOrder.receiver_phone}</p>
                    <p><strong>Address:</strong> ${selectedOrder.receiver_address}</p>
                    <p><strong>Weight:</strong> ${selectedOrder.weight} kg</p>
                    <p><strong>Notes:</strong> ${selectedOrder.note || 'N/A'}</p>
                </div>
            </div>
            <script>window.onload = function() { window.print(); };</script>
        </body>
        </html>
    `;
    const printWindow = window.open('', '_blank');
    if (printWindow) {
        printWindow.document.write(printContent);
        printWindow.document.close();
    }
  };

  // --- RENDER FORM CONTENT (Dùng chung cho Create và Edit để giảm lặp code) ---
  const renderFormContent = (isSubmitting: boolean) => (
    <div className="space-y-4 py-4">
        <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
                <Label htmlFor="receiver_name">Recipient Name *</Label>
                <Input id="receiver_name" value={formData.receiver_name} onChange={(e) => handleInputChange('receiver_name', e.target.value)} disabled={isSubmitting} required />
            </div>
            <div className="space-y-2">
                <Label htmlFor="receiver_phone">Recipient Phone *</Label>
                <Input id="receiver_phone" value={formData.receiver_phone} onChange={(e) => handleInputChange('receiver_phone', e.target.value)} disabled={isSubmitting} required />
            </div>
        </div>

        <div className="space-y-2 relative" ref={wrapperRef}>
            <Label htmlFor="receiver_address">Delivery Address *</Label>
            <Input id="receiver_address" placeholder="Type address to search..." value={formData.receiver_address} onChange={(e) => handleInputChange('receiver_address', e.target.value)} disabled={isSubmitting} required autoComplete="off" />
            {showSuggestions && suggestions.length > 0 && (
            <div className="absolute z-50 w-full bg-white border border-gray-200 rounded-md shadow-lg mt-1 max-h-60 overflow-y-auto">
                {suggestions.map((item, index) => (
                <div key={index} className="p-3 hover:bg-gray-100 cursor-pointer text-sm text-gray-700 border-b border-gray-50 last:border-b-0 flex items-center gap-2" onClick={() => handleSelectAddress(item)}>
                    <MapPin className="w-4 h-4 text-gray-400 shrink-0" /><span>{item.label}</span>
                </div>
                ))}
            </div>
            )}
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
                <Label htmlFor="weight">Weight (kg) *</Label>
                <Input id="weight" type="number" step="0.1" min="0.1" max="1000" value={formData.weight} onChange={(e) => handleInputChange('weight', e.target.value)} disabled={isSubmitting} required />
            </div>
            <div className="space-y-2">
                <Label>Dimensions (L x W x H) (cm)</Label>
                <div className="grid grid-cols-3 gap-2">
                    <Input placeholder="Length" value={dimL} onChange={(e) => setDimL(e.target.value)} disabled={isSubmitting} type="number" min="0" />
                    <Input placeholder="Width" value={dimW} onChange={(e) => setDimW(e.target.value)} disabled={isSubmitting} type="number" min="0" />
                    <Input placeholder="Height" value={dimH} onChange={(e) => setDimH(e.target.value)} disabled={isSubmitting} type="number" min="0" />
                </div>
            </div>
        </div>

        <div className="space-y-2">
            <Label htmlFor="package_type">Package Type</Label>
            <Input id="package_type" value={formData.package_type} onChange={(e) => handleInputChange('package_type', e.target.value)} disabled={isSubmitting} />
        </div>

        <div className="space-y-2">
            <Label htmlFor="special_instructions">Special Instructions</Label>
            <Textarea id="special_instructions" value={formData.special_instructions} onChange={(e) => handleInputChange('special_instructions', e.target.value)} disabled={isSubmitting} rows={3} />
        </div>
    </div>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-foreground mb-1">Orders</h1>
          <p className="text-muted-foreground">Manage and track all your delivery orders</p>
        </div>
        <div className="flex gap-2">
          {/* CREATE ORDER DIALOG */}
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="w-4 h-4 mr-2" /> Create Order
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Order</DialogTitle>
                <DialogDescription>Enter the order details below</DialogDescription>
              </DialogHeader>
              {createSuccess && <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md flex items-center gap-2 text-green-700 text-sm"><CheckCircle className="w-5 h-5" /> {createSuccess}</div>}
              {createError && <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md flex items-center gap-2 text-red-700 text-sm"><AlertCircle className="w-5 h-5" /> {createError}</div>}
              
              <form onSubmit={handleCreateOrder}>
                {renderFormContent(isCreating)}
                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setIsCreateDialogOpen(false)} disabled={isCreating}>Cancel</Button>
                  <Button type="submit" disabled={isCreating}>{isCreating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</> : 'Create Order'}</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>

          {/* EDIT ORDER DIALOG */}
          <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Edit Order: {selectedOrder?.order_code}</DialogTitle>
                <DialogDescription>Update order details</DialogDescription>
              </DialogHeader>
              {createSuccess && <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-md flex items-center gap-2 text-green-700 text-sm"><CheckCircle className="w-5 h-5" /> {createSuccess}</div>}
              {createError && <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md flex items-center gap-2 text-red-700 text-sm"><AlertCircle className="w-5 h-5" /> {createError}</div>}
              
              <form onSubmit={handleUpdateOrder}>
                {renderFormContent(isUpdating)}
                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setIsEditDialogOpen(false)} disabled={isUpdating}>Cancel</Button>
                  <Button type="submit" disabled={isUpdating}>{isUpdating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Updating...</> : 'Save Changes'}</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input placeholder="Search..." className="pl-9" value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">All Orders ({filteredOrders.length}) {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}</CardTitle>
          <CardDescription>Track and manage delivery orders</CardDescription>
        </CardHeader>
        <CardContent>
          {filteredOrders.length === 0 ? (
            <div className="text-center py-12"><Package className="w-12 h-12 text-muted-foreground mx-auto mb-4" /><p className="text-muted-foreground">No orders found.</p></div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border">
                    <th className="text-left py-3 px-2 text-muted-foreground">Code</th>
                    <th className="text-left py-3 px-2 text-muted-foreground">Recipient</th>
                    <th className="text-left py-3 px-2 text-muted-foreground">Address</th>
                    <th className="text-left py-3 px-2 text-muted-foreground">Status</th>
                    <th className="text-left py-3 px-2 text-muted-foreground">Weight</th>
                    <th className="text-right py-3 px-2 text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOrders.map((order) => {
                    const StatusIcon = statusConfig[order.status as keyof typeof statusConfig]?.icon || Package;
                    const statusInfo = statusConfig[order.status as keyof typeof statusConfig] || statusConfig.PENDING;
                    return (
                      <tr key={order.order_id} className="border-b border-border hover:bg-muted/50 cursor-pointer">
                        <td className="py-3 px-2 text-foreground font-medium" onClick={() => setSelectedOrder(order)}>{order.order_code}</td>
                        <td className="py-3 px-2 text-foreground">{order.receiver_name}</td>
                        <td className="py-3 px-2 text-foreground text-sm">{order.receiver_address}</td>
                        <td className="py-3 px-2"><Badge variant="secondary" className={statusInfo.color}><StatusIcon className="w-3 h-3 mr-1" />{statusInfo.label}</Badge></td>
                        <td className="py-3 px-2 text-foreground">{order.weight}kg</td>
                        <td className="py-3 px-2 text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild><Button variant="ghost" size="icon"><MoreVertical className="w-4 h-4" /></Button></DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => setSelectedOrder(order)}>View Details</DropdownMenuItem>
                              <DropdownMenuItem disabled={order.status !== 'PENDING'} onClick={() => handleOpenEdit(order)}>Edit Order</DropdownMenuItem>
                              <DropdownMenuItem disabled={order.status !== 'PENDING'} onClick={() => handleCancelOrder(order)} className="text-red-600 focus:text-red-600">Cancel Order</DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {selectedOrder && !isEditDialogOpen && (
        <Dialog open={!!selectedOrder} onOpenChange={() => setSelectedOrder(null)}>
          <DialogContent className="max-w-2xl">
            <DialogHeader><DialogTitle>Order Details: {selectedOrder.order_code}</DialogTitle><DialogDescription>Complete order information</DialogDescription></DialogHeader>
            <div className="space-y-6 py-4">
              <div className="grid sm:grid-cols-2 gap-4">
                <div><label className="text-sm text-muted-foreground">Recipient</label><div className="text-foreground">{selectedOrder.receiver_name}</div></div>
                <div><label className="text-sm text-muted-foreground">Phone</label><div className="text-foreground">{selectedOrder.receiver_phone}</div></div>
                <div className="col-span-2"><label className="text-sm text-muted-foreground">Delivery Address</label><div className="text-foreground">{selectedOrder.receiver_address}</div></div>
                <div><label className="text-sm text-muted-foreground">Weight</label><div className="text-foreground">{selectedOrder.weight}kg</div></div>
                <div><label className="text-sm text-muted-foreground">Dimensions</label><div className="text-foreground">{selectedOrder.dimensions || 'N/A'}</div></div>
                {selectedOrder.note && <div className="col-span-2"><label className="text-sm text-muted-foreground">Notes</label><div className="text-foreground">{selectedOrder.note}</div></div>}
              </div>
              <div className="flex justify-center p-6 bg-muted rounded-lg min-h-[150px] items-center">
                <div className="space-y-2 text-center w-full">
                  {isBarcodeLoading && <div className="flex flex-col items-center justify-center py-4"><Loader2 className="w-8 h-8 text-muted-foreground animate-spin mb-2" /><span className="text-xs text-muted-foreground">Loading barcode...</span></div>}
                  {barcodeError && !isBarcodeLoading && <div className="text-red-500 flex items-center justify-center gap-2 py-4"><AlertCircle className="w-5 h-5" /><span className="text-sm">{barcodeError}</span></div>}
                  {!isBarcodeLoading && !barcodeError && barcodeImage && <div className="bg-white p-2 rounded inline-block"><img src={barcodeImage} alt={`Barcode for ${selectedOrder.order_code}`} className="max-w-[300px] h-auto mx-auto" /></div>}
                  <div className="text-sm text-muted-foreground font-mono mt-2">{selectedOrder.barcode_id}</div>
                </div>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setSelectedOrder(null)}>Close</Button>
              <Button onClick={handlePrintLabel} disabled={!barcodeImage || isBarcodeLoading}>{isBarcodeLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />} Print Label</Button>
            </div>
          </DialogContent>
        </Dialog>
      )}
    </div>
  );
}