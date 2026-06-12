import sys
from functools import partial
import loguru
import loguru._logger


def build_logger():
    logger = loguru.logger.opt(colors=True)
    logger.opt = partial(loguru.logger.opt, colors=True)

    # 移除默认 sink，重新添加一个带自定义格式的 stdout sink
    logger.remove()
    logger.add(
        sys.stdout,
        colorize=True,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <6}</level> | "
            "<cyan>{file}:{line: <4}</cyan> | "
            "{message}"
        ),
    )
    return logger
