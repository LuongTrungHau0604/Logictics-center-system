import { useState } from "react";
import { Package, QrCode, Download, Upload, Filter, Search, ArrowUpDown, MapPin, BarChart3, AlertTriangle, ScanLine, ClipboardList, MoveHorizontal, PenSquare, Clock, TrendingUp, TrendingDown, Minus} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Input } from "../../components/ui/input";
import { Label } from "../../components/ui/label";
import { Badge } from "../../components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "../../components/ui/dialog";
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "../../components/ui/table";
import { Progress } from "../../components/ui/progress";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../components/ui/select";
import { RadioGroup, RadioGroupItem } from "../../components/ui/radio-group";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LabelList,
  ResponsiveContainer,
} from "recharts";

interface WarehousesInventoryPageProps {
  warehouseId?: string;
}

interface InventoryItem {
  id: string;
  sku: string;
  name: string;
  category: string;
  zone: string;
  onHand: number;
  reserved: number;
  available: number;
  status: "in-stock" | "low-stock" | "out-of-stock";
  reorderPoint: number;
}

interface ActivityLog {
  id: string;
  type: "inbound" | "outbound" | "relocation" | "adjustment";
  sku: string;
  quantity: number;
  zone: string;
  time: string;
  details: string;
}

export default function WarehousesInventoryPage({ warehouseId = "WH-001" }: WarehousesInventoryPageProps) {
  // Mock warehouse data
  const mockWarehouse = {
    id: "WH-001",
    name: "Warehouse A",
    location: "123 Logistics Blvd, District 7, Ho Chi Minh City",
    manager: "Nguyen Van Minh",
    phone: "+84 90 123 4567",
    status: "active" as const,
    capacity: 28000,
    currentLoad: 20900,
    zones: ["Zone A", "Zone B", "Zone C", "Cold Room", "Yard"],
  };

  // Mock inventory data
  const mockInventoryData: InventoryItem[] = [
    {
      id: "1",
      sku: "SKU-00123",
      name: "12L Insulated Container",
      category: "Cold Chain",
      zone: "Cold Room - Rack 2",
      onHand: 450,
      reserved: 120,
      available: 330,
      status: "in-stock",
      reorderPoint: 100,
    },
    {
      id: "2",
      sku: "SKU-00456",
      name: "Industrial Cardboard Box (Large)",
      category: "Dry Storage",
      zone: "Zone A - Rack 3 / Bin B12",
      onHand: 2400,
      reserved: 850,
      available: 1550,
      status: "in-stock",
      reorderPoint: 500,
    },
    {
      id: "3",
      sku: "SKU-00789",
      name: "Fragile Electronics Packaging",
      category: "Fragile",
      zone: "Zone B - Shelf 5",
      onHand: 85,
      reserved: 50,
      available: 35,
      status: "low-stock",
      reorderPoint: 100,
    },
    {
      id: "4",
      sku: "SKU-01234",
      name: "Frozen Food Pallet (Standard)",
      category: "Cold Chain",
      zone: "Cold Room - Rack 1",
      onHand: 320,
      reserved: 180,
      available: 140,
      status: "in-stock",
      reorderPoint: 80,
    },
    {
      id: "5",
      sku: "SKU-01567",
      name: "Pharmaceutical Storage Box",
      category: "Cold Chain",
      zone: "Cold Room - Rack 4",
      onHand: 45,
      reserved: 30,
      available: 15,
      status: "low-stock",
      reorderPoint: 50,
    },
    {
      id: "6",
      sku: "SKU-01890",
      name: "Heavy Machinery Parts Crate",
      category: "Dry Storage",
      zone: "Zone C - Floor Space 7",
      onHand: 180,
      reserved: 60,
      available: 120,
      status: "in-stock",
      reorderPoint: 40,
    },
    {
      id: "7",
      sku: "SKU-02123",
      name: "Textile Roll Storage",
      category: "Dry Storage",
      zone: "Zone A - Rack 8",
      onHand: 560,
      reserved: 200,
      available: 360,
      status: "in-stock",
      reorderPoint: 150,
    },
    {
      id: "8",
      sku: "SKU-02456",
      name: "Outdoor Equipment Container",
      category: "Dry Storage",
      zone: "Yard - Section 3",
      onHand: 12,
      reserved: 5,
      available: 7,
      status: "low-stock",
      reorderPoint: 20,
    },
    {
      id: "9",
      sku: "SKU-02789",
      name: "Chemical Storage Drum (Safe)",
      category: "Hazardous",
      zone: "Zone C - Isolation Area",
      onHand: 95,
      reserved: 25,
      available: 70,
      status: "in-stock",
      reorderPoint: 30,
    },
    {
      id: "10",
      sku: "SKU-03012",
      name: "Consumer Electronics Box",
      category: "Fragile",
      zone: "Zone B - Shelf 12",
      onHand: 0,
      reserved: 0,
      available: 0,
      status: "out-of-stock",
      reorderPoint: 60,
    },
    {
      id: "11",
      sku: "SKU-03345",
      name: "Beverage Pallet (24-pack)",
      category: "Dry Storage",
      zone: "Zone A - Rack 1",
      onHand: 1800,
      reserved: 600,
      available: 1200,
      status: "in-stock",
      reorderPoint: 300,
    },
    {
      id: "12",
      sku: "SKU-03678",
      name: "Medical Supplies Kit",
      category: "Cold Chain",
      zone: "Cold Room - Rack 3",
      onHand: 28,
      reserved: 20,
      available: 8,
      status: "low-stock",
      reorderPoint: 40,
    },
  ];

  // Mock activity log
  const mockActivityLog: ActivityLog[] = [
    {
      id: "1",
      type: "inbound",
      sku: "SKU-00123",
      quantity: 200,
      zone: "Cold Room - Rack 2",
      time: "10:32 AM",
      details: "Received from Supplier ABC",
    },
    {
      id: "2",
      type: "outbound",
      sku: "SKU-00456",
      quantity: 50,
      zone: "Zone A - Rack 3 / Bin B12",
      time: "09:15 AM",
      details: "Dispatched to Route #VN-HCM-23",
    },
    {
      id: "3",
      type: "relocation",
      sku: "SKU-01234",
      quantity: 80,
      zone: "Cold Room - Rack 1",
      time: "08:45 AM",
      details: "Moved from Zone B to Cold Room",
    },
    {
      id: "4",
      type: "adjustment",
      sku: "SKU-00789",
      quantity: -5,
      zone: "Zone B - Shelf 5",
      time: "Yesterday 4:20 PM",
      details: "Stock count adjustment - Damaged",
    },
    {
      id: "5",
      type: "inbound",
      sku: "SKU-02123",
      quantity: 150,
      zone: "Zone A - Rack 8",
      time: "Yesterday 2:10 PM",
      details: "Received from Supplier XYZ",
    },
    {
      id: "6",
      type: "outbound",
      sku: "SKU-01567",
      quantity: 15,
      zone: "Cold Room - Rack 4",
      time: "Yesterday 11:30 AM",
      details: "Dispatched to Route #VN-HN-45",
    },
  ];

  // Chart data for stock by zone
  const zoneChartData = [
    { zone: "Zone A", units: 4760, capacity: 8000 },
    { zone: "Zone B", units: 3200, capacity: 6000 },
    { zone: "Zone C", units: 2850, capacity: 5000 },
    { zone: "Cold Room", units: 843, capacity: 3000 },
    { zone: "Yard", units: 247, capacity: 6000 },
  ];

  // State
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [inventoryItems, setInventoryItems] = useState<InventoryItem[]>(mockInventoryData);
  
  // Dialog states
  const [scanDialogOpen, setScanDialogOpen] = useState(false);
  const [moveDialogOpen, setMoveDialogOpen] = useState(false);
  const [adjustDialogOpen, setAdjustDialogOpen] = useState(false);
  
  // Selected item for dialogs
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  
  // Scan dialog state
  const [scanType, setScanType] = useState<"inbound" | "outbound">("inbound");
  const [scanCode, setScanCode] = useState("");
  
  // Move dialog state
  const [targetZone, setTargetZone] = useState("");
  const [moveQuantity, setMoveQuantity] = useState("");
  
  // Adjust dialog state
  const [newQuantity, setNewQuantity] = useState("");
  const [adjustReason, setAdjustReason] = useState("");

  // Computed values
  const totalSKUs = inventoryItems.length;
  const totalUnits = inventoryItems.reduce((sum, item) => sum + item.onHand, 0);
  const utilizationPercent = Math.round((mockWarehouse.currentLoad / mockWarehouse.capacity) * 100);
  const lowStockCount = inventoryItems.filter((item) => item.status === "low-stock").length;

  // Filter inventory
  const filteredInventory = inventoryItems.filter((item) => {
    const matchesSearch =
      item.sku.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || item.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Low stock items for alerts
  const lowStockItems = inventoryItems
    .filter((item) => item.status === "low-stock" || item.status === "out-of-stock")
    .slice(0, 5);

  // Handle dialog actions
  const handleScanConfirm = () => {
    // Mock scan action
    console.log("Scanning:", scanType, scanCode);
    setScanDialogOpen(false);
    setScanCode("");
  };

  const handleMoveConfirm = () => {
    if (!selectedItem) return;
    // Mock move action
    console.log("Moving:", selectedItem.sku, "to", targetZone, "quantity:", moveQuantity);
    setMoveDialogOpen(false);
    setTargetZone("");
    setMoveQuantity("");
    setSelectedItem(null);
  };

  const handleAdjustConfirm = () => {
    if (!selectedItem) return;
    // Mock adjust action
    console.log("Adjusting:", selectedItem.sku, "new quantity:", newQuantity, "reason:", adjustReason);
    
    // Update inventory optimistically
    setInventoryItems((items) =>
      items.map((item) =>
        item.id === selectedItem.id
          ? {
              ...item,
              onHand: parseInt(newQuantity) || 0,
              available: Math.max(0, (parseInt(newQuantity) || 0) - item.reserved),
              status:
                parseInt(newQuantity) === 0
                  ? "out-of-stock"
                  : parseInt(newQuantity) < item.reorderPoint
                  ? "low-stock"
                  : "in-stock",
            }
          : item
      )
    );
    
    setAdjustDialogOpen(false);
    setNewQuantity("");
    setAdjustReason("");
    setSelectedItem(null);
  };

  const openMoveDialog = (item: InventoryItem) => {
    setSelectedItem(item);
    setMoveDialogOpen(true);
  };

  const openAdjustDialog = (item: InventoryItem) => {
    setSelectedItem(item);
    setNewQuantity(item.onHand.toString());
    setAdjustDialogOpen(true);
  };

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case "in-stock":
        return "default";
      case "low-stock":
        return "secondary";
      case "out-of-stock":
        return "destructive";
      default:
        return "default";
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "inbound":
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case "outbound":
        return <TrendingDown className="h-4 w-4 text-blue-500" />;
      case "relocation":
        return <MoveHorizontal className="h-4 w-4 text-purple-500" />;
      case "adjustment":
        return <Minus className="h-4 w-4 text-orange-500" />;
      default:
        return <Package className="h-4 w-4" />;
    }
  };

  const getActivityBadgeVariant = (type: string) => {
    switch (type) {
      case "inbound":
        return "default";
      case "outbound":
        return "secondary";
      case "relocation":
        return "outline";
      case "adjustment":
        return "secondary";
      default:
        return "default";
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
        <div className="space-y-3">
          <div>
            <h1 className="flex items-center gap-2">
              {mockWarehouse.name} - Inventory
            </h1>
            <p className="text-muted-foreground mt-1">
              Real-time overview of stock levels, zones, and SKUs for this warehouse
            </p>
          </div>
          
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-muted-foreground">
            <div className="flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              <span>{mockWarehouse.location}</span>
            </div>
            <div className="flex items-center gap-4">
              <span></span>
              <span>Manager: {mockWarehouse.manager}</span>
              <span>Phone: {mockWarehouse.phone}</span>
              <Badge variant={mockWarehouse.status === "active" ? "default" : "secondary"}>
                {mockWarehouse.status}
              </Badge>
            </div>
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <Button onClick={() => setScanDialogOpen(true)} className="gap-2">
            <QrCode className="h-4 w-4" />
            Scan Goods
          </Button>
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            Export Inventory
          </Button>
          <Button variant="outline" className="gap-2">
            <Upload className="h-4 w-4" />
            Import CSV
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total SKUs</CardDescription>
            <CardTitle className="flex items-baseline gap-2">
              {totalSKUs}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Unique products in this warehouse</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Total On-hand Units</CardDescription>
            <CardTitle className="flex items-baseline gap-2">
              {totalUnits.toLocaleString()}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">All zones combined</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Utilization</CardDescription>
            <CardTitle className="flex items-baseline gap-2">
              {utilizationPercent}%
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Progress value={utilizationPercent} className="mb-2" />
            <p className="text-muted-foreground">Based on storage capacity</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Low Stock Alerts</CardDescription>
            <CardTitle className="flex items-baseline gap-2">
              {lowStockCount}
              <AlertTriangle className="h-5 w-5 text-orange-500" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">Below reorder point</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content - Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-[2fr,1fr] gap-6">
        {/* Left Column - Inventory Table */}
        <Card>
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <CardTitle>Inventory Items</CardTitle>
                <CardDescription>All SKUs currently stored in this warehouse</CardDescription>
              </div>
              
              <div className="flex flex-wrap items-center gap-2">
                <div className="relative flex-1 md:flex-initial md:w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search SKU, name, or code…"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
                
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Status filter" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="in-stock">In Stock</SelectItem>
                    <SelectItem value="low-stock">Low Stock</SelectItem>
                    <SelectItem value="out-of-stock">Out of Stock</SelectItem>
                  </SelectContent>
                </Select>
                
                <Button variant="outline" size="icon">
                  <Filter className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="rounded-xl border overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="text-center">
                      <div className="flex items-center justify-center gap-1">
                        SKU / Code
                        <ArrowUpDown className="h-3 w-3" />
                      </div>
                    </TableHead>
                    <TableHead>Product Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Zone / Location</TableHead>
                    <TableHead className="text-center">On-hand</TableHead>
                    <TableHead className="text-center">Reserved</TableHead>
                    <TableHead className="text-center">Available</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-center">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredInventory.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={9} className="text-center text-muted-foreground py-8">
                        No inventory items found
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredInventory.map((item) => (
                      <TableRow key={item.id} className="hover:bg-muted/50">
                        <TableCell className="text-center">{item.sku}</TableCell>
                        <TableCell>{item.name}</TableCell>
                        <TableCell>
                          <Badge variant="outline">{item.category}</Badge>
                        </TableCell>
                        <TableCell className="text-muted-foreground">{item.zone}</TableCell>
                        <TableCell className="text-center">{item.onHand}</TableCell>
                        <TableCell className="text-center">{item.reserved}</TableCell>
                        <TableCell className="text-center">{item.available}</TableCell>
                        <TableCell>
                          <Badge variant={getStatusBadgeVariant(item.status)}>
                            {item.status === "in-stock"
                              ? "In Stock"
                              : item.status === "low-stock"
                              ? "Low Stock"
                              : "Out of Stock"}
                          </Badge>
                        </TableCell>
                        <TableCell className="text-center">
                          <div className="inline-flex justify-center gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => openMoveDialog(item)}
                              className="h-8 gap-1"
                            >
                              <MoveHorizontal className="h-3 w-3" />
                              Move
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => openAdjustDialog(item)}
                              className="h-8 gap-1"
                            >
                              <PenSquare className="h-3 w-3" />
                              Adjust
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        {/* Right Column - Analytics & Alerts */}
        <div className="space-y-6">
          {/* Stock by Zone Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Stock Distribution by Zone
              </CardTitle>
              <CardDescription>Where inventory is physically located</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={zoneChartData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis
                    dataKey="zone"
                    tick={{ fontSize: 12 }}
                    className="text-muted-foreground"
                  />
                  <YAxis tick={{ fontSize: 12 }} className="text-muted-foreground" />
                  <Tooltip
                    contentStyle={{
                        backgroundColor: "hsl(var(--card))",
                        border: "1px solid hsl(var(--border))",
                        borderRadius: "8px",
                        padding: "6px 10px",
                    }}
                    labelStyle={{ color: "hsl(var(--foreground))" }}
                    itemStyle={{ color: "hsl(var(--foreground))" }}
                  />

                  <Bar dataKey="units" fill="#2563EB" radius={[8, 8, 0, 0]}>
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Capacity & Alerts */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-500" />
                Capacity & Alerts
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-muted-foreground mb-2">
                  <span>Capacity Used</span>
                  <span>
                    {mockWarehouse.currentLoad.toLocaleString()} / {mockWarehouse.capacity.toLocaleString()} units
                  </span>
                </div>
                <Progress value={utilizationPercent} className="h-2" />
              </div>

              <div className="space-y-3 pt-2">
                <p className="text-muted-foreground">Low Stock Items:</p>
                {lowStockItems.length === 0 ? (
                  <p className="text-muted-foreground">No low stock alerts</p>
                ) : (
                  lowStockItems.map((item) => (
                    <div
                      key={item.id}
                      className="flex items-start gap-2 p-3 rounded-xl border bg-muted/30"
                    >
                      <AlertTriangle
                        className={`h-4 w-4 mt-0.5 ${
                          item.status === "out-of-stock" ? "text-red-500" : "text-orange-500"
                        }`}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="truncate">{item.name}</p>
                        <p className="text-muted-foreground">
                          {item.sku} • {item.available} units available
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity Log */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Recent Movements
              </CardTitle>
              <CardDescription>Last 6 stock movements</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {mockActivityLog.map((activity) => (
                  <div key={activity.id} className="flex gap-3 pb-3 border-b last:border-0 last:pb-0">
                    <div className="mt-1">{getActivityIcon(activity.type)}</div>
                    <div className="flex-1 min-w-0 space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge variant={getActivityBadgeVariant(activity.type)}>
                          {activity.type.charAt(0).toUpperCase() + activity.type.slice(1)}
                        </Badge>
                        <span className="text-muted-foreground">{activity.time}</span>
                      </div>
                      <p className="truncate">
                        {activity.sku} • {Math.abs(activity.quantity)} units
                      </p>
                      <p className="text-muted-foreground truncate">
                        {activity.details}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Scan Goods Dialog */}
      <Dialog open={scanDialogOpen} onOpenChange={setScanDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Scan Goods</DialogTitle>
            <DialogDescription>
              Scan barcode or QR code to register inbound/outbound inventory for {mockWarehouse.name}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Operation Type</Label>
              <RadioGroup value={scanType} onValueChange={(value: any) => setScanType(value)}>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="inbound" id="inbound" />
                  <Label htmlFor="inbound" className="cursor-pointer">
                    Inbound (Receiving goods)
                  </Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="outbound" id="outbound" />
                  <Label htmlFor="outbound" className="cursor-pointer">
                    Outbound (Dispatching goods)
                  </Label>
                </div>
              </RadioGroup>
            </div>

            <div className="space-y-2">
              <Label htmlFor="scan-code">Barcode / QR Code</Label>
              <Input
                id="scan-code"
                placeholder="Enter or scan code..."
                value={scanCode}
                onChange={(e) => setScanCode(e.target.value)}
              />
            </div>

            <div className="flex items-center justify-center p-8 border-2 border-dashed rounded-xl bg-muted/30">
              <div className="text-center space-y-2">
                <QrCode className="h-12 w-12 mx-auto text-muted-foreground" />
                <p className="text-muted-foreground">
                  Position barcode in scanner range
                </p>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setScanDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleScanConfirm} disabled={!scanCode}>
              Confirm Scan
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Move Stock Dialog */}
      <Dialog open={moveDialogOpen} onOpenChange={setMoveDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Move Stock</DialogTitle>
            <DialogDescription>
              Relocate inventory to a different zone within the warehouse
            </DialogDescription>
          </DialogHeader>

          {selectedItem && (
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Product</Label>
                <div className="p-3 rounded-xl border bg-muted/30">
                  <p>{selectedItem.name}</p>
                  <p className="text-muted-foreground">{selectedItem.sku}</p>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Current Zone</Label>
                <Input value={selectedItem.zone} disabled />
              </div>

              <div className="space-y-2">
                <Label htmlFor="target-zone">Target Zone</Label>
                <Select value={targetZone} onValueChange={setTargetZone}>
                  <SelectTrigger id="target-zone">
                    <SelectValue placeholder="Select target zone" />
                  </SelectTrigger>
                  <SelectContent>
                    {mockWarehouse.zones
                      .filter((zone) => !selectedItem.zone.includes(zone))
                      .map((zone) => (
                        <SelectItem key={zone} value={zone}>
                          {zone}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="move-quantity">Quantity to Move</Label>
                <Input
                  id="move-quantity"
                  type="number"
                  placeholder="Enter quantity"
                  value={moveQuantity}
                  onChange={(e) => setMoveQuantity(e.target.value)}
                  max={selectedItem.available}
                />
                <p className="text-muted-foreground">
                  Maximum available: {selectedItem.available} units
                </p>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setMoveDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleMoveConfirm}
              disabled={
                !targetZone ||
                !moveQuantity ||
                parseInt(moveQuantity) <= 0 ||
                (selectedItem && parseInt(moveQuantity) > selectedItem.available)
              }
            >
              Confirm Move
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Adjust Stock Dialog */}
      <Dialog open={adjustDialogOpen} onOpenChange={setAdjustDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Adjust Stock</DialogTitle>
            <DialogDescription>
              Update inventory quantity due to stock count, damage, or loss
            </DialogDescription>
          </DialogHeader>

          {selectedItem && (
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label>Product</Label>
                <div className="p-3 rounded-xl border bg-muted/30">
                  <p>{selectedItem.name}</p>
                  <p className="text-muted-foreground">{selectedItem.sku}</p>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Current Quantity</Label>
                <Input value={selectedItem.onHand} disabled />
              </div>

              <div className="space-y-2">
                <Label htmlFor="new-quantity">New Quantity</Label>
                <Input
                  id="new-quantity"
                  type="number"
                  placeholder="Enter new quantity"
                  value={newQuantity}
                  onChange={(e) => setNewQuantity(e.target.value)}
                  min="0"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="adjust-reason">Reason</Label>
                <Select value={adjustReason} onValueChange={setAdjustReason}>
                  <SelectTrigger id="adjust-reason">
                    <SelectValue placeholder="Select reason" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="stock-count">Stock Count</SelectItem>
                    <SelectItem value="damaged">Damaged</SelectItem>
                    <SelectItem value="lost">Lost</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setAdjustDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleAdjustConfirm}
              disabled={!newQuantity || !adjustReason || newQuantity === selectedItem?.onHand.toString()}
            >
              Confirm Adjustment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
