#!/usr/bin/env python
"""
Script to delete all data from the database (non-interactive).
WARNING: This is destructive and cannot be undone!
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcampus.settings')
django.setup()

from django.core.management import call_command
from django.db import connection, transaction

def clear_all_data():
    """Delete all data from all tables"""
    print("=" * 60)
    print("DELETING ALL DATA FROM DATABASE...")
    print("=" * 60)
    
    try:
        # Use Django's flush command (non-interactive)
        call_command('flush', '--noinput', verbosity=2)
        
        print("\n" + "=" * 60)
        print("SUCCESS: All data has been deleted!")
        print("=" * 60)
        print("\nNote: Table structures are preserved.")
        print("You may need to create a new superuser:")
        print("  python manage.py createsuperuser")
        
    except Exception as e:
        print(f"\nERROR: Failed to delete data: {e}")
        sys.exit(1)

if __name__ == '__main__':
    clear_all_data()

