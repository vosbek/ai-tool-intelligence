#!/usr/bin/env python3
"""
Test script to verify full Strands application functionality
"""

import requests
import json
import time
import sys
from datetime import datetime

def test_backend_endpoints():
    """Test all major backend API endpoints"""
    base_url = "http://localhost:5000"
    
    print("🔍 Testing Backend API Endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False
    
    # Test tools endpoint
    try:
        response = requests.get(f"{base_url}/api/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ Tools endpoint working ({tools['total']} tools found)")
        else:
            print(f"❌ Tools endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Tools endpoint error: {e}")
        return False
    
    # Test categories endpoint
    try:
        response = requests.get(f"{base_url}/api/categories", timeout=5)
        if response.status_code == 200:
            categories = response.json()
            print(f"✅ Categories endpoint working ({len(categories)} categories found)")
        else:
            print(f"❌ Categories endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Categories endpoint error: {e}")
        return False
    
    # Test research endpoint (should return graceful error without strands packages)
    try:
        response = requests.post(f"{base_url}/api/tools/1/research", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if "error" in result.get("research_data", {}):
                print("✅ Research endpoint working (expected error without strands packages)")
            else:
                print("✅ Research endpoint working fully")
        else:
            print(f"❌ Research endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Research endpoint error: {e}")
        return False
    
    return True

def test_frontend_availability():
    """Test if frontend is accessible"""
    print("\n🌐 Testing Frontend Availability...")
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible on port 3000")
            return True
        else:
            print(f"❌ Frontend returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️  Frontend not accessible (may still be starting): {e}")
        return False

def test_cors_configuration():
    """Test CORS configuration between frontend and backend"""
    print("\n🔗 Testing CORS Configuration...")
    
    try:
        # Simulate a browser request from frontend to backend
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        
        response = requests.options("http://localhost:5000/api/health", headers=headers, timeout=5)
        
        if 'Access-Control-Allow-Origin' in response.headers:
            print("✅ CORS configured correctly")
            return True
        else:
            print("⚠️  CORS may not be configured properly")
            return False
    except Exception as e:
        print(f"❌ CORS test error: {e}")
        return False

def generate_test_report():
    """Generate comprehensive test report"""
    print("\n" + "="*60)
    print("🎯 STRANDS APPLICATION TEST REPORT")
    print("="*60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all tests
    backend_ok = test_backend_endpoints()
    frontend_ok = test_frontend_availability()
    cors_ok = test_cors_configuration()
    
    # Summary
    print("\n📋 TEST SUMMARY:")
    print("="*30)
    print(f"Backend API:     {'✅ PASS' if backend_ok else '❌ FAIL'}")
    print(f"Frontend Access: {'✅ PASS' if frontend_ok else '⚠️  WARN'}")
    print(f"CORS Config:     {'✅ PASS' if cors_ok else '⚠️  WARN'}")
    
    # Overall status
    if backend_ok and cors_ok:
        print(f"\n🎉 OVERALL STATUS: ✅ READY FOR USE")
        print("\n📖 Next Steps:")
        print("1. Install strands packages: pip install strands-agents strands-tools")
        print("2. Configure AWS credentials in backend/.env")
        print("3. Start using the application at http://localhost:3000")
        return True
    else:
        print(f"\n⚠️  OVERALL STATUS: NEEDS ATTENTION")
        if not backend_ok:
            print("- Backend API issues need to be resolved")
        if not cors_ok:
            print("- CORS configuration may need adjustment")
        return False

def main():
    """Main test function"""
    print("🚀 Starting Strands Application Functionality Test")
    print("=" * 60)
    
    success = generate_test_report()
    
    print("\n" + "="*60)
    
    if success:
        print("✅ Application is ready for legacy Struts analysis workflow!")
        sys.exit(0)
    else:
        print("❌ Application needs additional configuration")
        sys.exit(1)

if __name__ == "__main__":
    main()