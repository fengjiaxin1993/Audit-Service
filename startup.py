# Apply pathlib patches before any other imports to fix WindowsPath issues
import uvicorn
import logging
# 屏蔽第三方库的冗余日志
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("rapid_doc").setLevel(logging.WARNING)
logging.getLogger("rapidocr").setLevel(logging.WARNING)
logging.getLogger("rapid_table").setLevel(logging.WARNING)
logging.getLogger("rapid_layout").setLevel(logging.WARNING)
logging.getLogger("onnxruntime").setLevel(logging.WARNING)
from server.logger_utils import build_logger
import click
from settings import Settings
from server.api_server.server_app import create_app
logger = build_logger()


def run_api_server():
    logger.info(f"Api MODEL_PLATFORMS: {Settings.model_settings.MODEL_PLATFORMS}")
    app = create_app()
    host = Settings.basic_settings.API_SERVER["host"]
    port = Settings.basic_settings.API_SERVER["port"]
    logger.info(f"服务地址:  http://{host}:{port}")
    logger.info(f"首页地址:  http://{host}:{port}/index")
    logger.info(f"规则管理地址:  http://{host}:{port}/rules")
    logger.info(f"API 文档:  http://{host}:{port}/docs")
    logger.info("=" * 50)
    uvicorn.run(app, host=host, port=port)

@click.command(help="启动服务")
def main():
    run_api_server()


if __name__ == "__main__":
    main()
