#!/usr/bin/env python
"""
Script to delete all data from the database.
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
from django.db import connection

def clear_all_data():
    """Delete all data from all tables"""
    print("=" * 60)
    print("WARNING: This will delete ALL data from the database!")
    print("=" * 60)
    
    # Get confirmation
    confirm = input("Type 'DELETE ALL' to confirm: ")
    if confirm != 'DELETE ALL':
        print("Operation cancelled.")
        return
    
    print("\nDeleting all data...")
    
    # Use Django's flush command
    call_command('flush', '--noinput', verbosity=2)
    
    print("\n" + "=" * 60)
    print("All data has been deleted!")
    print("=" * 60)
    print("\nNote: Table structures are preserved.")
    print("You may need to create a new superuser:")
    print("  python manage.py createsuperuser")

if __name__ == '__main__':
    clear_all_data()

