import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { Badge } from "../../components/ui/badge";
import {
  Download,
  FileText,
  TrendingUp,
  TrendingDown,
  MapPin,
  Phone,
  Mail,
  Truck,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

// Mock data for a single company – e.g. “Acme Corp”
const companyInfo = {
  id: "COMP-001",
  name: "Acme Corp",
  industry: "E-commerce / Retail",
  location: "District 1, Ho Chi Minh City",
  contactName: "Tran Thi Mai",
  phone: "+84 90 555 1234",
  email: "logistics@acmecorp.vn",
  avgSla: "2.1 days",
  tier: "Premium",
};

const companyOrdersPerDayData = [
  { date: "Oct 7", orders: 18, successful: 17, failed: 1 },
  { date: "Oct 8", orders: 21, successful: 21, failed: 0 },
  { date: "Oct 9", orders: 24, successful: 23, failed: 1 },
  { date: "Oct 10", orders: 19, successful: 19, failed: 0 },
  { date: "Oct 11", orders: 26, successful: 25, failed: 1 },
  { date: "Oct 12", orders: 23, successful: 22, failed: 1 },
  { date: "Oct 13", orders: 24, successful: 24, failed: 0 },
];

const companyRouteCostData = [
  { route: "District 1 → District 3", orders: 72, cost: 4100 },
  { route: "District 1 → District 7", orders: 38, cost: 2600 },
  { route: "District 1 → Thu Duc", orders: 21, cost: 1850 },
  { route: "Warehouse A → District 4", orders: 14, cost: 1150 },
];

const companyStatusData = [
  { name: "Delivered", value: 231, color: "#10b981" },
  { name: "In Transit", value: 27, color: "#3b82f6" },
  { name: "Pickup", value: 9, color: "#f59e0b" },
  { name: "Failed", value: 6, color: "#ef4444" },
];

const companyAiSuggestions = [
  {
    title: "Create Dedicated Pickup Time Window",
    impact: "Reduce failed delivery attempts by 35%",
    detail:
      "Most failed orders for Acme Corp occur between 11:00–13:00 when recipients are not at home. Suggest setting a dedicated 18:00–21:00 slot.",
    priority: "high",
  },
  {
    title: "Switch 60% of District 3 Orders to Route #D3-Express",
    impact: "Save 12% on delivery cost per order",
    detail:
      "Historical data shows better performance and lower fuel cost on the D3-Express route compared to the current mixed route.",
    priority: "medium",
  },
  {
    title: "Pre-allocate Capacity in Warehouse B",
    impact: "Prevent stockout risk during weekend campaigns",
    detail:
      "Traffic from Acme Corp spikes 40–50% on weekends; reserving 120 pallet positions at Warehouse B will stabilize lead time.",
    priority: "medium",
  },
];

const priorityColor: Record<"high" | "medium" | "low", string> = {
  high: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-400",
  medium:
    "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-400",
  low: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-400",
};

export function ReportsCompanyPage() {
  // computed mock KPIs
  const totalOrders = companyOrdersPerDayData.reduce(
    (sum, d) => sum + d.orders,
    0
  );
  const successfulOrders = companyOrdersPerDayData.reduce(
    (sum, d) => sum + d.successful,
    0
  );
  const failedOrders = companyOrdersPerDayData.reduce(
    (sum, d) => sum + d.failed,
    0
  );
  const successRate = ((successfulOrders / totalOrders) * 100).toFixed(1);
  const totalCost = companyRouteCostData.reduce(
    (sum, r) => sum + r.cost,
    0
  );
  const avgCostPerOrder = Math.round(totalCost / totalOrders);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="space-y-1">
          <h1 className="text-foreground">Company Report</h1>
          <p className="text-muted-foreground">
            Performance and cost analytics for{" "}
            <span className="font-medium text-foreground">
              {companyInfo.name}
            </span>
          </p>
          <div className="flex flex-wrap items-center gap-3 text-sm text-muted-foreground mt-2">
            <span className="inline-flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              {companyInfo.location}
            </span>
            <span className="inline-flex items-center gap-1">
              <Phone className="w-3 h-3" />
              {companyInfo.phone}
            </span>
            <span className="inline-flex items-center gap-1">
              <Mail className="w-3 h-3" />
              {companyInfo.email}
            </span>
            <Badge variant="outline" className="ml-0">
              {companyInfo.tier} client
            </Badge>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
          <Button variant="outline" size="sm">
            <FileText className="w-4 h-4 mr-2" />
            Send to Client
          </Button>
        </div>
      </div>

      {/* KPI cards */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Total Orders (7 days)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">
              {totalOrders}
            </div>
            <p className="text-sm text-muted-foreground">
              For {companyInfo.name}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Success Rate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">
              {successRate}%
            </div>
            <p className="text-sm text-muted-foreground">
              Failed: {failedOrders} orders
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Total Cost
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">
              ${totalCost.toLocaleString()}
            </div>
            <p className="text-sm text-muted-foreground">
              Avg ${avgCostPerOrder} / order
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-muted-foreground">
              Avg Delivery Time (SLA)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl text-foreground">
              {companyInfo.avgSla}
            </div>
            <p className="text-sm text-muted-foreground">
              From warehouse to customer
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts row */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Orders over time */}
        <Card>
          <CardHeader>
            <CardTitle>Orders Timeline</CardTitle>
            <CardDescription>
              7-day order trend for {companyInfo.name}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={companyOrdersPerDayData}>
                  <CartesianGrid
                    strokeDasharray="3 3"
                    className="stroke-muted"
                  />
                  <XAxis dataKey="date" className="text-xs" />
                  <YAxis className="text-xs" />
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
                  <Legend />
                  <Line type="monotone" dataKey="orders" stroke="#3b82f6" strokeWidth={2} name="Total Orders" />
                  <Line type="monotone" dataKey="successful" stroke="#10b981" strokeWidth={2} name="Successful" />
                  <Line type="monotone" dataKey="failed" stroke="#ef4444" strokeWidth={2} name="Failed" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Status distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Delivery Status</CardTitle>
            <CardDescription>
              Current order status for this company
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={companyStatusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name}: ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={100}
                    dataKey="value"
                  >
                    {companyStatusData.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
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
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Cost per route + table */}
      <Card>
        <CardHeader>
          <CardTitle>Cost by Route</CardTitle>
          <CardDescription>
            Transportation cost per main route for this company
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[280px] mb-6">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={companyRouteCostData}>
                <CartesianGrid
                  strokeDasharray="3 3"
                  className="stroke-muted"
                />
                <XAxis dataKey="route" className="text-xs" />
                <YAxis className="text-xs" />
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
                <Legend />
                <Bar
                  dataKey="cost"
                  name="Cost ($)"
                  fill="#2563EB"
                  radius={[6, 6, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-2 px-2 text-muted-foreground">
                    Route
                  </th>
                  <th className="text-right py-2 px-2 text-muted-foreground">
                    Orders
                  </th>
                  <th className="text-right py-2 px-2 text-muted-foreground">
                    Total Cost
                  </th>
                  <th className="text-right py-2 px-2 text-muted-foreground">
                    Avg Cost / Order
                  </th>
                </tr>
              </thead>
              <tbody>
                {companyRouteCostData.map((r) => (
                  <tr
                    key={r.route}
                    className="border-b border-border hover:bg-muted/50"
                  >
                    <td className="py-2 px-2 text-foreground">{r.route}</td>
                    <td className="py-2 px-2 text-right text-foreground">
                      {r.orders}
                    </td>
                    <td className="py-2 px-2 text-right text-foreground">
                      ${r.cost.toLocaleString()}
                    </td>
                    <td className="py-2 px-2 text-right text-foreground">
                      ${Math.round(r.cost / r.orders)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* AI suggestions for this company */}
      <Card className="border-accent/50">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-accent/10 rounded-lg flex items-center justify-center">
              <Truck className="w-5 h-5 text-accent" />
            </div>
            <div>
              <CardTitle>AI Suggestions for {companyInfo.name}</CardTitle>
              <CardDescription>
                Tailored recommendations to improve SLA and reduce cost
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {companyAiSuggestions.map((s, idx) => (
              <Card
                key={idx}
                className="border-2 hover:border-primary transition-colors"
              >
                <CardContent className="pt-5">
                  <div className="flex items-start justify-between gap-4 mb-2">
                    <h4 className="text-foreground">{s.title}</h4>
                    <Badge
                      variant="secondary"
                      className={priorityColor[s.priority as keyof typeof priorityColor]}
                    >
                      {s.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-accent mb-1">{s.impact}</p>
                  <p className="text-sm text-muted-foreground mb-3">
                    {s.detail}
                  </p>
                  <div className="flex justify-end">
                    <Button size="sm" variant="outline">
                      Add to Action Plan
                    </Button>
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
