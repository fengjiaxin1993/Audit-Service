"""
FastAPI 后端主应用 - PDF OCR 与关键词定位系统
前后端分离架构
"""
import logging
import uvicorn
from server.api_server.server_app import create_app
from server.common.task_queue import start_task_workers
from server.db.base import Base, engine

# 确保所有模型被导入，SQLAlchemy 才能自动建表
from server.db.models.contract_model import ContractModel  # noqa
from server.db.models.audit_rule_model import AuditRuleModel  # noqa
from server.db.models.task_model import TaskModel  # noqa
from server.db.models.audit_result_model import AuditResultModel

# -------------- 配置日志（在抑制 stderr 之前设置） --------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_tables():
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表已创建/更新")


# ==================== 主程序入口 ====================
def run_api_server():
    print()  # 空行
    logger.info("=" * 50)
    logger.info("OCR API 服务启动中...")
    logger.info("=" * 50)

    app = create_app()

    host = "127.0.0.1"
    port = 8000

    logger.info(f"本地地址:  http://{host}:{port}")
    logger.info(f"API 文档:  http://{host}:{port}/docs")
    logger.info(f"前端页面:  http://{host}:{port}/")
    logger.info("=" * 50)
    print()  # 空行

    create_tables()
    start_task_workers()
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_api_server()
