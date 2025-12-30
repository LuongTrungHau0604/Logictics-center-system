import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Download, FileText, TrendingUp, AlertCircle, Lightbulb, MapPin } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ordersPerDayData = [
  { date: 'Oct 7', orders: 42, successful: 40, failed: 2 },
  { date: 'Oct 8', orders: 48, successful: 46, failed: 2 },
  { date: 'Oct 9', orders: 55, successful: 53, failed: 2 },
  { date: 'Oct 10', orders: 51, successful: 49, failed: 2 },
  { date: 'Oct 11', orders: 63, successful: 61, failed: 2 },
  { date: 'Oct 12', orders: 58, successful: 55, failed: 3 },
  { date: 'Oct 13', orders: 67, successful: 65, failed: 2 },
];

const costPerCompanyData = [
  { company: 'Acme Corp', cost: 12400, orders: 145 },
  { company: 'TechStart Inc', cost: 8900, orders: 98 },
  { company: 'Global Traders', cost: 15200, orders: 178 },
  { company: 'FastShip Co', cost: 6700, orders: 72 },
  { company: 'LocalGoods', cost: 9800, orders: 112 },
];

const deliveryStatusData = [
  { name: 'Delivered', value: 847, color: '#10b981' },
  { name: 'In Transit', value: 124, color: '#3b82f6' },
  { name: 'Pickup', value: 58, color: '#f59e0b' },
  { name: 'Failed', value: 23, color: '#ef4444' },
];

const aiSuggestions = [
  {
    type: 'warehouse',
    title: 'Open New Warehouse in District 9',
    reason: 'High demand detected with 23% increase in orders from this area',
    impact: 'Reduce delivery time by 40% and costs by 25%',
    priority: 'high',
    estimatedCost: '$85,000',
  },
  {
    type: 'route',
    title: 'Optimize District 3-5 Route',
    reason: 'Current routes overlap, causing inefficiency',
    impact: 'Save 15% on fuel costs and improve delivery speed',
    priority: 'medium',
    estimatedCost: '$0 (route change)',
  },
  {
    type: 'shipper',
    title: 'Hire 3 Additional Shippers',
    reason: 'Peak hours show shipper shortage in Districts 1, 4, 7',
    impact: 'Handle 30% more orders during rush hours',
    priority: 'high',
    estimatedCost: '$18,000/month',
  },
  {
    type: 'capacity',
    title: 'Expand Warehouse B Capacity',
    reason: 'Currently at 77% capacity with growing demand',
    impact: 'Prevent bottlenecks and accommodate 40% more inventory',
    priority: 'medium',
    estimatedCost: '$45,000',
  },
];

const priorityColors = {
  high: 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-400',
  medium: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-400',
  low: 'bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-400',
};

export function ReportsPage() {
  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-foreground mb-1">Reports & Analytics</h1>
          <p className="text-muted-foreground">Insights and AI-powered recommendations</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
          <Button variant="outline" size="sm">
            <FileText className="w-4 h-4 mr-2" />
            Generate Report
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Total Orders (7 days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">384</div>
            <p className="text-sm text-accent flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              +18.2% from last week
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Success Rate</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">97.8%</div>
            <p className="text-sm text-accent flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              +1.2% improvement
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Total Revenue</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">$53,000</div>
            <p className="text-sm text-accent flex items-center gap-1">
              <TrendingUp className="w-3 h-3" />
              +24.5% increase
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">Cost Savings</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">$8,200</div>
            <p className="text-sm text-muted-foreground">From AI optimization</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Orders Per Day */}
        <Card>
          <CardHeader>
            <CardTitle>Orders Per Day</CardTitle>
            <CardDescription>Last 7 days performance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={ordersPerDayData}>
                  <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                  <XAxis dataKey="date" className="text-xs" />
                  <YAxis className="text-xs" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                  
                  <Legend />
                  <Line type="monotone" dataKey="orders" stroke="#3b82f6" strokeWidth={2} name="Total Orders" />
                  <Line type="monotone" dataKey="successful" stroke="#10b981" strokeWidth={2} name="Successful" />
                  <Line type="monotone" dataKey="failed" stroke="#ef4444" strokeWidth={2} name="Failed" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Delivery Status Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Delivery Status Distribution</CardTitle>
            <CardDescription>Current order status breakdown</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={deliveryStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {deliveryStatusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'hsl(var(--card))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: '8px'
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Cost Per Company */}
      <Card>
        <CardHeader>
          <CardTitle>Cost Summary by Company</CardTitle>
          <CardDescription>Total transportation costs per business</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] mb-6">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={costPerCompanyData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="company" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'hsl(var(--card))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: '8px'
                  }}
                  labelStyle={{ color: "hsl(var(--foreground))" }}
                  itemStyle={{ color: "hsl(var(--foreground))" }}
                />
                <Bar dataKey="cost" fill="#2563EB" name="Cost ($)" />
              </BarChart>
            </ResponsiveContainer>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-2 text-muted-foreground">Company</th>
                  <th className="text-right py-3 px-2 text-muted-foreground">Orders</th>
                  <th className="text-right py-3 px-2 text-muted-foreground">Total Cost</th>
                  <th className="text-right py-3 px-2 text-muted-foreground">Avg Cost/Order</th>
                </tr>
              </thead>
              <tbody>
                {costPerCompanyData.map((company) => (
                  <tr key={company.company} className="border-b border-border hover:bg-muted/50">
                    <td className="py-3 px-2 text-foreground">{company.company}</td>
                    <td className="py-3 px-2 text-right text-foreground">{company.orders}</td>
                    <td className="py-3 px-2 text-right text-foreground">${company.cost.toLocaleString()}</td>
                    <td className="py-3 px-2 text-right text-foreground">${Math.round(company.cost / company.orders)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* AI Suggestions */}
      <Card className="border-accent/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-accent/10 rounded-lg flex items-center justify-center">
              <Lightbulb className="w-5 h-5 text-accent" />
            </div>
            <div>
              <CardTitle>AI-Powered Suggestions</CardTitle>
              <CardDescription>Recommendations to improve efficiency and reduce costs</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {aiSuggestions.map((suggestion, i) => (
              <Card key={i} className="border-2 hover:border-primary transition-colors">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                      suggestion.type === 'warehouse' ? 'bg-blue-100 dark:bg-blue-950' :
                      suggestion.type === 'route' ? 'bg-green-100 dark:bg-green-950' :
                      suggestion.type === 'shipper' ? 'bg-purple-100 dark:bg-purple-950' :
                      'bg-amber-100 dark:bg-amber-950'
                    }`}>
                      {suggestion.type === 'warehouse' && <MapPin className="w-5 h-5 text-blue-600" />}
                      {suggestion.type === 'route' && <TrendingUp className="w-5 h-5 text-green-600" />}
                      {suggestion.type === 'shipper' && <svg className="w-5 h-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>}
                      {suggestion.type === 'capacity' && <svg className="w-5 h-5 text-amber-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
                      </svg>}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <h4 className="text-foreground">{suggestion.title}</h4>
                        <Badge 
                          variant="secondary" 
                          className={priorityColors[suggestion.priority as keyof typeof priorityColors]}
                        >
                          {suggestion.priority}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{suggestion.reason}</p>
                      <div className="flex items-center gap-2 mb-3 text-sm">
                        <AlertCircle className="w-4 h-4 text-accent" />
                        <span className="text-accent">{suggestion.impact}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          Estimated Cost: <span className="text-foreground">{suggestion.estimatedCost}</span>
                        </span>
                        <Button size="sm">
                          Review Details
                        </Button>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
