from pathlib import Path
import sys
import typing as t
from pydantic_settings_file import *

# chatchat 数据目录，必须通过环境变量设置。如未设置则自动使用当前目录。
CHATCHAT_ROOT = Path(".").resolve()


class BasicSettings(BaseFileSettings):
    """
    服务器基本配置信息
    """

    model_config = SettingsConfigDict(yaml_file=CHATCHAT_ROOT / "basic_settings.yaml")

    # @computed_field
    @cached_property
    def PACKAGE_ROOT(self) -> Path:
        """代码根目录"""
        return Path(__file__).parent

    # @computed_field
    @cached_property
    def DATA_PATH(self) -> Path:
        """用户数据根目录"""
        p = CHATCHAT_ROOT / "data"
        return p

    # @computed_field
    @cached_property
    def CACHE_DATA_PATH(self) -> Path:
        """OCR缓存目录"""
        p = self.DATA_PATH / "cache"
        return p


    # @computed_field
    @cached_property
    def UPLOADS_DIR(self) -> Path:
        """文件上传目录"""
        p = self.DATA_PATH / "uploads"
        return p

    SQLALCHEMY_DATABASE_URI: str = "sqlite:///" + str(CHATCHAT_ROOT / "data/info.db")
    """知识库信息数据库连接URI"""

    MAX_CONCURRENT_AUDIT_LLM: int = 2
    """审计最多同时启用LLM数"""

    PDF_DPI: int = 200
    """OCR 使用的 DPI（控制 OCR 精度和速度）"""

    OCR_BASE_URL: str = "http://localhost:7840"
    """OCR 使用的 DPI（控制 OCR 精度和速度）"""

    DEFAULT_BIND_HOST: str = "0.0.0.0" if sys.platform != "win32" else "127.0.0.1"
    """
    各服务器默认绑定host。如改为"0.0.0.0"需要修改下方所有XX_SERVER的host
    Windows 下 WEBUI 自动弹出浏览器时，如果地址为 "0.0.0.0" 是无法访问的，需要手动修改地址栏
    """

    API_SERVER: dict = {"host": DEFAULT_BIND_HOST, "port": 7861}
    """API 服务器地址"""

    def make_dirs(self):
        '''创建所有数据目录'''
        for p in [
            self.DATA_PATH,
            self.CACHE_DATA_PATH,
            self.UPLOADS_DIR
        ]:
            p.mkdir(parents=True, exist_ok=True)


class PlatformConfig(MyBaseModel):
    """模型加载平台配置"""

    platform_name: str = "ollama"
    """平台名称"""

    platform_type: t.Literal["ollama", "openai"] = "ollama"
    """平台类型"""

    llm_base_url: str = "http://127.0.0.1:11434/v1"
    """openai api url"""

    embedding_base_url: str = "http://127.0.0.1:11434/v1"
    """openai api url"""

    llm_api_key: str = "EMPTY"
    """api key if available"""

    embedding_api_key: str = "EMPTY"
    """api key if available"""

    llm_models: t.Union[t.Literal["auto"], t.List[str]] = []
    """该平台支持的大语言模型列表"""

    embed_models: t.Union[t.Literal["auto"], t.List[str]] = []
    """该平台支持的嵌入模型列表"""


class ApiModelSettings(BaseFileSettings):
    """模型配置项"""

    model_config = SettingsConfigDict(yaml_file=CHATCHAT_ROOT / "model_settings.yaml")

    DEFAULT_LLM_MODEL: str = "qwen2.5:0.5b"
    """默认选用的 LLM 名称"""

    IS_ALIYUN_PLATFORM: bool = True
    """针对openAI, 是否是阿里云百练平台的接口"""

    DEFAULT_EMBEDDING_MODEL: str = "quentinz/bge-small-zh-v1.5"
    """默认选用的 Embedding 名称"""

    HISTORY_LEN: int = 3
    """默认历史对话轮数"""

    MAX_TOKENS: t.Optional[int] = 4096  # TODO: 似乎与 LLM_MODEL_CONFIG 重复了
    """大模型最长支持的长度，如果不填写，则使用模型默认的最大长度，如果填写，则为用户设定的最大长度"""

    TEMPERATURE: float = 0.7
    """LLM通用对话参数"""

    LLM_MODEL_CONFIG: t.Dict[str, t.Dict] = {
        "llm_model": {
            "model": "",
            "prompt_name": "default",
        }
    }
    """
    LLM模型配置，包括了不同模态初始化参数。
    `model` 如果留空则自动使用 DEFAULT_LLM_MODEL
    """

    MODEL_PLATFORMS: t.List[PlatformConfig] = [
        PlatformConfig(**{
            "platform_name": "ollama",
            "platform_type": "ollama",
            "llm_base_url": "http://192.168.88.1:11434/v1",
            "embedding_base_url": "http://192.168.88.1:11434/v1",
            "llm_api_key": "EMPTY",
            "embedding_api_key": "EMPTY",
            "llm_models": [
                "qwen2.5:0.5b",
            ],
            "embed_models": [
                "quentinz/bge-small-zh-v1.5",
            ],
        }),
        PlatformConfig(**{
            "platform_name": "openai",
            "platform_type": "openai",
            "llm_base_url": "https://api.openai.com/v1",
            "embedding_base_url": "https://api.openai.com/v1",
            "llm_api_key": "EMPTY",
            "embedding_api_key": "EMPTY",
            "llm_models": [
                "gpt-4o",
                "gpt-3.5-turbo",
            ],
            "embed_models": [
                "text-embedding-3-small",
                "text-embedding-3-large",
            ],
        }),
    ]
    """模型平台配置"""



class SettingsContainer:
    CHATCHAT_ROOT = CHATCHAT_ROOT

    basic_settings: BasicSettings = settings_property(BasicSettings())
    model_settings: ApiModelSettings = settings_property(ApiModelSettings())

    def create_all_templates(self):
        self.basic_settings.create_template_file(write_file=True)
        self.model_settings.create_template_file(sub_comments={
            "MODEL_PLATFORMS": {"model_obj": PlatformConfig(),
                                "is_entire_comment": True}},
            write_file=True)

    def set_auto_reload(self, flag: bool = True):
        self.basic_settings.auto_reload = flag
        self.model_settings.auto_reload = flag


Settings = SettingsContainer()

if __name__ == "__main__":
    Settings.create_all_templates()
