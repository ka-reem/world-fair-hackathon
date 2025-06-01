#!/usr/bin/env python3
"""
Startup script for Meta Agent FastAPI Server
Simple way to start the web API with proper configuration
"""

import uvicorn
import os
from fastapi_server import app

if __name__ == "__main__":
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print("🚀 Starting Meta Agent FastAPI Server...")
    print(f"🌐 Server: http://{host}:{port}")
    print(f"📊 Dashboard: http://{host}:{port}/workflow/dashboard")
    print(f"📚 API Docs: http://{host}:{port}/docs")
    print(f"🔄 Reload: {reload}")
    print("-" * 50)
    
    # Start server
    uvicorn.run(
        "fastapi_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    ) 