import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Package, TrendingDown, MapPin, FileBarChart, CheckCircle, Clock, Users, Shield } from 'lucide-react';
import { ImageWithFallback } from '../../components/figma/ImageWithFallback';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="sticky top-0 z-50 bg-card/95 backdrop-blur border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <Package className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-foreground">AI Transport Hub</span>
            </div>
            <div className="flex items-center gap-3">
              <Link to="/tracking">
                <Button variant="ghost">Track Order</Button>
              </Link>
              <Link to="/login">
                <Button variant="ghost">Login</Button>
              </Link>
              <Link to="/register">
                <Button>Register Business</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-b from-primary/5 to-background py-20 sm:py-32">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6">
              <div className="inline-block px-3 py-1 bg-accent/10 text-accent rounded-full border border-accent/20">
                AI-Powered Logistics
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl text-foreground">
                AI-Powered Transportation Hub for SMEs
              </h1>
              <p className="text-lg text-muted-foreground">
                Optimize delivery routes, reduce costs, and improve transparency with our intelligent transportation management system.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/register">
                  <Button size="lg" className="w-full sm:w-auto">
                    Register Business
                  </Button>
                </Link>
                <Link to="/dashboard/overview">
                </Link>
              </div>
              <div className="flex items-center gap-8 pt-4">
                <div>
                  <div className="text-2xl text-foreground">500+</div>
                  <div className="text-sm text-muted-foreground">Companies</div>
                </div>
                <div>
                  <div className="text-2xl text-foreground">50K+</div>
                  <div className="text-sm text-muted-foreground">Deliveries</div>
                </div>
                <div>
                  <div className="text-2xl text-foreground">98%</div>
                  <div className="text-sm text-muted-foreground">Success Rate</div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-[4/3] rounded-2xl overflow-hidden shadow-2xl">
                <ImageWithFallback 
                  src="https://images.unsplash.com/photo-1758707845038-1f28b342b487?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxkZWxpdmVyeSUyMHRydWNrJTIwbG9naXN0aWNzfGVufDF8fHx8MTc2MDM2NDczOHww&ixlib=rb-4.1.0&q=80&w=1080"
                  alt="Transportation logistics"
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-card/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl text-foreground mb-4">How It Works</h2>
            <p className="text-lg text-muted-foreground">Simple process to manage your deliveries</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { step: '01', title: 'Create Order', desc: 'Input delivery details and requirements', icon: Package },
              { step: '02', title: 'Assign Route', desc: 'AI optimizes routes automatically', icon: MapPin },
              { step: '03', title: 'Deliver', desc: 'Shippers execute delivery efficiently', icon: Users },
              { step: '04', title: 'Track', desc: 'Real-time tracking and updates', icon: CheckCircle },
            ].map((item) => (
              <Card key={item.step} className="relative overflow-hidden border-2 hover:border-primary transition-colors">
                <CardHeader>
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                    <item.icon className="w-6 h-6 text-primary" />
                  </div>
                  <div className="absolute top-4 right-4 text-4xl text-primary/10">{item.step}</div>
                  <CardTitle>{item.title}</CardTitle>
                  <CardDescription>{item.desc}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl text-foreground mb-4">Why Choose Us</h2>
            <p className="text-lg text-muted-foreground">Built for SMEs who need efficiency and reliability</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { 
                title: 'Lower Costs', 
                desc: 'Reduce transportation costs by up to 30% with AI route optimization',
                icon: TrendingDown,
                color: 'bg-blue-500'
              },
              { 
                title: 'Smart Routing', 
                desc: 'AI-powered algorithms find the most efficient delivery routes',
                icon: MapPin,
                color: 'bg-green-500'
              },
              { 
                title: 'Real-time Tracking', 
                desc: 'Monitor all deliveries in real-time with live updates',
                icon: Clock,
                color: 'bg-amber-500'
              },
              { 
                title: 'Transparent Reports', 
                desc: 'Detailed analytics and insights for better decision making',
                icon: FileBarChart,
                color: 'bg-purple-500'
              },
            ].map((item) => (
              <Card key={item.title} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className={`w-12 h-12 ${item.color} rounded-lg flex items-center justify-center mb-4`}>
                    <item.icon className="w-6 h-6 text-white" />
                  </div>
                  <CardTitle>{item.title}</CardTitle>
                  <CardDescription>{item.desc}</CardDescription>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-card/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl text-foreground mb-4">Trusted by SMEs</h2>
            <p className="text-lg text-muted-foreground">See what our customers say</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { name: 'Sarah Chen', role: 'CEO, FastDelivery Co.', text: 'Cut our logistics costs by 35% in the first quarter. The AI routing is incredibly accurate.' },
              { name: 'Michael Torres', role: 'Operations Manager, QuickShip', text: 'Real-time tracking has improved our customer satisfaction scores dramatically.' },
              { name: 'Emily Johnson', role: 'Founder, LocalGoods', text: 'Best investment we made. The system pays for itself within months.' },
            ].map((item, i) => (
              <Card key={i}>
                <CardHeader>
                  <div className="flex items-center gap-1 text-amber-500 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <svg key={i} className="w-4 h-4 fill-current" viewBox="0 0 20 20">
                        <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                      </svg>
                    ))}
                  </div>
                  <CardDescription className="mb-4">{item.text}</CardDescription>
                  <div>
                    <div className="text-foreground">{item.name}</div>
                    <div className="text-sm text-muted-foreground">{item.role}</div>
                  </div>
                </CardHeader>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl sm:text-4xl mb-4">Ready to Optimize Your Transportation?</h2>
          <p className="text-lg mb-8 opacity-90">Join hundreds of SMEs already saving costs and improving efficiency</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/register">
              <Button size="lg" variant="secondary" className="w-full sm:w-auto">
                Register Your Business
              </Button>
            </Link>
            <Link to="/dashboard/overview">
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-card border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                  <Package className="w-5 h-5 text-primary-foreground" />
                </div>
                <span className="text-foreground">AI Transport Hub</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Optimizing logistics for SMEs with AI-powered solutions.
              </p>
            </div>
            <div>
              <h4 className="mb-4 text-foreground">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="/" className="hover:text-primary">Features</Link></li>
                <li><Link to="/" className="hover:text-primary">Pricing</Link></li>
                <li><Link to="/tracking" className="hover:text-primary">Tracking</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="mb-4 text-foreground">Company</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="/" className="hover:text-primary">About</Link></li>
                <li><Link to="/" className="hover:text-primary">Careers</Link></li>
                <li><Link to="/" className="hover:text-primary">Contact</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="mb-4 text-foreground">Support</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="/" className="hover:text-primary">Help Center</Link></li>
                <li><Link to="/" className="hover:text-primary">Documentation</Link></li>
                <li><Link to="/" className="hover:text-primary">API</Link></li>
              </ul>
            </div>
          </div>
          <div className="mt-12 pt-8 border-t border-border text-center text-sm text-muted-foreground">
            <p>© 2025 AI Transport Hub. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
