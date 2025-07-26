# Dify RAG MCP Server

一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 的 Dify RAG 服务器，提供知识库管理、文档处理、分段管理和智能搜索功能。

## 🚀 特性

- **完整的知识库管理**: 创建、更新、删除、复制知识库
- **文档处理**: 支持文本和文件上传，文档状态管理
- **分段管理**: 文档分段的增删改查，批量操作
- **智能搜索**: 语义搜索、关键词搜索、混合搜索、全文搜索
- **多种传输方式**: 支持 stdio、SSE、WebSocket
- **异步架构**: 高性能异步处理
- **完整测试**: 单元测试、集成测试、端到端测试
- **类型安全**: 完整的 TypeScript 风格类型注解

## 📋 系统要求

- Python 3.8+
- Dify API 访问权限

## 🛠️ 安装

### 1. 克隆项目

```bash
git clone <repository-url>
cd dify-rag-mcp
```

### 2. 安装依赖

```bash
# 生产环境
pip install -e .

# 开发环境
pip install -e ".[dev]"

# 或使用 Makefile
make install-dev
```

### 3. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置
vim .env
```

必需的环境变量：

```bash
DIFY_API_KEY=your_dify_api_key_here
DIFY_BASE_URL=https://api.dify.ai/v1  # 可选，默认值
```

## 🚀 快速开始

### 使用管理脚本（推荐）

项目提供了便捷的管理脚本来启动、停止和重启服务器：

```bash
# 启动服务器（默认 stdio 模式）
./manage_server.sh start

# 启动 SSE 模式服务器
./manage_server.sh start sse

# 启动 WebSocket 模式服务器
./manage_server.sh start websocket

# 查看服务器状态
./manage_server.sh status

# 停止服务器
./manage_server.sh stop

# 重启服务器
./manage_server.sh restart sse

# 查看帮助
./manage_server.sh help
```

详细的管理脚本使用说明请参考 [SERVER_MANAGEMENT.md](SERVER_MANAGEMENT.md)。

### 命令行启动

也可以直接使用 Python 命令启动：

```bash
# stdio 模式（默认）
python -m src.main --transport stdio

# SSE 模式
python -m src.main --transport sse --host localhost --port 8000

# WebSocket 模式
python -m src.main --transport websocket --host localhost --port 9000

# 使用 Makefile
make run-stdio
make run-sse
make run-websocket
```

### 开发模式

```bash
# 开发模式启动（启用调试日志）
make dev-stdio
make dev-sse

# 或直接使用环境变量
DIFY_LOG_LEVEL=DEBUG python -m src.main --transport stdio
```

### 健康检查

```bash
# 检查服务器状态
python -m src.main --health-check

# 或使用 Makefile
make health-check
```

## 📚 使用方法

### MCP 工具

服务器提供以下 MCP 工具：

#### 知识库管理
- `create_dataset` - 创建知识库
- `list_datasets` - 列出知识库
- `get_dataset` - 获取知识库详情
- `update_dataset` - 更新知识库
- `delete_dataset` - 删除知识库
- `copy_dataset` - 复制知识库

#### 文档管理
- `list_documents` - 列出文档
- `create_document_by_text` - 通过文本创建文档
- `create_document_by_file` - 通过文件创建文档
- `get_document` - 获取文档详情
- `update_document` - 更新文档
- `delete_document` - 删除文档

#### 分段管理
- `list_segments` - 列出分段
- `create_segment` - 创建分段
- `get_segment` - 获取分段详情
- `update_segment` - 更新分段
- `delete_segment` - 删除分段
- `batch_enable_segments` - 批量启用分段
- `batch_disable_segments` - 批量禁用分段

#### 搜索功能
- `semantic_search` - 语义搜索
- `keyword_search` - 关键词搜索
- `hybrid_search` - 混合搜索
- `fulltext_search` - 全文搜索
- `multi_dataset_search` - 多知识库搜索

### MCP 资源

- `dataset://{dataset_id}` - 知识库资源
- `document://{dataset_id}/{document_id}` - 文档资源
- `segment://{dataset_id}/{segment_id}` - 分段资源

### 配置文件

支持 YAML 配置文件：

