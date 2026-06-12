import os
import atexit

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse, RedirectResponse

from audit_service.server.ocr.ocr_service import startup_event
from audit_service.server.utils import MakeFastAPIOffline
from audit_service.settings import Settings
from audit_service.server.api_server.main_routes import ocr_router
from audit_service.server.api_server.audit_rule_routes import audit_rule_router
from audit_service.server.api_server.audit_result_routes import audit_result_router
from audit_service.server.api_server.contract_routes import contract_router
from audit_service.server.api_server.task_routes import task_router
from audit_service.server.common.task_queue import stop_task_workers, start_task_workers
from audit_service.server.logger_utils import build_logger

logger = build_logger()


def _force_cleanup():
    """注册 atexit 钩子，确保退出时释放资源，避免卡住"""
    try:
        stop_task_workers()
    except Exception:
        pass
    # 尝试释放 RapidDoc 全局引擎实例
    try:
        from server.ocr.single_ocr_engine import _rapid_doc_engine
        if _rapid_doc_engine is not None:
            del _rapid_doc_engine
    except Exception:
        pass


# 注册退出钩子，确保 Ctrl+C 时不会被 ONNX Runtime 线程阻塞
atexit.register(_force_cleanup)


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
        logger.info("服务正在关闭...")
        stop_task_workers()
        logger.info("服务关闭完成")

    @app.on_event("startup")
    def on_startup():
        """服务启动时执行初始化"""
        start_task_workers()
        startup_event()

    @app.get("/index",summary="文档展示页面", include_in_schema=False)
    async def root():
        """根路由 - 返回前端页面"""
        frontend_path = os.path.join(Settings.basic_settings.DATA_PATH, "frontend", "index.html")
        if os.path.exists(frontend_path):
            return FileResponse(frontend_path)
        return {"message": "PDF OCR API 服务运行中", "docs": "/docs"}

    @app.get("/rules",summary="规则库管理文档", include_in_schema=False)
    async def rules_page():
        """规则管理页面"""
        rules_path = os.path.join(Settings.basic_settings.DATA_PATH, "frontend", "rules.html")
        if os.path.exists(rules_path):
            return FileResponse(rules_path)
        return {"message": "规则管理页面不存在", "docs": "/rules"}

    @app.get("/contracts",summary="合同与任务管理", include_in_schema=False)
    async def contracts_page():
        """合同与任务管理页面"""
        contracts_path = os.path.join(Settings.basic_settings.DATA_PATH, "frontend", "contracts.html")
        if os.path.exists(contracts_path):
            return FileResponse(contracts_path)
        return {"message": "合同管理页面不存在", "docs": "/contracts"}

    @app.get("/results",summary="审计结果查看", include_in_schema=False)
    async def results_page():
        """审计结果查看页面"""
        results_path = os.path.join(Settings.basic_settings.DATA_PATH, "frontend", "results.html")
        if os.path.exists(results_path):
            return FileResponse(results_path)
        return {"message": "审计结果页面不存在", "docs": "/results"}

    @app.get("/docs", summary="swagger 文档", include_in_schema=False)
    async def document():
        return RedirectResponse(url="/docs")

    @app.get("/", summary="界面首页", include_in_schema=False)
    async def document():
        return RedirectResponse(url="/index")

    app.include_router(ocr_router)
    app.include_router(audit_rule_router)
    app.include_router(audit_result_router)
    app.include_router(contract_router)
    app.include_router(task_router)

    return app


def run_api(host, port):
    uvicorn.run(app, host=host, port=port)


app = create_app()