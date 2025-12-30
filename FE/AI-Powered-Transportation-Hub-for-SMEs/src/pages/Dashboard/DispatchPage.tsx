import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../../components/ui/dialog';
import { Input } from '../../components/ui/input';
import { MapPin, RotateCcw, Package, ArrowRight, User, Warehouse as WarehouseIcon, Sparkles, Loader2, Search } from 'lucide-react';
import { toast } from 'sonner';

// Services
import { dispatchService, DispatchOrder, OrderJourneyLeg } from '../../services/dispatchService';
import { warehouseService } from '../../services/warehouseService';

// --- Helper Functions & Styles ---
const getPriorityColor = (priority: string) => {
  if (!priority) return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
  switch (priority.toLowerCase()) {
    case 'high': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
    case 'medium': return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400';
    case 'low': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
    default: return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
  }
};

const cleanEnumValue = (value: string): string => {
  if (!value) return 'UNKNOWN';
  const parts = value.split('.');
  return parts[parts.length - 1];
};

const formatStatus = (status: string): string => {
  const clean = cleanEnumValue(status);
  return clean
    .split('_')
    .map(word => word.charAt(0) + word.slice(1).toLowerCase())
    .join(' ');
};

const getStatusColor = (status: string) => {
    const cleanStatus = cleanEnumValue(status);
    switch (cleanStatus) {
        case 'COMPLETED': return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
        case 'IN_PROGRESS': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
        case 'IN_TRANSIT': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
        case 'AT_WAREHOUSE': return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400';
        case 'DELIVERING': return 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400';
        case 'PENDING': return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
        case 'CANCELLED': return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
        default: return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
    }
}

