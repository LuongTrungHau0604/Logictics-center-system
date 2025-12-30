import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { LandingPage } from "./pages/HomePage/LandingPage";
import { LoginPage } from "./pages/Auth/LoginPage";
import { RegisterPage } from "./pages/Auth/RegisterPage";
import { OverviewPage } from "./pages/CompanyManagement/OverviewPage";
import { OrdersPage } from "./pages/Order/OrdersPage";
import { WarehousesPage } from "./pages/Warehouse/WarehousesPage";
import { DispatchPage } from "./pages/Dashboard/DispatchPage";
import { ShippersPage } from "./pages/CompanyManagement/ShippersPage";
import { ReportsPage } from "./pages/Report/ReportsPage";
import { ReportsCompanyPage } from "./pages/Report/ReportsCompanyPage";
import { AdminPanelPage } from "./pages/Dashboard/AdminPanelPage";
import { CompanyProfilePage } from "./pages/CompanyManagement/CompanyProfilePage";
import { TrackingPage } from "./pages/Customer/TrackingPage";
import { DashboardLayout } from "./components/Layout/DashboardLayout";
import { Toaster } from "./components/ui/sonner";
import WarehouseInventoryPage from "./pages/Warehouse/WarehousesInventoryPage";
import { AreasPage } from "./pages/Dashboard/AreaPage";
import {WarehouseStaffPage} from "./pages/WarehouseManager/WareHouseManagerPage";
import { DispatchManagementPage } from './pages/Dashboard/DispatchManagementPage';




export default function App() {
  return (
    <BrowserRouter>
      <Toaster />
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/tracking" element={<TrackingPage />} />

        {/* Dashboard routes */}
        <Route path="/dashboard" element={<DashboardLayout />}>
          <Route
            index
            element={<Navigate to="/dashboard/overview" replace />}
          />
          <Route path="overview" element={<OverviewPage />} />
          <Route path="orders" element={<OrdersPage />} />
          <Route path="warehouses" element={<WarehousesPage />} />
          <Route path="areas" element={<AreasPage />} />
          {/* 🔹 inventory route relative */}
          <Route
            path="warehouses/:id/inventory"
            element={<WarehouseInventoryPage />}
          />
          <Route path="dispatch" element={<DispatchPage />} />
          <Route path="shippers" element={<ShippersPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="profile" element={<CompanyProfilePage />} />
          <Route path="admin" element={<AdminPanelPage />} />
          <Route path="/dashboard/reports/company" element={<ReportsCompanyPage />} />
          <Route path="warehousestaff" element={<WarehouseStaffPage />} />
          <Route path="dispatch-management" element={<DispatchManagementPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