```yaml
# config/production.yaml
dify_api_key: "your_api_key"
dify_base_url: "https://api.dify.ai/v1"
environment: "production"
log_level: "INFO"
timeout: 30
max_retries: 3
```

使用配置文件启动：

```bash
python -m src.main --config config/production.yaml
```

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
make test

# 运行特定类型的测试
make test-unit        # 单元测试
make test-integration # 集成测试
make test-e2e        # 端到端测试

# 生成覆盖率报告
make test-coverage
```

### 测试标记

```bash
# 运行特定标记的测试
pytest -m "dataset"    # 知识库相关测试
pytest -m "search"     # 搜索相关测试
pytest -m "slow"       # 慢速测试
```

## 🔧 开发

### 代码质量

```bash
# 代码检查
make lint

# 代码格式化
make format

# 类型检查
make type-check

# 完整的 CI 检查
make ci-check
```

### 项目结构

```
dify-rag-mcp/
├── src/                    # 源代码
│   ├── api/               # API 客户端
│   │   ├── client.py      # 主客户端
│   │   ├── dataset.py     # 知识库 API
│   │   ├── document.py    # 文档 API
│   │   ├── segment.py     # 分段 API
│   │   └── search.py      # 搜索 API
│   ├── config/            # 配置管理
│   │   └── settings.py    # 设置类
│   ├── mcp/               # MCP 服务器
│   │   ├── server.py      # 主服务器
│   │   ├── tools/         # MCP 工具
│   │   └── resources/     # MCP 资源
│   ├── utils/             # 工具函数
│   └── main.py            # 主入口
├── test/                  # 测试代码
│   ├── test_api/          # API 测试
│   ├── test_mcp/          # MCP 测试
│   └── test_integration/  # 集成测试
├── config/                # 配置文件
├── logs/                  # 日志文件
└── docs/                  # 文档
```

### 添加新功能

1. **添加 API 方法**: 在相应的 API 类中添加方法
2. **添加 MCP 工具**: 在 `src/mcp/tools/` 中添加工具
3. **添加测试**: 在 `test/` 目录中添加对应测试
4. **更新文档**: 更新 README 和相关文档

## 📖 API 文档

### Dify API 客户端

```python
from src.api.client import DifyAPIClient
from src.config.settings import Settings

# 创建客户端
settings = Settings(dify_api_key="your_key")
client = DifyAPIClient(settings)

# 使用知识库 API
datasets = await client.dataset.list_datasets()
dataset = await client.dataset.create_dataset(
    name="测试知识库",
    description="这是一个测试知识库"
)

# 使用搜索 API
results = await client.search.semantic_search(
    dataset_id=dataset["id"],
    query="搜索查询",
    top_k=5
)
```

### MCP 服务器

```python
from src.mcp.server import create_server, run_server
from src.config.settings import Settings

# 创建服务器
settings = Settings(dify_api_key="your_key")
server = create_server(settings)

# 运行服务器
await run_server(
    settings=settings,
    transport="sse",
    host="localhost",
    port=8000
)
```

## 🔒 安全

- API 密钥通过环境变量管理
- 支持 HTTPS/WSS 连接
- 输入验证和错误处理
- 日志脱敏处理

## 📊 监控

### 日志

```bash
# 查看日志
make logs

# 或直接查看文件
tail -f logs/dify-mcp-server.log
```

### 性能监控

```bash
# 性能测试
make perf-test

# 内存分析
make memory-profile

# 代码复杂度
make complexity
```

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发指南

- 遵循 PEP 8 代码风格
- 添加类型注解
- 编写测试用例
- 更新文档
- 运行 `make ci-check` 确保代码质量

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

- 📧 邮箱: support@example.com
- 🐛 问题反馈: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 文档: [项目文档](https://your-docs-url.com)

## 🙏 致谢

- [Model Context Protocol](https://modelcontextprotocol.io/) - MCP 协议
- [Dify](https://dify.ai/) - AI 应用开发平台
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP 服务器框架

## 📈 路线图

- [ ] 支持更多搜索算法
- [ ] 添加缓存机制
- [ ] 支持批量操作
- [ ] 添加 Web 管理界面
- [ ] 支持插件系统
- [ ] 添加监控面板

---

**Dify RAG MCP Server** - 让 AI 应用的知识管理更简单！