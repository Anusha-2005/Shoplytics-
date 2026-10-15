"""
Shoplytics API Server Launcher
Starts the Uvicorn ASGI server hosting the Shoplytics FastAPI application.
"""

import os
import argparse
import uvicorn

def main():
    parser = argparse.ArgumentParser(description="Shoplytics Analytics REST API Server")
    parser.add_argument("--host", default=os.getenv("API_HOST", "127.0.0.1"), help="Host address to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=int(os.getenv("API_PORT", 8000)), help="Port to bind (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload on code changes")
    args = parser.parse_args()

    print("=" * 70)
    print("STARTING SHOPLYTICS REST API SERVER")
    print(f"URL: http://{args.host}:{args.port}")
    print(f"Interactive Swagger Documentation: http://{args.host}:{args.port}/docs")
    print(f"ReDoc Documentation: http://{args.host}:{args.port}/redoc")
    print("=" * 70)

    uvicorn.run(
        "src.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()
