import { useState } from 'react';
import { Input } from '../../components/ui/input';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
// import { Badge } from '../../components/ui/badge'; 
import { 
  Search, Truck, KeyRound, ArrowLeft, 
  MapPin, Phone, User, Package, Scale, Ruler, 
  FileText, CalendarClock, CheckCircle2, CircleDashed 
} from 'lucide-react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001/api/v1/tracking';

// Helper: Format trạng thái sang tiếng Việt và màu sắc
const getStatusConfig = (status: string) => {
  switch (status) {
    case 'PENDING': return { label: 'Chờ xử lý', color: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: CircleDashed };
    case 'PICKUP_ASSIGNED': return { label: 'Đang điều phối lấy', color: 'bg-blue-100 text-blue-800 border-blue-200', icon: Truck };
    case 'PICKED_UP': return { label: 'Đã lấy hàng', color: 'bg-indigo-100 text-indigo-800 border-indigo-200', icon: Package };
    case 'IN_TRANSIT': return { label: 'Đang luân chuyển', color: 'bg-purple-100 text-purple-800 border-purple-200', icon: Truck };
    case 'OUT_FOR_DELIVERY': return { label: 'Đang giao hàng', color: 'bg-orange-100 text-orange-800 border-orange-200', icon: Truck };
    case 'COMPLETED': return { label: 'Giao thành công', color: 'bg-green-100 text-green-800 border-green-200', icon: CheckCircle2 };
    case 'CANCELLED': return { label: 'Đã hủy', color: 'bg-red-100 text-red-800 border-red-200', icon: CircleDashed };
    default: return { label: status, color: 'bg-gray-100 text-gray-800 border-gray-200', icon: CircleDashed };
  }
};

// Helper: Format loại chặng hành trình
const getLegTypeLabel = (type: string) => {
    const map: Record<string, string> = {
        'PICKUP': 'Lấy hàng',
        'TRANSFER': 'Luân chuyển/Trung chuyển',
        'DELIVERY': 'Giao hàng'
    };
    return map[type] || type;
};

