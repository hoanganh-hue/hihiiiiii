#!/usr/bin/env python3
"""
Enhanced BHXH Tool - Launcher Script
Simple launcher for the Enhanced BHXH Tool
"""

import sys
import os
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Main launcher function"""
    print("🚀 Enhanced BHXH Tool v2.0.0 - Python Version")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = current_dir / '.env'
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please copy .env.template to .env and configure your settings.")
        print("Run: cp .env.template .env")
        return 1
    
    # Check if input file exists
    input_file = current_dir / 'data-input.xlsx'
    if not input_file.exists():
        print("❌ data-input.xlsx file not found!")
        print("Please ensure the input Excel file is present.")
        return 1
    
    # Import and run main
    try:
        from main import main as main_func
        return main_func()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())