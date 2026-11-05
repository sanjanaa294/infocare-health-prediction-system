"""Server launcher script for the Health Prediction & Patient Management Application."""

import os
import uvicorn
from dotenv import load_dotenv

# Load environment configuration
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "True").lower() in ("true", "1", "yes")

    print("=" * 65)
    print("  HEALTH PREDICTION & PATIENT MANAGEMENT APPLICATION")
    print(f"  Starting local server at: http://{host}:{port}")
    print(f"  Interactive API Docs:     http://{host}:{port}/docs")
    print(f"  Web Dashboard:            http://{host}:{port}/dashboard")
    print("=" * 65)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info",
    )

