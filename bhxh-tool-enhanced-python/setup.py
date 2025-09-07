#!/usr/bin/env python3
"""
Setup script for Enhanced BHXH Tool
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True


def install_dependencies():
    """Install required dependencies"""
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        return False
    return True


def create_directories():
    """Create necessary directories"""
    directories = ['logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    return True


def setup_environment():
    """Setup environment file"""
    env_file = Path('.env')
    env_template = Path('.env.template')
    
    if not env_file.exists() and env_template.exists():
        print("📝 Creating .env file from template...")
        with open(env_template, 'r') as template:
            content = template.read()
        with open(env_file, 'w') as env:
            env.write(content)
        print("✅ Created .env file from template")
        print("⚠️  Please edit .env file and add your 2captcha API key")
    elif env_file.exists():
        print("✅ .env file already exists")
    else:
        print("⚠️  No .env.template found, please create .env file manually")
    
    return True


def verify_files():
    """Verify required files exist"""
    required_files = [
        'tinh-thanh.json',
        'data-input.xlsx'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Missing required files: {', '.join(missing_files)}")
        print("Please ensure these files are present before running the tool")
        return False
    
    print("✅ All required files are present")
    return True


def main():
    """Main setup function"""
    print("🚀 Enhanced BHXH Tool - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    # Verify files
    verify_files()
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file and add your 2captcha API key")
    print("2. Ensure data-input.xlsx file is present")
    print("3. Run: python main.py --test (to test configuration)")
    print("4. Run: python main.py (to start processing)")


if __name__ == '__main__':
    main()