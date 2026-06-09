# Audit-Service 合同智能审计系统

## 项目概述

**Audit-Service** 是一个基于 OCR + 大语言模型（LLM）的合同智能审计系统，提供 PDF 合同文件的上传、预览、文字识别、规则管理和多维度审计功能。系统采用前后端分离架构，后端使用 FastAPI 框架，前端使用原生 HTML/CSS/JavaScript，LLM 调用阿里云百炼（DashScope）API。

### 核心功能

- 📤 **PDF 文件上传** — 支持 PDF 文件上传，自动去重（同名文件重新提交任务）
- 📄 **PDF 页面预览** — 将 PDF 页面渲染为图片并在前端展示，支持翻页
- 🔍 **审计规则管理** — 可视化增删改查审计规则，支持一键初始化默认规则
- 🎯 **字段定位高亮** — 在 PDF 页面上精确定位并高亮显示提取的字段位置
- 🤖 **LLM 智能审计** — 基于预置规则，调用大模型对合同进行多维度合规性审查
- 🔄 **异步任务队列** — 上传后自动进入后台队列，依次执行 OCR 识别 → 审计，结果实时可查

---

## 目录结构

```
Audit-Service/
│
├── startup.py                      # 服务启动入口（推荐方式）
├── cli.py                          # CLI 命令行入口（数据库初始化等）
├── init_database.py                # 数据库初始化脚本
├── settings.py                     # Pydantic Settings 配置管理
├── pydantic_settings_file.py       # YAML 配置读取基类
├── setup.py                        # 项目安装脚本
├── basic_settings.yaml             # 基础配置（路径、端口、LLM 并发数等）
├── model_settings.yaml             # 模型配置（LLM 平台、API Key、模型列表）
│
├── frontend/                       # 前端页面（原生 HTML/JS）
│   ├── index.html                  # 首页：PDF 上传、预览、审计结果展示
│   └── rules.html                  # 规则管理页：审计规则增删改查
│
├── server/                         # 后端服务模块
│   ├── api_server/                # API 路由层
│   │   ├── server_app.py          # FastAPI 应用创建、CORS、中间件配置
│   │   ├── main_routes.py         # 上传 / pdf_pages / 任务状态 / 审计结果接口
│   │   ├── audit_rule_routes.py   # 审计规则 CRUD + 初始化接口
│   │   ├── audit_result_routes.py # 审计结果查询接口
│   │   ├── contract_routes.py     # 合同列表 / 详情 / 删除接口
│   │   ├── task_routes.py         # 任务列表 / 状态 / 删除 / 重新处理接口
│   │   ├── utils.py               # ApiResponse 统一响应模型
│   │   └── static/               # Swagger UI / ReDoc 静态资源
│   │
│   ├── audit/                     # 审计核心逻辑
│   │   ├── audit_graph.py         # 审计图引擎（节点执行、依赖管理）
│   │   ├── extract_audit.py       # 从数据库读取规则并调用 LLM 执行审计
│   │   └── model.py              # 审计相关数据模型（AuditContext 等）
│   │
│   ├── common/                    # 通用工具
│   │   ├── pdf_tools.py          # PDF 转图片（Base64）、获取页面信息
│   │   ├── file_tools.py         # 缓存目录管理、文件工具
│   │   ├── locate_tools.py        # 字段定位工具
│   │   ├── task_queue.py         # 异步任务队列（ThreadPoolExecutor）
│   │   └── tools.py              # 通用工具函数
│   │
│   ├── db/                        # 数据库层
│   │   ├── base.py               # SQLAlchemy Base
│   │   ├── session.py            # Session 上下文管理器
│   │   ├── models/               # ORM 模型
│   │   │   ├── contract_model.py   # 合同表（file_name, file_size, status 等）
│   │   │   ├── task_model.py       # 任务表（contract_id, status 等）
│   │   │   ├── audit_rule_model.py # 审计规则表（name, description, keywords 等）
│   │   │   └── audit_result_model.py # 审计结果表（rule_id, is_compliant 等）
│   │   └── repository/            # Repository 数据访问层
│   │       ├── contract_repository.py
│   │       ├── task_repository.py
│   │       ├── audit_rule_repository.py
│   │       └── audit_result_repository.py
│   │
│   ├── logger_utils.py            # Loguru 日志封装
│   └── utils.py                   # FastAPI 离线静态资源注入
│
├── tests/                          # 测试脚本（手动测试用，非 pytest 单元测试）
│   └── ...
│
└── data/                           # 数据目录（自动创建）
    ├── uploads/                   # 上传的 PDF 文件
    └── cache/                    # OCR/审计结果缓存
```

---

## 技术栈

| 类别 | 技术 |
|------|------|
| **后端框架** | FastAPI + Uvicorn |
| **前端** | HTML5 + CSS3 + JavaScript（原生，无框架） |
| **LLM** | 阿里云百炼 DashScope API（OpenAI 兼容格式） |
| **PDF 处理** | PyMuPDF（fitz） |
| **图像处理** | Pillow + OpenCV |
| **数据库** | SQLite + SQLAlchemy 2.0 |
| **配置管理** | Pydantic Settings + YAML |
| **任务队列** | ThreadPoolExecutor（异步后台任务） |
| **日志** | Loguru |

---

## API 接口概览

所有接口均以 `/api` 为前缀，统一响应格式为：

```json
{
  "success": true,
  "message": "操作成功",
  "data": { ... }
}
```