export function TrackingPage() {
  const [step, setStep] = useState(1);
  const [orderCode, setOrderCode] = useState('');
  const [phone, setPhone] = useState('');
  const [otp, setOtp] = useState('');
  
  const [loading, setLoading] = useState(false);
  const [orderData, setOrderData] = useState<any>(null);
  const [error, setError] = useState('');

  const handleRequestOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!orderCode || !phone) { setError('Vui lòng nhập đủ thông tin'); return; }
    setLoading(true); setError('');
    try {
      await axios.post(`${API_BASE_URL}/request-otp`, { order_code: orderCode.trim(), phone_number: phone.trim() });
      setStep(2);
    } catch (err: any) { setError(err.response?.data?.detail || 'Lỗi hệ thống'); } 
    finally { setLoading(false); }
  };

  const handleVerifyOtp = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otp.length !== 6) { setError('Mã OTP phải có 6 số'); return; }
    setLoading(true); setError('');
    try {
      const response = await axios.post(`${API_BASE_URL}/verify-track`, {
        order_code: orderCode.trim(), phone_number: phone.trim(), otp: otp.trim()
      });
      setOrderData(response.data);
      setStep(1);
    } catch (err: any) { setError(err.response?.data?.detail || 'OTP sai hoặc hết hạn'); } 
    finally { setLoading(false); }
  };

  const resetSearch = () => {
    setOrderData(null); setOtp(''); setStep(1); setError('');
  };

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4 sm:px-6 lg:px-8 font-sans">
      
      {/* Header Compact */}
      <div className="max-w-3xl mx-auto text-center mb-8">
        <div className="inline-flex items-center justify-center p-3 bg-white rounded-full shadow-sm mb-4">
            <Truck className="h-8 w-8 text-blue-600" />
        </div>
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Tra cứu hành trình vận đơn</h1>
      </div>

      {/* Logic Form Nhập */}
      {!orderData && (
        <Card className="w-full max-w-md mx-auto shadow-xl border-slate-200">
          <CardContent className="pt-8 pb-8 px-6">
            {step === 1 ? (
               <form onSubmit={handleRequestOtp} className="space-y-5">
                  <div className="space-y-1">
                    <label className="text-sm font-semibold text-slate-700">Mã vận đơn</label>
                    <div className="relative">
                        <Package className="absolute left-3 top-2.5 h-5 w-5 text-slate-400" />
                        <Input className="pl-10 h-10" placeholder="VD: ORDER-12345" value={orderCode} onChange={(e) => setOrderCode(e.target.value.toUpperCase())} />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-sm font-semibold text-slate-700">Số điện thoại nhận hàng</label>
                    <div className="relative">
                        <Phone className="absolute left-3 top-2.5 h-5 w-5 text-slate-400" />
                        <Input className="pl-10 h-10" placeholder="VD: 0901234567" value={phone} onChange={(e) => setPhone(e.target.value)} />
                    </div>
                  </div>
                  <Button type="submit" className="w-full h-10 bg-blue-600 hover:bg-blue-700 font-medium text-base shadow-sm" disabled={loading}>
                    {loading ? 'Đang xử lý...' : 'Tra cứu ngay'}
                  </Button>
               </form>
            ) : (
                <form onSubmit={handleVerifyOtp} className="space-y-6 animate-in zoom-in-95 duration-200">
                    <div className="text-center">
                        <h3 className="text-lg font-semibold text-slate-900">Xác thực OTP</h3>
                        <p className="text-sm text-slate-500 mt-1">Mã xác thực đã được gửi tới SĐT của bạn</p>
                    </div>
                    <div className="flex justify-center">
                        <Input className="text-center text-3xl font-mono tracking-[0.5em] w-48 h-12" maxLength={6} value={otp} onChange={(e) => setOtp(e.target.value.replace(/[^0-9]/g, ''))} />
                    </div>
                    <Button type="submit" className="w-full h-10 bg-green-600 hover:bg-green-700 shadow-sm" disabled={loading}>
                        {loading ? 'Đang xác thực...' : 'Xem kết quả'}
                    </Button>
                    <button type="button" onClick={() => setStep(1)} className="w-full text-sm text-slate-500 hover:text-blue-600 flex items-center justify-center">
                        <ArrowLeft className="w-4 h-4 mr-1"/> Quay lại
                    </button>
                </form>
            )}
            {error && <div className="mt-4 p-3 text-sm text-red-600 bg-red-50 rounded-md border border-red-100 text-center flex items-center justify-center gap-2"><CircleDashed className="w-4 h-4"/> {error}</div>}
          </CardContent>
        </Card>
      )}

      {/* KẾT QUẢ TRA CỨU */}
      {orderData && (
        <div className="w-full max-w-4xl mx-auto animate-in slide-in-from-bottom-4 duration-500">
            
            {/* Header Card */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <p className="text-sm text-slate-500 font-medium uppercase tracking-wider mb-1">Mã vận đơn</p>
                    <div className="flex items-center gap-3">
                        <h2 className="text-3xl font-extrabold text-slate-900">{orderData.order_code}</h2>
                    </div>
                    <p className="text-sm text-slate-400 mt-1 flex items-center gap-1">
                        <CalendarClock className="w-4 h-4" /> Cập nhật lần cuối: {new Date(orderData.updated_at || orderData.created_at || new Date()).toLocaleString('vi-VN')}
                    </p>
                </div>
                <div className={`px-4 py-2 rounded-lg border ${getStatusConfig(orderData.status).color} flex items-center gap-2`}>
                    {(() => {
                        const StatusIcon = getStatusConfig(orderData.status).icon;
                        return <StatusIcon className="w-5 h-5" />;
                    })()}
                    <span className="font-bold text-sm md:text-base">{getStatusConfig(orderData.status).label}</span>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Cột trái: Thông tin chi tiết */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Thông tin kiện hàng */}
                    <Card className="shadow-sm border-slate-200 overflow-hidden">
                        <CardHeader className="bg-slate-50/50 pb-4 border-b border-slate-100">
                            <CardTitle className="text-base font-bold text-slate-800 flex items-center gap-2">
                                <Package className="w-5 h-5 text-blue-600" /> Thông tin kiện hàng
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-6 grid grid-cols-1 sm:grid-cols-2 gap-6">
                            <div className="flex items-start gap-3">
                                <div className="p-2 bg-blue-50 rounded-lg text-blue-600"><Scale className="w-5 h-5" /></div>
                                <div>
                                    <p className="text-xs text-slate-500 font-medium uppercase">Khối lượng</p>
                                    <p className="text-slate-900 font-semibold">{orderData.weight} kg</p>
                                </div>
                            </div>
                            <div className="flex items-start gap-3">
                                <div className="p-2 bg-purple-50 rounded-lg text-purple-600"><Ruler className="w-5 h-5" /></div>
                                <div>
                                    <p className="text-xs text-slate-500 font-medium uppercase">Kích thước</p>
                                    <p className="text-slate-900 font-semibold">{orderData.dimensions || 'Tiêu chuẩn'}</p>
                                </div>
                            </div>
                            {orderData.note && (
                                <div className="sm:col-span-2 flex items-start gap-3">
                                    <div className="p-2 bg-amber-50 rounded-lg text-amber-600"><FileText className="w-5 h-5" /></div>
                                    <div>
                                        <p className="text-xs text-slate-500 font-medium uppercase">Ghi chú</p>
                                        <p className="text-slate-700 italic">"{orderData.note}"</p>
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>

                    {/* Thông tin người nhận */}
                    <Card className="shadow-sm border-slate-200 overflow-hidden">
                        <CardHeader className="bg-slate-50/50 pb-4 border-b border-slate-100">
                            <CardTitle className="text-base font-bold text-slate-800 flex items-center gap-2">
                                <User className="w-5 h-5 text-green-600" /> Người nhận
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-6 space-y-4">
                            <div className="flex items-center gap-3">
                                <User className="w-4 h-4 text-slate-400" />
                                <span className="font-semibold text-slate-900">{orderData.receiver_name}</span>
                            </div>
                            <div className="flex items-center gap-3">
                                <Phone className="w-4 h-4 text-slate-400" />
                                <span className="text-slate-700 font-mono">{orderData.receiver_phone}</span>
                            </div>
                            <div className="flex items-start gap-3">
                                <MapPin className="w-4 h-4 text-slate-400 mt-1" />
                                <span className="text-slate-700 leading-relaxed">{orderData.receiver_address}</span>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Cột phải: Timeline hành trình (FIXED CSS) */}
                {/* Cột phải: Timeline hành trình */}
                <div className="lg:col-span-1">
                    <Card className="h-full shadow-sm border-slate-200">
                        <CardHeader className="bg-slate-50/50 pb-4 border-b border-slate-100">
                            {/* Đã bỏ icon Truck, chỉ để lại text */}
                            <CardTitle className="text-base font-bold text-slate-800">
                                Hành trình
                            </CardTitle>
                        </CardHeader>
                        <CardContent className="pt-6 px-4">
                             {/* Timeline container */}
                             <div className="relative border-l-2 border-slate-200 ml-5 space-y-8 pb-2">
                                
                                {(!orderData.journey || orderData.journey.length === 0) && (
                                    <div className="ml-6 text-sm text-slate-500 italic">Đơn hàng vừa được tạo.</div>
                                )}

                                {/* Lịch sử các chặng trước đó */}
                                {orderData.journey?.map((log: any, index: number) => (
                                    <div key={index} className="relative pl-8">
                                        {/* Dot xanh dương: Đã căn chỉnh chính xác giữa dòng kẻ */}
                                        <span className="absolute -left-[9px] top-1 bg-white border-2 border-blue-500 w-4 h-4 rounded-full"></span>
                                        
                                        <div className="flex flex-col">
                                            <span className="text-xs text-slate-400 font-medium mb-1">
                                                {new Date(log.updated_at || log.created_at || new Date()).toLocaleString('vi-VN', { hour: '2-digit', minute:'2-digit', day:'2-digit', month:'2-digit' })}
                                            </span>
                                            <h4 className="text-sm font-bold text-slate-900">{log.status}</h4>
                                            <p className="text-xs text-blue-600 bg-blue-50 w-fit px-2 py-0.5 rounded mt-1 font-medium">
                                                {getLegTypeLabel(log.leg_type)}
                                            </p>
                                        </div>
                                    </div>
                                ))}

                                {/* Điểm cuối cùng: Trạng thái hiện tại */}
                                <div className="relative pl-8">
                                    {/* Đã bỏ icon CheckCircle.
                                        Chỉnh kích thước w-4 h-4 và left -9px để thẳng hàng tuyệt đối với các chấm bên trên.
                                        Thêm hiệu ứng ring-green-100 để nổi bật hơn một chút nhưng vẫn gọn.
                                    */}
                                    <span className="absolute -left-[9px] top-1 bg-green-500 ring-4 ring-green-100 w-4 h-4 rounded-full"></span>
                                    
                                    <div className="flex flex-col">
                                        <span className="text-xs text-slate-400 font-medium mb-1">Hiện tại</span>
                                        <h4 className="text-sm font-bold text-green-700">
                                            {getStatusConfig(orderData.status).label}
                                        </h4>
                                    </div>
                                </div>
                             </div>
                        </CardContent>
                    </Card>
                </div>
            </div>

            <div className="mt-8 text-center">
                <Button onClick={resetSearch} variant="outline" className="border-slate-300 hover:bg-slate-50 text-slate-600">
                    <Search className="mr-2 h-4 w-4" /> Tra cứu đơn khác
                </Button>
            </div>
        </div>
      )}
    </div>
  );
}