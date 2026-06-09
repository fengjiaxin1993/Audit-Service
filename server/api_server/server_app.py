import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, RedirectResponse

from server.utils import MakeFastAPIOffline
from settings import Settings
from server.api_server.main_routes import ocr_router
from server.api_server.audit_rule_routes import audit_rule_router
from server.api_server.audit_result_routes import audit_result_router
from server.api_server.contract_routes import contract_router
from server.api_server.task_routes import task_router
from server.common.task_queue import stop_task_workers


def create_app():
    app = FastAPI(title="OCR API Server")
    MakeFastAPIOffline(app)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("shutdown")
    def shutdown():
        """服务关闭时停止 TaskWorker 线程"""
        stop_task_workers()

    @app.get("/index",summary="文档展示页面", include_in_schema=False)
    async def root():
        """根路由 - 返回前端页面"""
        frontend_path = os.path.join(Settings.basic_settings.PACKAGE_ROOT, "frontend", "index.html")
        if os.path.exists(frontend_path):
            return FileResponse(frontend_path)
        return {"message": "PDF OCR API 服务运行中", "docs": "/docs"}

    @app.get("/rules",summary="规则库管理文档", include_in_schema=False)
    async def rules_page():
        """规则管理页面"""
        rules_path = os.path.join(Settings.basic_settings.PACKAGE_ROOT, "frontend", "rules.html")
        if os.path.exists(rules_path):
            return FileResponse(rules_path)
        return {"message": "规则管理页面不存在", "docs": "/rules"}

    @app.get("/docs", summary="swagger 文档", include_in_schema=False)
    async def document():
        return RedirectResponse(url="/docs")

    app.include_router(ocr_router)
    app.include_router(audit_rule_router)
    app.include_router(audit_result_router)
    app.include_router(contract_router)
    app.include_router(task_router)

    return app


def run_api(host, port):
    uvicorn.run(app, host=host, port=port)


app = create_app()