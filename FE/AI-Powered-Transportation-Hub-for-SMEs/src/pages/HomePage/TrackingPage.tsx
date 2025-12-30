import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Package, Search, MapPin, CheckCircle, Clock, Truck, XCircle } from 'lucide-react';

const mockOrderData = {
  'ORD-2451': {
    code: 'ORD-2451',
    from: 'Warehouse A, District 1',
    to: '123 Main St, District 5',
    status: 'delivered',
    shipper: 'John Doe',
    shipperPhone: '+1 (555) 123-4567',
    estimatedTime: 'Oct 13, 2:30 PM',
    timeline: [
      { status: 'Created', time: 'Oct 13, 9:20 AM', completed: true },
      { status: 'Picked Up', time: 'Oct 13, 10:15 AM', completed: true },
      { status: 'In Transit', time: 'Oct 13, 11:30 AM', completed: true },
      { status: 'Out for Delivery', time: 'Oct 13, 1:45 PM', completed: true },
      { status: 'Delivered', time: 'Oct 13, 2:30 PM', completed: true },
    ],
  },
  'ORD-2452': {
    code: 'ORD-2452',
    from: 'Warehouse B, District 3',
    to: '456 Oak Ave, District 7',
    status: 'in-transit',
    shipper: 'Jane Smith',
    shipperPhone: '+1 (555) 234-5678',
    estimatedTime: 'Oct 13, 4:00 PM',
    timeline: [
      { status: 'Created', time: 'Oct 13, 11:00 AM', completed: true },
      { status: 'Picked Up', time: 'Oct 13, 12:15 PM', completed: true },
      { status: 'In Transit', time: 'Oct 13, 1:30 PM', completed: true },
      { status: 'Out for Delivery', time: 'Estimated 3:30 PM', completed: false },
      { status: 'Delivered', time: 'Estimated 4:00 PM', completed: false },
    ],
  },
};

