import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Badge } from '../../components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '../../components/ui/dialog';
import { Label } from '../../components/ui/label';
import { Textarea } from '../../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
// Import các icon cần thiết
import { Plus, Search, MoreVertical, Edit, Trash2, Loader2, MapPin } from 'lucide-react'; 
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '../../components/ui/dropdown-menu';
import { areaService, Area, CreateAreaRequest } from '../../services/areaService';
import { geocodingService, AddressSuggestion } from '../../services/geocodingService';
import { createPortal } from 'react-dom';
import { toast } from "sonner";

export function AreasPage() {
  const [areas, setAreas] = useState<Area[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Dialog State
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  
  // --- STATE CHO MANUAL AUTOCOMPLETE (Giống OrdersPage) ---
  const [addressInput, setAddressInput] = useState('');
  const [suggestions, setSuggestions] = useState<AddressSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [debouncedAddress, setDebouncedAddress] = useState('');
  
  // Ref để xử lý click ra ngoài (Click Outside)
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Form State
  const [formData, setFormData] = useState<CreateAreaRequest>({
    name: '',
    type: 'CUSTOM',
    status: 'ACTIVE',
    description: '',
    radius_km: 5,
    center_latitude: 10.762622, 
    center_longitude: 106.660172
  });

  // Load Data
  useEffect(() => { fetchAreas(); }, []);

  const fetchAreas = async () => {
    setLoading(true);
    const data = await areaService.getAllAreas();
    setAreas(data);
    setLoading(false);
  };

  // --- LOGIC AUTOCOMPLETE (Thủ công) ---
  
  // 1. Debounce Input
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedAddress(addressInput), 500);
    return () => clearTimeout(timer);
  }, [addressInput]);

  // 2. Fetch API Suggestions
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!debouncedAddress || debouncedAddress.length < 3) {
        setSuggestions([]);
        return;
      }
      
      // Nếu text giống description đã chọn thì không search lại
      if (debouncedAddress === formData.description) return;

      try {
          const results = await geocodingService.getSuggestions(debouncedAddress);
          setSuggestions(results);
          setShowSuggestions(true);
      } catch (e) { console.error(e); }
    };
    fetchSuggestions();
  }, [debouncedAddress]);

  // 3. Xử lý Click ra ngoài để đóng Popup (Quan trọng)
  useEffect(() => {
    function handleClickOutside(event: any) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [wrapperRef]);

  // 4. Chọn địa chỉ
  const handleSelectAddress = async (suggestion: AddressSuggestion) => {
    setAddressInput(suggestion.description);
    setShowSuggestions(false); // Đóng popup

    try {
      const detail = await geocodingService.getPlaceDetail(suggestion.place_id);
      if (detail) {
        setFormData(prev => ({
          ...prev,
          center_latitude: detail.latitude,
          center_longitude: detail.longitude,
          description: suggestion.description 
        }));
        toast.success("Coordinates updated!");
      }
    } catch (error) {
      toast.error("Error getting location details.");
    }
  };
  // --- END LOGIC ---

  const handleInputChange = (field: keyof CreateAreaRequest, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleOpenCreate = () => {
    setEditingId(null);
    setAddressInput('');
    setSuggestions([]);
    setShowSuggestions(false);
    setFormData({
      name: '',
      type: 'CUSTOM',
      status: 'ACTIVE',
      description: '',
      radius_km: 5,
      center_latitude: 10.762622,
      center_longitude: 106.660172
    });
    setIsDialogOpen(true);
  };

  const handleOpenEdit = (area: Area) => {
    setEditingId(area.area_id);
    setAddressInput(area.description || ''); 
    setSuggestions([]);
    setShowSuggestions(false);
    setFormData({
      name: area.name,
      type: area.type,
      status: area.status,
      description: area.description || '',
      radius_km: area.radius_km,
      center_latitude: area.center_latitude,
      center_longitude: area.center_longitude
    });
    setIsDialogOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      if (editingId) {
        await areaService.updateArea(editingId, formData);
        toast.success("Area updated successfully");
      } else {
        await areaService.createArea(formData);
        toast.success("Area created successfully");
      }
      setIsDialogOpen(false);
      fetchAreas();
    } catch (error: any) {
      console.error(error);
      toast.error("Failed to save area.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
     if (!confirm("Are you sure?")) return;
     try {
       await areaService.deleteArea(id);
       toast.success("Deleted");
       fetchAreas();
     } catch(e) { toast.error("Failed"); }
  };

  const filteredAreas = areas.filter(area => 
    area.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Area Management</h1>
          <p className="text-muted-foreground">Manage logistics zones, cities, and districts.</p>
        </div>
        <Button onClick={handleOpenCreate}>
          <Plus className="w-4 h-4 mr-2" /> Add Area
        </Button>
      </div>

       <Card>
        <CardContent className="pt-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <Input 
              placeholder="Search areas..." className="pl-9 max-w-md"
              value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Areas List ({filteredAreas.length})</CardTitle>
          <CardDescription>List of all operational areas.</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-primary" /></div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-3 text-left">Name</th>
                    <th className="p-3 text-left">Type</th>
                    <th className="p-3 text-left">Status</th>
                    <th className="p-3 text-left">Coordinates</th>
                    <th className="p-3 text-left">Radius</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAreas.map((area) => (
                    <tr key={area.area_id} className="border-b hover:bg-muted/50">
                      <td className="p-3"><div className="font-medium">{area.name}</div></td>
                      <td className="p-3"><Badge variant="outline">{area.type}</Badge></td>
                      <td className="p-3"><Badge variant={area.status === 'ACTIVE' ? 'default' : 'secondary'}>{area.status}</Badge></td>
                      <td className="p-3 font-mono text-xs">{area.center_latitude?.toFixed(4)}, {area.center_longitude?.toFixed(4)}</td>
                      <td className="p-3">{area.radius_km} km</td>
                      <td className="p-3 text-right">
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild><Button variant="ghost" size="icon"><MoreVertical className="w-4 h-4" /></Button></DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleOpenEdit(area)}><Edit className="w-4 h-4 mr-2" /> Edit</DropdownMenuItem>
                            <DropdownMenuItem className="text-red-600" onClick={() => handleDelete(area.area_id)}><Trash2 className="w-4 h-4 mr-2" /> Delete</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* --- FORM DIALOG --- */}
      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        {/* Quan trọng: overflow-visible để popup đè lên được */}
        <DialogContent className="max-w-lg overflow-visible"> 
          <DialogHeader>
            <DialogTitle>{editingId ? 'Edit Area' : 'Create New Area'}</DialogTitle>
            <DialogDescription>Search for a central location and define the radius.</DialogDescription>
          </DialogHeader>
          
          <form onSubmit={handleSubmit} className="space-y-4 py-4">
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input 
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  required placeholder="e.g. HCM District 1"
                />
              </div>
              <div className="space-y-2">
                <Label>Type</Label>
                <Select 
                  value={formData.type} 
                  onValueChange={(val) => handleInputChange('type', val)}
                >
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="CITY">City</SelectItem>
                    <SelectItem value="DISTRICT">District</SelectItem>
                    <SelectItem value="REGION">Region</SelectItem>
                    <SelectItem value="CUSTOM">Custom</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* --- MANUAL ADDRESS AUTOCOMPLETE (Giống OrdersPage) --- */}
            {/* Sử dụng wrapperRef để detect click outside */}
            <div className="space-y-2 relative" ref={wrapperRef}>
              <Label>Central Address</Label>
              <Input 
                placeholder="Type address to search..." 
                value={addressInput} 
                onChange={(e) => {
                  setAddressInput(e.target.value);
                  if (e.target.value.length === 0) setShowSuggestions(false);
                }}
                // Khi focus, nếu có suggestion cũ thì hiện lại
                onFocus={() => {
                   if(suggestions.length > 0) setShowSuggestions(true);
                }}
                autoComplete="off" 
              />
              
              {/* Dropdown Container: Absolute, z-50, nền trắng cứng */}
              {showSuggestions && suggestions.length > 0 && (
                <div 
                  className="absolute z-50 w-full bg-white border border-gray-200 rounded-md shadow-lg mt-1 max-h-60 overflow-y-auto"
                  style={{ 
                    position: 'absolute',
                    zIndex: 9999,
                    backgroundColor: '#ffffff',
                  }}
                >
                  {suggestions.map((item, index) => (
                    <div 
                      key={item.place_id || index} 
                      className="flex items-center gap-2" 
                      onClick={() => handleSelectAddress(item)}
                      style={{ 
                        padding: '0.75rem',
                        cursor: 'pointer',
                        borderBottom: '1px solid #f9fafb',
                        color: '#374151',
                        fontSize: '0.875rem'
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#f3f4f6'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    >
                      <MapPin className="w-4 h-4 text-gray-400 shrink-0" />
                      <span>{item.label || item.description}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
            
            {/* Các field bên dưới */}
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Radius (km)</Label>
                <Input 
                  type="number" step="0.1"
                  value={formData.radius_km}
                  onChange={(e) => handleInputChange('radius_km', parseFloat(e.target.value))}
                  required 
                />
              </div>
              <div className="space-y-2">
                <Label>Status</Label>
                <Select 
                  value={formData.status} 
                  onValueChange={(val) => handleInputChange('status', val)}
                >
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ACTIVE">Active</SelectItem>
                    <SelectItem value="INACTIVE">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea 
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Additional notes..."
              />
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                {editingId ? 'Update Area' : 'Create Area'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}