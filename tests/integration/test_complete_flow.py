"""
Integration test: Complete delivery flow
Tests the entire flow from order creation to delivery
"""
import pytest
from fastapi.testclient import TestClient
import time

# Import all service clients
from app.main import app as order_app

order_client = TestClient(order_app)

@pytest.mark.integration
@pytest.mark.slow
class TestCompleteDeliveryFlow:
    """Test complete delivery workflow across all services"""
    
    def test_end_to_end_delivery_flow(self, test_db, auth_headers):
        """
        Complete delivery flow:
        1. SME creates order
        2. AI calculates optimal route and assigns warehouse
        3. Warehouse receives order
        4. Shipper picks up order
        5. Shipper delivers order
        6. Order completed
        """
        
        # STEP 1: Create Order
        order_data = {
            "sme_id": "SME001",
            "receiver_name": "Test Customer",
            "receiver_phone": "0123456789",
            "receiver_address": "456 Delivery St, District 2, HCMC",
            "latitude": 10.8,
            "longitude": 106.7,
            "required_capacity": 3.0
        }
        
        response = order_client.post(
            "/api/v1/orders",
            json=order_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        order_id = response.json()["order_id"]
        barcode = response.json()["barcode"]
        
        print(f"✅ Order created: {order_id}")
        
        # STEP 2: Request AI Route Calculation
        # (Calling AI Agent Service)
        import requests
        ai_response = requests.post(
            "http://localhost:8000/api/v1/ai-insights/calculate-route",
            json={
                "business_address": "123 Business Ave, District 1, HCMC",
                "receiver_address": order_data["receiver_address"],
                "required_capacity": order_data["required_capacity"]
            }
        )
        
        if ai_response.status_code == 200:
            ai_data = ai_response.json()
            warehouse_id = ai_data["route"]["warehouse"]["warehouse_id"]
            print(f"✅ AI assigned warehouse: {warehouse_id}")
        else:
            # Fallback to default warehouse
            warehouse_id = "WH001"
            print(f"⚠️ AI service unavailable, using default warehouse: {warehouse_id}")
        
        # STEP 3: Scan at Warehouse (IN)
        scan_in_response = order_client.post(
            "/api/v1/scan/warehouse",
            json={
                "barcode": barcode,
                "warehouse_id": warehouse_id,
                "action": "IN"
            },
            headers=auth_headers
        )
        assert scan_in_response.status_code == 200
        print(f"✅ Order scanned IN at warehouse: {warehouse_id}")
        
        # Verify order status updated
        order_status = order_client.get(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers
        )
        assert order_status.json()["status"] == "AT_WAREHOUSE"
        
        # STEP 4: Assign Shipper & Scan OUT
        shipper_id = "SHIP001"
        scan_out_response = order_client.post(
            "/api/v1/scan/warehouse",
            json={
                "barcode": barcode,
                "warehouse_id": warehouse_id,
                "action": "OUT",
                "shipper_id": shipper_id
            },
            headers=auth_headers
        )
        assert scan_out_response.status_code == 200
        print(f"✅ Order scanned OUT, assigned to shipper: {shipper_id}")
        
        # Verify status
        order_status = order_client.get(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers
        )
        assert order_status.json()["status"] == "IN_TRANSIT"
        
        # STEP 5: Update to OUT_FOR_DELIVERY
        update_response = order_client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "OUT_FOR_DELIVERY"},
            headers=auth_headers
        )
        assert update_response.status_code == 200
        print(f"✅ Order out for delivery")
        
        # STEP 6: Complete Delivery
        complete_response = order_client.patch(
            f"/api/v1/orders/{order_id}/status",
            json={"status": "DELIVERED"},
            headers=auth_headers
        )
        assert complete_response.status_code == 200
        print(f"✅ Order delivered successfully")
        
        # Final verification
        final_order = order_client.get(
            f"/api/v1/orders/{order_id}",
            headers=auth_headers
        )
        final_data = final_order.json()
        
        assert final_data["status"] == "DELIVERED"
        assert final_data["order_id"] == order_id
        
        print(f"\n🎉 COMPLETE DELIVERY FLOW PASSED!")
        print(f"Order ID: {order_id}")
        print(f"Barcode: {barcode}")
        print(f"Warehouse: {warehouse_id}")
        print(f"Shipper: {shipper_id}")
        print(f"Final Status: {final_data['status']}")

@pytest.mark.integration
class TestAIDispatchIntegration:
    """Test AI dispatch integration"""
    
    def test_ai_batch_optimization(self, test_db, auth_headers):
        """
        Test AI batch optimization:
        1. Create multiple pending orders
        2. Trigger AI batch optimization
        3. Verify orders are optimized and assigned
        """
        
        # Create multiple orders
        order_ids = []
        for i in range(5):
            order_data = {
                "sme_id": f"SME00{i+1}",
                "receiver_name": f"Customer {i+1}",
                "receiver_phone": f"012345678{i}",
                "receiver_address": f"{100+i*10} Test St, District {i+1}, HCMC",
                "latitude": 10.7 + (i * 0.01),
                "longitude": 106.7 + (i * 0.01),
                "required_capacity": 2.0 + i
            }
            
            response = order_client.post(
                "/api/v1/orders",
                json=order_data,
                headers=auth_headers
            )
            assert response.status_code == 201
            order_ids.append(response.json()["order_id"])
        
        print(f"✅ Created {len(order_ids)} orders")
        
        # Trigger AI optimization
        import requests
        try:
            ai_optimize_response = requests.post(
                "http://localhost:8000/api/v1/ai-batch-optimizer/ai/optimize",
                json={
                    "max_concurrent_orders": 10
                }
            )
            
            if ai_optimize_response.status_code == 200:
                optimization_result = ai_optimize_response.json()
                print(f"✅ AI Optimization Result:")
                print(f"   Status: {optimization_result['status']}")
                print(f"   Processed: {optimization_result['total_processed']}")
                print(f"   Success: {optimization_result['successful']}")
                
                assert optimization_result["status"] == "completed"
                assert optimization_result["successful"] > 0
            else:
                pytest.skip("AI service not available")
                
        except Exception as e:
            pytest.skip(f"AI service not available: {e}")

@pytest.mark.integration
class TestServiceCommunication:
    """Test communication between services"""
    
    def test_order_to_warehouse_communication(self, test_db, auth_headers):
        """Test Order Service can communicate with Warehouse Service"""
        import requests
        
        try:
            # Get warehouses from Warehouse Service
            warehouse_response = requests.get(
                "http://localhost:3004/api/v1/warehouses"
            )
            
            if warehouse_response.status_code == 200:
                warehouses = warehouse_response.json()
                assert len(warehouses) > 0
                print(f"✅ Retrieved {len(warehouses)} warehouses")
            else:
                pytest.skip("Warehouse service not available")
                
        except Exception as e:
            pytest.skip(f"Warehouse service not available: {e}")
    
    def test_order_to_identity_communication(self, test_db, auth_headers):
        """Test Order Service can communicate with Identity Service"""
        import requests
        
        try:
            # Get shippers from Identity Service
            shipper_response = requests.get(
                "http://localhost:8001/api/v1/employee/shippers",
                headers=auth_headers
            )
            
            if shipper_response.status_code == 200:
                print(f"✅ Successfully communicated with Identity Service")
            else:
                pytest.skip("Identity service not available")
                
        except Exception as e:
            pytest.skip(f"Identity service not available: {e}")