export function TrackingPage() {
  const [trackingCode, setTrackingCode] = useState('');
  const [orderData, setOrderData] = useState<typeof mockOrderData['ORD-2451'] | null>(null);
  const [searched, setSearched] = useState(false);

  const handleTrack = () => {
    setSearched(true);
    const data = mockOrderData[trackingCode.toUpperCase() as keyof typeof mockOrderData];
    setOrderData(data || null);
  };

  const statusConfig = {
    delivered: { icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-100 dark:bg-green-950' },
    'in-transit': { icon: Truck, color: 'text-blue-600', bgColor: 'bg-blue-100 dark:bg-blue-950' },
    pickup: { icon: Clock, color: 'text-amber-600', bgColor: 'bg-amber-100 dark:bg-amber-950' },
    failed: { icon: XCircle, color: 'text-red-600', bgColor: 'bg-red-100 dark:bg-red-950' },
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-primary/5 to-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-card/95 backdrop-blur border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Package className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-foreground">AI Transport Hub</span>
            </Link>
            <div className="flex items-center gap-3">
              <Link to="/">
                <Button variant="ghost">Home</Button>
              </Link>
              <Link to="/login">
                <Button>Login</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-20">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl sm:text-5xl text-foreground mb-4">Track Your Order</h1>
          <p className="text-lg text-muted-foreground">
            Enter your tracking code to get real-time updates on your delivery
          </p>
        </div>

        {/* Search Box */}
        <Card className="mb-8">
          <CardContent className="pt-6">
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input 
                  placeholder="Enter tracking code (e.g., ORD-2451)" 
                  className="pl-10 h-12"
                  value={trackingCode}
                  onChange={(e) => setTrackingCode(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleTrack()}
                />
              </div>
              <Button size="lg" onClick={handleTrack}>
                Track Order
              </Button>
            </div>
            <p className="text-sm text-muted-foreground mt-3">
              Try: ORD-2451 (delivered) or ORD-2452 (in transit)
            </p>
          </CardContent>
        </Card>

        {/* Results */}
        {searched && !orderData && (
          <Card className="border-2 border-dashed">
            <CardContent className="py-12">
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto">
                  <Package className="w-8 h-8 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="text-foreground mb-2">Order Not Found</h3>
                  <p className="text-muted-foreground">
                    We couldn't find an order with tracking code "{trackingCode}".
                    Please check the code and try again.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {orderData && (
          <div className="space-y-6">
            {/* Order Status Card */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Order {orderData.code}</CardTitle>
                    <CardDescription>Track your delivery status</CardDescription>
                  </div>
                  {orderData.status && (
                    <div className={`w-12 h-12 ${statusConfig[orderData.status as keyof typeof statusConfig].bgColor} rounded-full flex items-center justify-center`}>
                      {(() => {
                        const StatusIcon = statusConfig[orderData.status as keyof typeof statusConfig].icon;
                        return <StatusIcon className={`w-6 h-6 ${statusConfig[orderData.status as keyof typeof statusConfig].color}`} />;
                      })()}
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Status Banner */}
                <div className={`p-4 ${statusConfig[orderData.status as keyof typeof statusConfig].bgColor} rounded-lg`}>
                  <div className="flex items-center gap-3">
                    {(() => {
                      const StatusIcon = statusConfig[orderData.status as keyof typeof statusConfig].icon;
                      return <StatusIcon className={`w-6 h-6 ${statusConfig[orderData.status as keyof typeof statusConfig].color}`} />;
                    })()}
                    <div>
                      <div className={`${statusConfig[orderData.status as keyof typeof statusConfig].color}`}>
                        {orderData.status === 'delivered' ? 'Delivered Successfully!' : 
                         orderData.status === 'in-transit' ? 'Your Order is On The Way' :
                         orderData.status === 'pickup' ? 'Order Picked Up' :
                         'Delivery Failed'}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {orderData.status === 'delivered' 
                          ? `Delivered on ${orderData.estimatedTime}`
                          : `Estimated delivery: ${orderData.estimatedTime}`
                        }
                      </div>
                    </div>
                  </div>
                </div>

                {/* Order Info */}
                <div className="grid sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-muted-foreground text-sm">
                      <MapPin className="w-4 h-4" />
                      <span>From</span>
                    </div>
                    <div className="text-foreground pl-6">{orderData.from}</div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-muted-foreground text-sm">
                      <MapPin className="w-4 h-4" />
                      <span>To</span>
                    </div>
                    <div className="text-foreground pl-6">{orderData.to}</div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-muted-foreground text-sm">Shipper</div>
                    <div className="text-foreground">{orderData.shipper}</div>
                  </div>
                  <div className="space-y-2">
                    <div className="text-muted-foreground text-sm">Contact</div>
                    <div className="text-foreground">{orderData.shipperPhone}</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Timeline */}
            <Card>
              <CardHeader>
                <CardTitle>Delivery Timeline</CardTitle>
                <CardDescription>Real-time tracking updates</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {orderData.timeline.map((step, i) => (
                    <div key={i} className="flex gap-4">
                      <div className="flex flex-col items-center">
                        <div className={`w-4 h-4 rounded-full border-2 ${
                          step.completed 
                            ? 'bg-primary border-primary' 
                            : 'bg-background border-border'
                        }`} />
                        {i < orderData.timeline.length - 1 && (
                          <div className={`w-0.5 h-12 ${
                            step.completed ? 'bg-primary' : 'bg-border'
                          }`} />
                        )}
                      </div>
                      <div className="flex-1 pb-4">
                        <div className={`${
                          step.completed ? 'text-foreground' : 'text-muted-foreground'
                        }`}>
                          {step.status}
                        </div>
                        <div className="text-sm text-muted-foreground">{step.time}</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-3">
              <Button variant="outline" className="flex-1" onClick={() => window.print()}>
                Print Receipt
              </Button>
              <Button variant="outline" className="flex-1">
                Contact Support
              </Button>
              <Button className="flex-1" onClick={() => { setOrderData(null); setSearched(false); setTrackingCode(''); }}>
                Track Another Order
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center text-sm text-muted-foreground">
            <p>© 2025 AI Transport Hub. All rights reserved.</p>
            <div className="mt-2 space-x-4">
              <Link to="/" className="hover:text-primary">Help Center</Link>
              <span>·</span>
              <Link to="/" className="hover:text-primary">Contact Us</Link>
              <span>·</span>
              <Link to="/" className="hover:text-primary">Terms of Service</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