### 合同管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload` | 上传 PDF 文件，自动创建任务 |
| GET | `/api/contracts/list` | 获取合同列表 |
| GET | `/api/contracts/detail/{id}` | 获取合同详情 |
| POST | `/api/contracts/delete/{id}` | 删除合同（同时删除文件、缓存、数据库记录） |

### 任务管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks` | 获取所有任务列表 |
| GET | `/api/tasks/{id}` | 获取任务详情 |
| GET | `/api/tasks/contract/{id}` | 获取合同对应的任务 |
| POST | `/api/tasks/delete/{id}` | 删除任务（同时删除关联审计结果） |
| POST | `/api/tasks/reprocess/{contract_id}` | 重新处理合同（重新入队） |

### 审计规则管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/rules/create` | 新建规则 |
| GET | `/api/rules/list` | 获取规则列表 |
| GET | `/api/rules/detail/{id}` | 获取规则详情 |
| POST | `/api/rules/update/{id}` | 更新规则 |
| POST | `/api/rules/delete/{id}` | 删除规则 |
| POST | `/api/rules/init_default` | 一键初始化默认规则（新增/更新/跳过三种行为） |

### 审计结果

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/audit-results/task/{task_id}` | 获取任务的所有审计结果及通过/失败统计 |

### PDF 处理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/pdf_pages` | 获取 PDF 页面信息（图像 Base64） |
| GET | `/api/task/status/{id}` | 查询任务状态（pending / processing / completed / failed） |
| POST | `/api/get_audit_result` | 获取审计结果（含字段定位信息） |

完整的 Swagger 文档访问：`http://localhost:7861/docs`

---

## 配置说明

所有配置通过 YAML 文件管理，无需修改代码。

### `basic_settings.yaml` — 基础配置

```yaml
# API 服务地址
API_SERVER:
  host: 127.0.0.1
  port: 7861

# 并发 LLM 数量
MAX_CONCURRENT_AUDIT_LLM: 2

# PDF OCR DPI（越高精度越好，但速度越慢）
PDF_DPI: 200

# OCR 服务地址
OCR_BASE_URL: http://localhost:7840
```

### `model_settings.yaml` — 模型配置

```yaml
DEFAULT_LLM_MODEL: qwen3-32b
DEFAULT_EMBEDDING_MODEL: text-embedding-v4
TEMPERATURE: 0.7
MAX_TOKENS: 4096

MODEL_PLATFORMS:
  - platform_name: openai
    platform_type: openai
    llm_base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    llm_api_key: sk-xxxxxxxxxxxxxxxx  # 替换为你的 API Key
    llm_models:
      - qwen3-32b
    embed_models:
      - text-embedding-v4
```

---

## 快速启动

### 1. 安装依赖

```bash
conda create -n ICDO-RNV python=3.11
conda activate ICDO-RNV
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

### 2. 初始化数据库（首次运行）

```bash
python cli.py init
```

### 3. 启动服务

```bash
python startup.py
```

> 也可通过 CLI 启动：`python cli.py start`

服务启动后将显示：

```
服务地址:  http://127.0.0.1:7861
首页地址:  http://127.0.0.1:7861/index
规则管理地址:  http://127.0.0.1:7861/rules
API 文档:  http://127.0.0.1:7861/docs
```

### 4. 访问应用

- **首页（合同上传与审计）**: http://127.0.0.1:7861/index
- **规则管理**: http://127.0.0.1:7861/rules
- **API 文档**: http://127.0.0.1:7861/docs

---

## 使用流程

```
┌─────────────────────────────────────────────────────┐
│                     首页 /index                      │
│                                                      │
│  1. 上传 PDF 文件（拖拽或点击选择）                    │
│       ↓                                             │
│  2. 自动进入后台任务队列，实时查询状态                 │
│       ↓                                             │
│  3. 审计完成后，右侧面板展示审计结果                   │
│       ↓                                             │
│  4. 点击字段名 → 对应 PDF 位置高亮定位                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   规则管理 /rules                     │
│                                                      │
│  • 查看已有审计规则                                    │
│  • 新建 / 编辑 / 删除规则                             │
│  • 一键「初始化规则」导入默认规则库                    │
└─────────────────────────────────────────────────────┘
```

### 首页使用步骤

1. 打开 http://127.0.0.1:7861/index
2. 点击「选择文件」上传 PDF 合同
3. 上传成功后自动进入后台处理，显示任务状态
4. OCR + 审计完成后，右侧面板显示字段提取结果和审计结论
5. 鼠标悬停字段名，PDF 页面上对应位置自动高亮

### 规则管理使用步骤

1. 打开 http://127.0.0.1:7861/rules
2. 点击「初始化规则」可一键导入 8 条默认审计规则（主体、付款、违约、知识产权等）
3. 点击「新建规则」自定义审计维度
4. 规则自动关联到后续的审计任务中

---

## 默认审计规则

系统内置 2 条默认审计规则：

| 规则名称 | 审计内容 |
|---------|---------|
| 法律法规判断 | 判断引用的法规是否正确 |
| 厂站情况判断 | 厂站情况描述是否齐全，是否详细 |

---

## 注意事项

1. **API Key** — 首次使用需在 `model_settings.yaml` 中配置阿里云百炼的 API Key
2. **OCR 服务** — 需确保 `basic_settings.yaml` 中的 `OCR_BASE_URL` 服务可用
3. **并发控制** — `MAX_CONCURRENT_AUDIT_LLM` 控制同时调用 LLM 的最大数量，避免 API 限流
4. **CORS** — 当前允许所有来源访问（`allow_origins=["*"]`），生产环境请按需限制
5. **数据目录** — `data/uploads/` 和 `data/cache/` 目录由系统自动创建，无需手动建立