export function DispatchPage() {
  // --- STATE MANAGEMENT ---
  const [isAutoDispatching, setIsAutoDispatching] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  
  // Search State
  const [searchTerm, setSearchTerm] = useState("");

  // Data State
  const [dispatchOrders, setDispatchOrders] = useState<DispatchOrder[]>([]);

  // Detail Modal State
  const [selectedOrder, setSelectedOrder] = useState<DispatchOrder | null>(null);
  const [orderLegs, setOrderLegs] = useState<OrderJourneyLeg[]>([]);
  const [isLoadingDetails, setIsLoadingDetails] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  
  // Cache for Warehouse Names
  const [nameCache, setNameCache] = useState<Record<string, string>>({});

  // --- EFFECT: Load Initial Data ---
  useEffect(() => {
    loadInitialData();
  }, []);

  // --- HANDLERS ---
  const loadInitialData = async () => {
    setIsLoading(true);
    try {
      const ordersData = await dispatchService.getDispatchSummary();
      if (Array.isArray(ordersData)) setDispatchOrders(ordersData);
    } catch (error) {
      console.error("Failed to load data", error);
      toast.error("Failed to load orders");
    } finally {
      setIsLoading(false);
    }
  };

  const refreshOrders = async () => {
    setIsLoading(true);
    try {
      const data = await dispatchService.getDispatchSummary();
      if (Array.isArray(data)) setDispatchOrders(data);
    } catch (error) {
      toast.error("Failed to refresh orders");
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to fetch warehouse names for ID-only legs
  const fetchEnrichedLegDetails = async (legs: OrderJourneyLeg[]) => {
    const newCache = { ...nameCache };
    const promises: Promise<void>[] = [];
    const warehouseIds = new Set<string>();
    
    legs.forEach(leg => {
        if (leg.origin_warehouse_id) warehouseIds.add(leg.origin_warehouse_id);
        if (leg.destination_warehouse_id) warehouseIds.add(leg.destination_warehouse_id);
    });

    warehouseIds.forEach(id => {
        if (!newCache[id]) {
            const p = warehouseService.getWarehouseById(id)
                .then(wh => { newCache[id] = wh.name; })
                .catch(() => { newCache[id] = `Unknown (${id})`; });
            promises.push(p);
        }
    });

    await Promise.all(promises);
    setNameCache(newCache);
  };

  const handleOrderClick = async (order: DispatchOrder) => {
    setSelectedOrder(order);
    setIsDetailOpen(true);
    setIsLoadingDetails(true);
    setOrderLegs([]);

    try {
        const legs = await dispatchService.getOrderDetails(order.id);
        await fetchEnrichedLegDetails(legs);
        setOrderLegs(legs);
    } catch (error) {
        toast.error("Failed to fetch order journey");
    } finally {
        setIsLoadingDetails(false);
    }
  };

  const handleAutoDispatch = async () => {
    setIsAutoDispatching(true);
    try {
      const result = await dispatchService.runAutoPilot();
      
      if (result.status === 'COMPLETED' || result.status === 'SUCCESS') {
        toast.success(`AI Optimization Complete!`, { 
            description: `Processed ${result.processed_count} areas. Summary: ${result.summary}` 
        });
        setTimeout(refreshOrders, 2000);
      } else {
        toast.info("AI Optimization Finished", { description: result.status });
      }
    } catch (error: any) {
      toast.error("Optimization Failed", { description: error.response?.data?.detail || "System Error" });
    } finally {
      setIsAutoDispatching(false);
    }
  };

  // --- FILTER LOGIC ---
  const filteredOrders = dispatchOrders.filter(order => {
    const term = searchTerm.toLowerCase();
    return (
      order.code.toLowerCase().includes(term) ||
      order.from_location.toLowerCase().includes(term) ||
      order.to_location.toLowerCase().includes(term)
    );
  });

  // --- RENDER ---
  return (
    <div className="space-y-6 p-6">
      {/* HEADER & CONTROLS */}
      <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">Dispatch Console</h1>
          <p className="text-muted-foreground">Intelligent Logistics Management System.</p>
        </div>
        
        {/* Toolbar: Search + Actions */}
        <div className="flex flex-col sm:flex-row gap-3 bg-muted/30 p-2 rounded-lg border items-center">
          
          {/* Search Input */}
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Search code, location..."
              className="w-full pl-9 bg-background h-10"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          {/* AI Auto-Pilot Button */}
          <Button 
            onClick={handleAutoDispatch} 
            disabled={isAutoDispatching} 
            size="default" // Có thể dùng 'lg' nếu muốn to hơn
            className="w-full sm:w-auto h-10 bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white shadow-md transition-all"
          >
            {isAutoDispatching ? (
                <>
                    <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing...
                </>
            ) : (
                <>
                    <Sparkles className="w-5 h-5 mr-2" />
                    AI Auto-Pilot
                </>
            )}
          </Button>

          <div className="hidden sm:block w-px bg-border mx-1 h-8"></div>

          {/* Refresh Button */}
          <Button variant="ghost" size="icon" onClick={refreshOrders} disabled={isLoading} className="h-10 w-10">
            <RotateCcw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* ORDER TABLE */}
      <Card className="w-full">
        <CardHeader>
          <CardTitle>Logistics Queue</CardTitle>
          <CardDescription>Real-time order status and journey tracking.</CardDescription>
        </CardHeader>
        <CardContent>
           {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <Loader2 className="w-8 h-8 animate-spin mb-2" />
              <p>Loading orders...</p>
            </div>
          ) : filteredOrders.length === 0 ? (
            <div className="text-center py-16 text-muted-foreground bg-muted/10 rounded-lg border border-dashed">
              {searchTerm ? (
                  <>
                    <Search className="w-10 h-10 mx-auto mb-2 opacity-20" />
                    <p>No orders match "{searchTerm}".</p>
                  </>
              ) : (
                  <>
                    <Package className="w-10 h-10 mx-auto mb-2 opacity-20" />
                    <p>No orders found.</p>
                  </>
              )}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-border bg-muted/40">
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase">Code</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase">Route</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase">Priority</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase">Distance</th>
                    <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredOrders.map((order) => (
                    <tr 
                      key={order.id} 
                      className="group transition-colors hover:bg-muted/50 cursor-pointer"
                      onClick={() => handleOrderClick(order)}
                    >
                      <td className="py-4 px-4 font-semibold text-sm">{order.code}</td>
                      <td className="py-4 px-4">
                        <div className="flex flex-col gap-1 text-xs">
                           <div className="flex items-center gap-1 text-muted-foreground"><MapPin className="w-3 h-3"/> {order.from_location}</div>
                           <div className="flex items-center gap-1 font-medium"><ArrowRight className="w-3 h-3"/> {order.to_location}</div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                          <Badge variant="outline" className={`${getPriorityColor(order.priority)} border-0`}>{order.priority}</Badge>
                      </td>
                      <td className="py-4 px-4 font-mono text-sm">{order.total_distance.toFixed(1)} km</td>
                      <td className="py-4 px-4">
                        <Badge variant="secondary" className={`${getStatusColor(order.status)} border-0 font-medium`}>
                          {formatStatus(order.status)}
                        </Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* DETAIL MODAL */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="max-w-3xl max-h-[85vh] overflow-y-auto">
            <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                    <Package className="w-5 h-5 text-primary"/>
                    Order Journey: {selectedOrder?.code}
                </DialogTitle>
                <DialogDescription>
                    Tracking details and logistics legs for this order.
                </DialogDescription>
            </DialogHeader>

            {isLoadingDetails ? (
                <div className="py-12 flex justify-center"><Loader2 className="w-8 h-8 animate-spin text-primary"/></div>
            ) : (
                <div className="space-y-6 mt-4">
                    {/* Progress Line */}
                    <div className="relative border-l-2 border-muted ml-3 space-y-8 pb-4">
                        {orderLegs.length === 0 ? (
                            <div className="pl-6 text-muted-foreground italic">No journey plan generated yet.</div>
                        ) : orderLegs.map((leg, index) => (
                            <div key={leg.id} className="relative pl-8">
                                {/* Status Dot */}
                                <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full border-2 border-background ${
                                    leg.status === 'COMPLETED' ? 'bg-green-500' : 'bg-blue-500'
                                }`}></div>

                                <div className="flex flex-col gap-2 bg-muted/20 p-4 rounded-md border">
                                    <div className="flex items-center justify-between">
                                        <div className="font-semibold text-sm flex items-center gap-2">
                                            <Badge variant="outline">{leg.leg_type}</Badge>
                                            <span className="text-muted-foreground text-xs">Leg #{leg.sequence}</span>
                                        </div>
                                        <Badge className={getStatusColor(leg.status)}>{formatStatus(leg.status)}</Badge>
                                    </div>

                                    {/* Route Info */}
                                    <div className="grid grid-cols-2 gap-4 text-sm mt-2">
                                        <div className="space-y-1">
                                            <div className="text-xs text-muted-foreground uppercase flex items-center gap-1">
                                                <WarehouseIcon className="w-3 h-3"/> Origin
                                            </div>
                                            <div className="font-medium">
                                                {leg.origin_sme_id ? "SME Pickup Point" : 
                                                 (nameCache[leg.origin_warehouse_id || ''] || leg.origin_warehouse_id || "N/A")}
                                            </div>
                                        </div>
                                        <div className="space-y-1">
                                            <div className="text-xs text-muted-foreground uppercase flex items-center gap-1">
                                                <WarehouseIcon className="w-3 h-3"/> Destination
                                            </div>
                                            <div className="font-medium">
                                                {leg.destination_is_receiver ? "Customer Receiver" : 
                                                 (nameCache[leg.destination_warehouse_id || ''] || leg.destination_warehouse_id || "N/A")}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Shipper Info with Name Display */}
                                    <div className="border-t pt-2 mt-2 flex items-center justify-between text-sm">
                                        <div className="flex items-center gap-2 text-muted-foreground">
                                            <User className="w-4 h-4"/>
                                            <span>Shipper:</span>
                                            
                                            <div className="flex flex-col ml-2">
                                                {leg.assigned_shipper_id ? (
                                                    <>
                                                        <span className="text-foreground font-medium">
                                                            {leg.shipper_full_name || "Unknown Name"}
                                                        </span>
                                                        <span className="text-xs text-muted-foreground">
                                                            ID: {leg.assigned_shipper_id}
                                                        </span>
                                                    </>
                                                ) : (
                                                    <span className="text-muted-foreground italic">Unassigned</span>
                                                )}
                                            </div>
                                        </div>

                                        <div className="font-mono text-xs">
                                            Est. Dist: {leg.estimated_distance} km
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </DialogContent>
      </Dialog>
    </div>
  );
}