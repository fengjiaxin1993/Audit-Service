import argparse
import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

from server.api_server.main_routes import ocr_router
from server.configs.basic_config import BASE_DIR


def create_app():
    app = FastAPI(title="OCR API Server")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    async def root():
        """根路由 - 返回前端页面"""
        frontend_path = os.path.join(BASE_DIR, "frontend", "index.html")
        if os.path.exists(frontend_path):
            return FileResponse(frontend_path)
        return {"message": "PDF OCR API 服务运行中", "docs": "/docs"}

    app.include_router(ocr_router)

    return app


def run_api(host, port):
    uvicorn.run(app, host=host, port=port)


app = create_app()
