import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { Package, TrendingUp, Users, Scale, ArrowUp, ArrowDown, Loader2, ShoppingCart } from 'lucide-react';
import { orderService, type OrderResponse } from '../../services/orderService';

// Map trạng thái sang màu sắc
const statusColors: Record<string, string> = {
  COMPLETED: 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-400',
  DELIVERING: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-400',
  IN_TRANSIT: 'bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-400',
  AT_WAREHOUSE: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-400',
  PENDING: 'bg-gray-100 text-gray-800 dark:bg-gray-950 dark:text-gray-400',
  CANCELLED: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-400',
};

export function OverviewPage() {
  const [orders, setOrders] = useState<OrderResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    totalOrders: 0,
    successRate: 0,
    activeOrders: 0, // Đang xử lý (Pending + In Transit + At Warehouse)
    totalWeight: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      // Gọi API lấy danh sách (Admin sẽ nhận được toàn bộ đơn hàng nếu Backend đã config đúng)
      const data = await orderService.getOrders();
      
      // Sắp xếp mới nhất lên đầu
      const sortedOrders = data.sort((a, b) => 
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
      setOrders(sortedOrders);

      // --- TÍNH TOÁN KPI TOÀN HỆ THỐNG ---
      const total = data.length;
      const completed = data.filter(o => o.status === 'COMPLETED').length;
      
      // Các trạng thái được coi là đang hoạt động/xử lý
      const active = data.filter(o => ['PENDING', 'IN_TRANSIT', 'AT_WAREHOUSE', 'DELIVERING', 'PICKED'].includes(o.status)).length;
      
      const weight = data.reduce((acc, curr) => acc + curr.weight, 0);

      setStats({
        totalOrders: total,
        successRate: total > 0 ? parseFloat(((completed / total) * 100).toFixed(1)) : 0,
        activeOrders: active,
        totalWeight: parseFloat(weight.toFixed(1))
      });

    } catch (error) {
      console.error("Failed to load overview data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const kpiData = [
    {
      title: 'Total Orders',
      value: stats.totalOrders.toString(),
      subtext: 'All time orders',
      icon: ShoppingCart,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100 dark:bg-blue-950',
    },
    {
      title: 'Success Rate',
      value: `${stats.successRate}%`,
      subtext: 'Completed orders',
      icon: TrendingUp,
      color: 'text-green-600',
      bgColor: 'bg-green-100 dark:bg-green-950',
    },
    {
      title: 'Active Processing',
      value: stats.activeOrders.toString(),
      subtext: 'Pending & In-transit',
      icon: Package,
      color: 'text-amber-600',
      bgColor: 'bg-amber-100 dark:bg-amber-950',
    },
    {
      title: 'Total Volume',
      value: `${stats.totalWeight} kg`,
      subtext: 'Total weight handled',
      icon: Scale,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100 dark:bg-purple-950',
    },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-100px)]">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-foreground mb-1 font-bold text-2xl">System Overview</h1>
        <p className="text-muted-foreground">
          Admin Dashboard - Real-time monitoring of all logistics operations.
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiData.map((kpi) => (
          <Card key={kpi.title} className="shadow-sm">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {kpi.title}
              </CardTitle>
              <div className={`w-8 h-8 ${kpi.bgColor} rounded-lg flex items-center justify-center`}>
                <kpi.icon className={`w-4 h-4 ${kpi.color}`} />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground mb-1">{kpi.value}</div>
              <p className="text-xs text-muted-foreground">{kpi.subtext}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recent Orders Table (Hiển thị 10 đơn mới nhất thay vì 5 để Admin dễ nhìn) */}
      <Card className="shadow-sm">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Latest Orders</CardTitle>
              <CardDescription>Most recent transactions across the system</CardDescription>
            </div>
            <Badge variant="outline" className="ml-auto">
              Total: {orders.length}
            </Badge>
          </div>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Order Code</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Recipient</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Address</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Date</th>
                  <th className="text-left py-3 px-4 text-sm font-medium text-muted-foreground">Status</th>
                  <th className="text-right py-3 px-4 text-sm font-medium text-muted-foreground">Weight</th>
                </tr>
              </thead>
              <tbody>
                {orders.slice(0, 10).map((order) => (
                  <tr key={order.order_id} className="border-b border-border hover:bg-muted/50 transition-colors">
                    <td className="py-3 px-4 text-sm font-medium text-foreground">
                      {order.order_code}
                    </td>
                    <td className="py-3 px-4 text-sm text-foreground">
                      {order.receiver_name}
                    </td>
                    <td className="py-3 px-4 text-sm text-foreground max-w-[250px] truncate" title={order.receiver_address}>
                      {order.receiver_address}
                    </td>
                    <td className="py-3 px-4 text-sm text-muted-foreground">
                      {new Date(order.created_at).toLocaleDateString('vi-VN')}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant="secondary" className={statusColors[order.status] || statusColors.PENDING}>
                        {order.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4 text-sm text-right text-foreground font-medium">
                      {order.weight} kg
                    </td>
                  </tr>
                ))}
                {orders.length === 0 && (
                  <tr>
                    <td colSpan={6} className="text-center py-12 text-muted-foreground">
                      No orders found in the system.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}