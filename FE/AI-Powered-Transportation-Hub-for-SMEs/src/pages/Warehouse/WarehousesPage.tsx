import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Label } from '../../components/ui/label';
import { Badge } from '../../components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../../components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../../components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../../components/ui/dropdown-menu';
import { Progress } from '../../components/ui/progress';
import {
  Plus,
  Package,
  MapPin,
  QrCode,
  Loader2,
  AlertCircle,
  MoreVertical,
  Edit,
  Trash2
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { warehouseService, type Warehouse } from '../../services/warehouseService';
import { areaService, type Area } from '../../services/areaService';
import { aiServiceClient } from '../../services/api';

// --- MAP IMPORTS (FIXED) ---
import Map, { Marker, NavigationControl } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';
import maplibregl from 'maplibre-gl'; 

// Interface cho Form
interface WarehouseFormState {
  name: string;
  address: string;
  capacity_limit: number;
  manager: string;
  contact_phone: string;
  type: string;
  area_id: string;
  latitude?: number;
  longitude?: number;
}

export function WarehousesPage() {
  const GOONG_MAP_KEY = import.meta.env.VITE_GOONG_MAP_KEY || 'YOUR_GOONG_MAP_TILES_KEY'; 
  const GOONG_STYLE_URL = `https://tiles.goong.io/assets/goong_map_web.json?api_key=${GOONG_MAP_KEY}`;

  // State management
  const [warehouses, setWarehouses] = useState<Warehouse[]>([]);
  const [availableAreas, setAvailableAreas] = useState<Area[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingAreas, setIsLoadingAreas] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedWarehouse, setSelectedWarehouse] = useState<Warehouse | null>(null);
  
  // Dialog states
  const [scanDialogOpen, setScanDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false); // State cho Edit Dialog

  // Processing states
  const [isCreating, setIsCreating] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  // Sync result state
  const [syncResult, setSyncResult] = useState<any>(null);
  const [showSyncDialog, setShowSyncDialog] = useState(false);

  // --- FORMS ---
  // 1. Create Form
  const [createForm, setCreateForm] = useState<WarehouseFormState>({
    name: '', address: '', capacity_limit: 0, manager: '', phone: '', type: 'HUB', area_id: '', latitude: undefined, longitude: undefined,
  });

  // 2. Edit Form
  const [editForm, setEditForm] = useState<WarehouseFormState & { warehouse_id: string }>({
    warehouse_id: '', name: '', address: '', capacity_limit: 0, manager: '', phone: '', type: 'HUB', area_id: '', latitude: undefined, longitude: undefined,
  });

  // --- AUTOCOMPLETE STATE ---
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null); // Ref cho Create Form
  const editWrapperRef = useRef<HTMLDivElement>(null); // Ref cho Edit Form

  // Load initial data
  useEffect(() => {
    Promise.all([loadWarehouses(), loadAreas()]);
  }, []);

  const loadWarehouses = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await warehouseService.getAllWarehouses();
      setWarehouses(data);
    } catch (err: any) {
      console.error('Failed to load warehouses:', err);
      setError(err.response?.data?.detail || 'Failed to load warehouses');
    } finally {
      setIsLoading(false);
    }
  };


  useEffect(() => {
    // Hàm chạy ngầm (Silent Sync)
    const runAutoSync = async () => {
      try {
        // 1. Gọi API Sync Usage (nhưng không hiện loading spinner lớn)
        await warehouseService.syncWarehouseUsage();
        
        // 2. Gọi xong thì reload lại danh sách kho để cập nhật số liệu mới lên UI
        await loadWarehouses();
        
        console.log("🔄 Auto-sync & refresh completed.");
      } catch (err) {
        console.error("⚠️ Auto-sync failed:", err);
        // Không hiện lỗi lên UI để tránh spam người dùng
      }
    };

    // Thiết lập chu kỳ lặp lại (ví dụ: 30 giây = 30000ms)
    const intervalId = setInterval(runAutoSync, 30000);

    // Dọn dẹp interval khi component bị hủy (người dùng chuyển trang)
    return () => clearInterval(intervalId);
  }, []); // Empty dependency array [] đảm bảo chỉ set interval 1 lần khi mount


  const loadAreas = async () => {
    try {
      setIsLoadingAreas(true);
      const data = await areaService.getAllAreas();
      setAvailableAreas(data);
    } catch (err: any) {
      console.error('Failed to load areas:', err);
      setAvailableAreas([]);
    } finally {
      setIsLoadingAreas(false);
    }
  };

  // --- AUTOCOMPLETE LOGIC (Reusable) ---
  const fetchSuggestions = async (text: string) => {
    if (!text || text.length < 3) {
      setSuggestions([]);
      return;
    }
    try {
      const response = await aiServiceClient.get('/geocoding/autocomplete', {
        params: { text }
      });
      if (response.data && response.data.suggestions) {
        setSuggestions(response.data.suggestions);
        setShowSuggestions(true);
      }
    } catch (err) {
      console.error("Autocomplete error:", err);
    }
  };

  // Effect cho Create Form Autocomplete
  useEffect(() => {
    const timer = setTimeout(() => fetchSuggestions(createForm.address), 500);
    return () => clearTimeout(timer);
  }, [createForm.address]);

  // Effect cho Edit Form Autocomplete
  useEffect(() => {
    // Chỉ fetch khi dialog edit đang mở để tránh conflict
    if (editDialogOpen) {
        const timer = setTimeout(() => fetchSuggestions(editForm.address), 500);
        return () => clearTimeout(timer);
    }
  }, [editForm.address, editDialogOpen]);

  // Click outside handler
  useEffect(() => {
    function handleClickOutside(event: any) {
      // Check Create Form Wrapper
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
      // Check Edit Form Wrapper
      if (editWrapperRef.current && !editWrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef, editWrapperRef]);

  // --- HANDLERS ---

  // 1. CREATE
  const handleCreateWarehouse = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createForm.name || !createForm.address || !createForm.capacity_limit || !createForm.area_id) {
      setError('Please fill in all required fields');
      return;
    }
    setIsCreating(true);
    try {
      await warehouseService.createWarehouse(createForm as any);
      await loadWarehouses();
      setCreateForm({ name: '', address: '', capacity_limit: 0, manager: '', phone: '', type: 'HUB', area_id: '', latitude: undefined, longitude: undefined });
      setCreateDialogOpen(false);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create warehouse');
    } finally {
      setIsCreating(false);
    }
  };

  // 2. DELETE
  const handleDeleteWarehouse = async (id: string) => {
    if (!window.confirm("Are you sure you want to delete this warehouse?")) return;
    
    try {
        await warehouseService.deleteWarehouse(id);
        // Cập nhật state local để không cần load lại toàn bộ
        setWarehouses(prev => prev.filter(w => w.warehouse_id !== id));
    } catch (err: any) {
        alert(err.response?.data?.detail || "Failed to delete warehouse");
    }
  };

  // 3. PREPARE EDIT
  const handleOpenEdit = (warehouse: Warehouse) => {
    setEditForm({
        warehouse_id: warehouse.warehouse_id,
        name: warehouse.name,
        address: warehouse.address,
        capacity_limit: warehouse.capacity_limit,
        manager: warehouse.manager || '',
        contact_phone: warehouse.contact_phone || '',
        type: warehouse.type || 'HUB',
        area_id: warehouse.area_id || '',
        latitude: warehouse.latitude,
        longitude: warehouse.longitude
    });
    setEditDialogOpen(true);
  };

  // 4. SUBMIT EDIT
  const handleUpdateWarehouse = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdating(true);
    try {
        await warehouseService.updateWarehouse(editForm.warehouse_id, {
            name: editForm.name,
            address: editForm.address,
            capacity_limit: editForm.capacity_limit,
            manager: editForm.manager,
            contact_phone: editForm.contact_phone,
            type: editForm.type,
            area_id: editForm.area_id,
        });
        await loadWarehouses();
        setEditDialogOpen(false);
    } catch (err: any) {
        console.error(err);
        alert(err.response?.data?.detail || "Failed to update warehouse");
    } finally {
        setIsUpdating(false);
    }
  };

  // Handler để sync usage
  const handleSyncUsage = async () => {
    try {
      setIsSyncing(true);
      const result = await warehouseService.syncWarehouseUsage();
      setSyncResult(result);
      setShowSyncDialog(true);
      
      // Reload warehouses để hiển thị usage mới
      await loadWarehouses();
      
    } catch (err: any) {
      console.error('Sync failed:', err);
      alert('Lỗi khi đồng bộ usage: ' + (err.response?.data?.detail || err.message));
    } finally {
      setIsSyncing(false);
    }
  };

  // --- STATS CALCULATION ---
  const totalCapacity = warehouses.reduce((sum, w) => sum + w.capacity_limit, 0);
  const totalLoad = warehouses.reduce((sum, w) => sum + w.current_load, 0);
  const utilizationRate = totalCapacity > 0 ? Math.round((totalLoad / totalCapacity) * 100) : 0;
  const activeCount = warehouses.filter(w => w.status === 'ACTIVE').length;
  const maintenanceCount = warehouses.filter(w => w.status === 'MAINTENANCE').length;

  const capacityData = warehouses.map((w) => ({
    name: w.name,
    usage: w.capacity_limit > 0 ? Math.round((w.current_load / w.capacity_limit) * 100) : 0,
    remaining: w.capacity_limit > 0 ? Math.round(((w.capacity_limit - w.current_load) / w.capacity_limit) * 100) : 0,
  }));

  if (isLoading) {
    return <div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>;
  }

  return (
    <div className="space-y-6">
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md flex items-center gap-2">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-foreground mb-1">Warehouses</h1>
          <p className="text-muted-foreground">Manage warehouse locations and inventory</p>
        </div>
        <div className="flex gap-2">
          <Dialog open={scanDialogOpen} onOpenChange={setScanDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm">
                <QrCode className="w-4 h-4 mr-2" /> Scan Goods
              </Button>
            </DialogTrigger>
            <DialogContent>
               <DialogHeader><DialogTitle>Scan Goods</DialogTitle><DialogDescription>Feature coming soon...</DialogDescription></DialogHeader>
            </DialogContent>
          </Dialog>

          {/* CREATE DIALOG */}
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm"><Plus className="w-4 h-4 mr-2" /> Add Warehouse</Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Add New Warehouse</DialogTitle>
                <DialogDescription>Enter details. Address will be auto-completed.</DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreateWarehouse} className="space-y-4 py-4">
                <div className="grid sm:grid-cols-2 gap-4">
                    <div className="space-y-2">
                        <Label>Warehouse Name *</Label>
                        <Input value={createForm.name} onChange={(e) => setCreateForm(prev => ({ ...prev, name: e.target.value }))} required />
                    </div>
                    <div className="space-y-2">
                        <Label>Type *</Label>
                        <Select value={createForm.type} onValueChange={(val) => setCreateForm(prev => ({...prev, type: val}))}>
                            <SelectTrigger><SelectValue placeholder="Select type" /></SelectTrigger>
                            <SelectContent>
                                <SelectItem value="HUB">HUB</SelectItem>
                                <SelectItem value="SATELLITE">SATELLITE</SelectItem>
                                <SelectItem value="LOCAL_DEPOT">LOCAL DEPOT</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                </div>
                <div className="space-y-2">
                  <Label>Area / Zone *</Label>
                  <Select value={createForm.area_id} onValueChange={(val) => setCreateForm(prev => ({...prev, area_id: val}))}>
                      <SelectTrigger><SelectValue placeholder="Select area..." /></SelectTrigger>
                      <SelectContent>
                        {availableAreas.map((area) => (
                          <SelectItem key={area.area_id} value={area.area_id}>{area.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                </div>
                <div className="space-y-2 relative" ref={wrapperRef}>
                  <Label>Address *</Label>
                  <Input 
                    placeholder="Start typing address..." 
                    value={createForm.address} 
                    onChange={(e) => { setCreateForm(prev => ({ ...prev, address: e.target.value })); setShowSuggestions(true); }} 
                    required autoComplete="off" 
                  />
                  {showSuggestions && suggestions.length > 0 && (
                    <div className="absolute z-50 w-full bg-white border border-gray-200 rounded-md shadow-lg mt-1 max-h-60 overflow-y-auto">
                      {suggestions.map((item, index) => (
                        <div key={index} className="p-3 hover:bg-gray-100 cursor-pointer text-sm flex items-center gap-2" 
                             onClick={() => {
                                 setCreateForm(prev => ({ ...prev, address: item.label, latitude: item.latitude, longitude: item.longitude }));
                                 setShowSuggestions(false);
                             }}>
                          <MapPin className="w-4 h-4 text-gray-400 shrink-0" /><span>{item.label}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Capacity *</Label>
                    <Input type="number" value={createForm.capacity_limit || ''} onChange={(e) => setCreateForm(prev => ({ ...prev, capacity_limit: parseInt(e.target.value) || 0 }))} required />
                  </div>
                  <div className="space-y-2"><Label>Manager</Label><Input value={createForm.manager} onChange={(e) => setCreateForm(prev => ({ ...prev, manager: e.target.value }))} /></div>
                </div>
                <div className="space-y-2"><Label>Phone</Label><Input value={createForm.contact_phone} onChange={(e) => setCreateForm(prev => ({ ...prev, contact_phone: e.target.value }))} /></div>
                <div className="flex justify-end gap-2 pt-4">
                  <Button type="button" variant="outline" onClick={() => setCreateDialogOpen(false)} disabled={isCreating}>Cancel</Button>
                  <Button type="submit" disabled={isCreating}>{isCreating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Creating...</> : 'Add Warehouse'}</Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
          <div className="flex items-center gap-2 text-xs text-muted-foreground mr-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            Live updates (30s)
          </div>
          {/* ✅ NEW: Sync Usage Button */}
          <Button 
            onClick={handleSyncUsage}
            disabled={isSyncing}
            variant="outline"
            className="gap-2"
          >
            {isSyncing ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Syncing...
              </>
            ) : (
              <>
                <Package className="w-4 h-4" />
                Sync Usage
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total Warehouses</CardTitle></CardHeader><CardContent><div className="text-2xl">{warehouses.length}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total Capacity</CardTitle></CardHeader><CardContent><div className="text-2xl">{totalCapacity.toLocaleString()}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Current Load</CardTitle></CardHeader><CardContent><div className="text-2xl">{totalLoad.toLocaleString()}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Available</CardTitle></CardHeader><CardContent><div className="text-2xl">{(totalCapacity - totalLoad).toLocaleString()}</div></CardContent></Card>
      </div>

      {/* Chart */}
      <Card>
        <CardHeader><CardTitle>Capacity Usage</CardTitle><CardDescription>Utilization per location</CardDescription></CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={capacityData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip />
                <Bar dataKey="usage" stackId="a" fill="#3b82f6" />
                <Bar dataKey="remaining" stackId="a" fill="#e5e7eb" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* WAREHOUSE LIST */}
      <div className="grid md:grid-cols-2 gap-6">
        {warehouses.map((warehouse) => {
          const usagePercent = warehouse.capacity_limit > 0 ? Math.round((warehouse.current_load / warehouse.capacity_limit) * 100) : 0;
          return (
            <Card key={warehouse.warehouse_id} className="hover:shadow-lg transition-shadow cursor-pointer" onClick={() => setSelectedWarehouse(warehouse)}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="flex items-center gap-2"><Package className="w-5 h-5" />{warehouse.name}</CardTitle>
                    <CardDescription className="flex items-center gap-1 mt-1"><MapPin className="w-3 h-3" />{warehouse.address}</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={warehouse.status === 'ACTIVE' ? 'default' : 'secondary'}>{warehouse.status}</Badge>
                    
                    {/* ACTIONS DROPDOWN */}
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                            <Button variant="ghost" size="icon" className="h-8 w-8"><MoreVertical className="w-4 h-4" /></Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleOpenEdit(warehouse); }}>
                                <Edit className="w-4 h-4 mr-2" /> Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={(e) => { e.stopPropagation(); handleDeleteWarehouse(warehouse.warehouse_id); }} className="text-red-600 focus:text-red-600">
                                <Trash2 className="w-4 h-4 mr-2" /> Delete
                            </DropdownMenuItem>
                        </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2 text-sm"><span className="text-muted-foreground">Usage</span><span>{usagePercent}%</span></div>
                  <Progress value={usagePercent} className="h-2" />
                  <div className="flex items-center justify-between mt-1 text-xs text-muted-foreground"><span>{warehouse.current_load} used</span><span>{warehouse.capacity_limit} total</span></div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* VIEW DETAILS DIALOG */}
      {selectedWarehouse && !editDialogOpen && (
        <Dialog open={!!selectedWarehouse} onOpenChange={(open) => !open && setSelectedWarehouse(null)}>
          <DialogContent className="max-w-3xl"> 
            <DialogHeader>
              <DialogTitle>{selectedWarehouse.name}</DialogTitle>
              <DialogDescription>Warehouse Details</DialogDescription>
            </DialogHeader>
            
            <div className="grid md:grid-cols-2 gap-6 py-4">
              {/* Left Column: Info */}
              <div className="space-y-4">
                <div><label className="text-sm text-muted-foreground block">Address</label><div className="font-medium">{selectedWarehouse.address}</div></div>
                <div className="grid grid-cols-2 gap-4">
                   <div><label className="text-sm text-muted-foreground block">Area</label><div>{selectedWarehouse.area_id}</div></div>
                   <div><label className="text-sm text-muted-foreground block">Type</label><Badge>{selectedWarehouse.type}</Badge></div>
                </div>
                <div><label className="text-sm text-muted-foreground block">Manager</label><div>{selectedWarehouse.manager || 'N/A'}</div></div>
                <div><label className="text-sm text-muted-foreground block">Phone</label><div>{selectedWarehouse.contact_phone || 'N/A'}</div></div>
                
                <div className="pt-4 border-t">
                  <div className="flex justify-between text-sm mb-2">
                      <span className="text-muted-foreground">Capacity Utilization</span>
                      <span className="font-bold">{selectedWarehouse.capacity_limit > 0 ? Math.round((selectedWarehouse.current_load / selectedWarehouse.capacity_limit) * 100) : 0}%</span>
                  </div>
                  <Progress value={selectedWarehouse.capacity_limit > 0 ? (selectedWarehouse.current_load / selectedWarehouse.capacity_limit) * 100 : 0} />
                </div>
              </div>

              {/* Right Column: Map */}
              <div className="h-[300px] w-full rounded-md overflow-hidden border border-border relative">
                  {selectedWarehouse.latitude && selectedWarehouse.longitude ? (
                      <Map
                          mapLib={maplibregl} /* --- FIX IS HERE: Explicitly passing the map library --- */
                          initialViewState={{
                              longitude: selectedWarehouse.longitude,
                              latitude: selectedWarehouse.latitude,
                              zoom: 14
                          }}
                          style={{width: '100%', height: '100%'}}
                          mapStyle={GOONG_STYLE_URL}
                      >
                          <Marker 
                              longitude={selectedWarehouse.longitude} 
                              latitude={selectedWarehouse.latitude} 
                              color="red" 
                          />
                          <NavigationControl position="top-right" />
                      </Map>
                  ) : (
                      <div className="flex items-center justify-center h-full bg-gray-100 text-gray-400">
                          <div className="text-center">
                              <MapPin className="w-8 h-8 mx-auto mb-2 opacity-50" />
                              <span className="text-sm">No coordinates available</span>
                          </div>
                      </div>
                  )}
              </div>
            </div>
            
            <div className="flex justify-end">
              <Button variant="outline" onClick={() => setSelectedWarehouse(null)}>Close</Button>
            </div>
          </DialogContent>
        </Dialog>
      )}

      {/* EDIT DIALOG */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-lg">
            <DialogHeader><DialogTitle>Edit Warehouse</DialogTitle><DialogDescription>Update warehouse information</DialogDescription></DialogHeader>
            <form onSubmit={handleUpdateWarehouse} className="space-y-4 py-4">
                <div className="grid sm:grid-cols-2 gap-4">
                    <div className="space-y-2"><Label>Name</Label><Input value={editForm.name} onChange={(e) => setEditForm(prev => ({...prev, name: e.target.value}))} required /></div>
                    <div className="space-y-2">
                        <Label>Type</Label>
                        <Select value={editForm.type} onValueChange={(val) => setEditForm(prev => ({...prev, type: val}))}>
                            <SelectTrigger><SelectValue /></SelectTrigger>
                            <SelectContent><SelectItem value="HUB">HUB</SelectItem><SelectItem value="SATELLITE">SATELLITE</SelectItem><SelectItem value="LOCAL_DEPOT">LOCAL DEPOT</SelectItem></SelectContent>
                        </Select>
                    </div>
                </div>
                <div className="space-y-2"><Label>Area</Label>
                    <Select value={editForm.area_id} onValueChange={(val) => setEditForm(prev => ({...prev, area_id: val}))}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>{availableAreas.map(area => <SelectItem key={area.area_id} value={area.area_id}>{area.name}</SelectItem>)}</SelectContent>
                    </Select>
                </div>
                <div className="space-y-2 relative" ref={editWrapperRef}>
                    <Label>Address</Label>
                    <Input value={editForm.address} onChange={(e) => { setEditForm(prev => ({...prev, address: e.target.value})); setShowSuggestions(true); }} required autoComplete="off" />
                    {showSuggestions && suggestions.length > 0 && (
                        <div className="absolute z-50 w-full bg-white border border-gray-200 rounded-md shadow-lg mt-1 max-h-60 overflow-y-auto">
                            {suggestions.map((item, index) => (
                                <div key={index} className="p-3 hover:bg-gray-100 cursor-pointer text-sm flex items-center gap-2"
                                    onClick={() => { setEditForm(prev => ({...prev, address: item.label, latitude: item.latitude, longitude: item.longitude})); setShowSuggestions(false); }}>
                                    <MapPin className="w-4 h-4 text-gray-400 shrink-0" /><span>{item.label}</span>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
                <div className="grid sm:grid-cols-2 gap-4">
                    <div className="space-y-2"><Label>Capacity</Label><Input type="number" value={editForm.capacity_limit} onChange={(e) => setEditForm(prev => ({...prev, capacity_limit: parseInt(e.target.value) || 0}))} required /></div>
                    <div className="space-y-2"><Label>Manager</Label><Input value={editForm.manager} onChange={(e) => setEditForm(prev => ({...prev, manager: e.target.value}))} /></div>
                </div>
                <div className="space-y-2"><Label>Phone</Label><Input value={editForm.contact_phone} onChange={(e) => setEditForm(prev => ({...prev, contact_phone: e.target.value}))} /></div>
                <div className="flex justify-end gap-2 pt-4">
                    <Button type="button" variant="outline" onClick={() => setEditDialogOpen(false)} disabled={isUpdating}>Cancel</Button>
                    <Button type="submit" disabled={isUpdating}>{isUpdating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Saving...</> : 'Save Changes'}</Button>
                </div>
            </form>
        </DialogContent>
      </Dialog>

      {/* Sync Result Dialog */}
      <Dialog open={showSyncDialog} onOpenChange={setShowSyncDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>🔄 Warehouse Usage Sync Result</DialogTitle>
            <DialogDescription>
              Scanned all pickup orders and updated warehouse usage
            </DialogDescription>
          </DialogHeader>
          
          {syncResult && (
            <div className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <Card>
                  <CardContent className="pt-4">
                    <div className="text-2xl font-bold">{syncResult.total_warehouses_scanned}</div>
                    <div className="text-sm text-muted-foreground">Warehouses Scanned</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-4">
                    <div className="text-2xl font-bold">{syncResult.warehouses_updated.length}</div>
                    <div className="text-sm text-muted-foreground">Warehouses Updated</div>
                  </CardContent>
                </Card>
                <Card>
                  <CardContent className="pt-4">
                    <div className="text-2xl font-bold">{syncResult.total_orders_counted}</div>
                    <div className="text-sm text-muted-foreground">Total Orders</div>
                  </CardContent>
                </Card>
              </div>

              {/* Updated Warehouses List */}
              <div className="max-h-96 overflow-y-auto">
                <h3 className="font-semibold mb-2">Updated Warehouses:</h3>
                {syncResult.warehouses_updated.map((wh: any) => (
                  <div key={wh.warehouse_id} className="flex items-center justify-between p-2 border-b">
                    <span className="font-medium">{wh.warehouse_name}</span>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">{wh.old_load}</span>
                      <span>→</span>
                      <span className="text-sm font-semibold">{wh.new_load}</span>
                      <span className="text-xs text-muted-foreground">
                        / {wh.capacity_limit}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              <div className="text-xs text-muted-foreground">
                Synced at: {new Date(syncResult.timestamp).toLocaleString()}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}