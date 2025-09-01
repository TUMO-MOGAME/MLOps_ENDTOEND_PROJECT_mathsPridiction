#!/usr/bin/env python3
"""
Startup script for ML Pipeline Monitoring
This script starts the monitoring stack and metrics server
"""

import subprocess
import sys
import time
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🚀 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Success")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Failed")
        print(f"Error: {e.stderr}")
        return False

def check_docker():
    """Check if Docker is running"""
    return run_command("docker --version", "Checking Docker")

def start_monitoring_stack():
    """Start the Docker monitoring stack"""
    return run_command("docker-compose up -d", "Starting monitoring stack (Prometheus, Grafana, AlertManager)")

def start_metrics_server():
    """Start the ML metrics server"""
    print("🚀 Starting ML Metrics Server...")
    try:
        # Install Flask if not available
        subprocess.run([sys.executable, "-m", "pip", "install", "flask"], 
                      check=False, capture_output=True)
        
        # Start the metrics server
        subprocess.run([sys.executable, "ml_metrics_server.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Metrics server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start metrics server: {e}")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🔍 ML Pipeline Monitoring System Startup")
    print("=" * 60)
    
    # Change to monitoring directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Check prerequisites
    if not check_docker():
        print("❌ Docker is not available. Please install Docker first.")
        print("💡 You can still run the metrics server without Docker:")
        print("   python ml_metrics_server.py")
        
        # Ask if user wants to continue with just metrics server
        response = input("\n🤔 Continue with just the metrics server? (y/n): ")
        if response.lower() != 'y':
            sys.exit(1)
        
        print("\n🚀 Starting only the ML Metrics Server...")
        try:
            start_metrics_server()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
        return
    
    # Start monitoring stack
    if not start_monitoring_stack():
        print("❌ Failed to start monitoring stack")
        print("💡 You can still run the metrics server:")
        print("   python ml_metrics_server.py")
        sys.exit(1)
    
    # Wait for services to start
    print("⏳ Waiting for services to start...")
    time.sleep(10)
    
    # Show service status
    print("\n📊 Service Status:")
    subprocess.run("docker-compose ps", shell=True)
    
    # Show access URLs
    print("\n🌐 Access URLs:")
    print("  📈 Grafana Dashboard: http://localhost:3000 (admin/admin123)")
    print("  🔍 Prometheus: http://localhost:9090")
    print("  🚨 AlertManager: http://localhost:9093")
    print("  📊 ML Metrics: http://localhost:8001/metrics")
    print("  🎯 ML Dashboard: http://localhost:8001/dashboard")
    print("  📋 Simple Status: http://localhost:8001/status")
    print("  ❤️  Health Check: http://localhost:8001/health")
    
    # Start metrics server
    print("\n🚀 Starting ML Metrics Server...")
    print("📝 Metrics server will run in the foreground.")
    print("📝 Press Ctrl+C to stop the metrics server.")
    print("📝 The monitoring stack will continue running in the background.")
    
    try:
        start_metrics_server()
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down...")
        print("📝 Monitoring stack is still running. Use 'docker-compose down' to stop it.")

if __name__ == "__main__":
    main()
