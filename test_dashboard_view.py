#!/usr/bin/env python
"""
Script to test the dashboard view directly and see what error occurs.
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetmanagement.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from core.views import dashboard
import traceback

User = get_user_model()

def test_dashboard():
    """Test the dashboard view"""
    try:
        # Create a mock request
        factory = RequestFactory()
        request = factory.get('/fleet/')
        
        # Get a user (or create a test user)
        try:
            user = User.objects.first()
            if not user:
                print("No users found. Creating test user...")
                user = User.objects.create_user(
                    username='testuser',
                    email='test@test.com',
                    password='testpass123'
                )
        except Exception as e:
            print(f"Error getting/creating user: {e}")
            return
        
        # Set the user on the request (simulate login)
        request.user = user
        
        print("Testing dashboard view...")
        response = dashboard(request)
        
        if response.status_code == 200:
            print("✓ Dashboard view executed successfully!")
            print(f"Response status: {response.status_code}")
        else:
            print(f"✗ Dashboard view returned status: {response.status_code}")
            print(f"Response content: {response.content[:500]}")
            
    except Exception as e:
        print(f"✗ Error testing dashboard view:")
        print(f"Error: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()

if __name__ == '__main__':
    test_dashboard()

