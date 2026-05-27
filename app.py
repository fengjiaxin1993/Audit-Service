"""
FastAPI 后端主应用 - PDF OCR 与关键词定位系统
前后端分离架构
"""
import logging
import uvicorn
from server.api_server.server_app import create_app

# -------------- 配置日志（在抑制 stderr 之前设置） --------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ==================== 主程序入口 ====================
def run_api_server():
    print()  # 空行
    logger.info("=" * 50)
    logger.info("PDF OCR API 服务启动中...")
    logger.info("=" * 50)

    app = create_app()

    host = "127.0.0.1"
    port = 8000

    logger.info(f"本地地址:  http://{host}:{port}")
    logger.info(f"API 文档:  http://{host}:{port}/docs")
    logger.info(f"前端页面:  http://{host}:{port}/")
    logger.info("=" * 50)
    print()  # 空行

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_api_server()
