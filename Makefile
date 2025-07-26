# Dify RAG MCP Server Makefile

.PHONY: help install install-dev test test-unit test-integration test-e2e test-coverage lint format type-check clean build run-stdio run-sse run-websocket docs

# 默认目标
help:
	@echo "Dify RAG MCP Server - 可用命令:"
	@echo ""
	@echo "安装和环境:"
	@echo "  install        - 安装项目依赖"
	@echo "  install-dev    - 安装开发依赖"
	@echo "  clean          - 清理临时文件和缓存"
	@echo ""
	@echo "测试:"
	@echo "  test           - 运行所有测试"
	@echo "  test-unit      - 运行单元测试"
	@echo "  test-integration - 运行集成测试"
	@echo "  test-e2e       - 运行端到端测试"
	@echo "  test-coverage  - 运行测试并生成覆盖率报告"
	@echo ""
	@echo "代码质量:"
	@echo "  lint           - 运行代码检查"
	@echo "  format         - 格式化代码"
	@echo "  type-check     - 运行类型检查"
	@echo ""
	@echo "服务器管理（推荐）:"
	@echo "  server-start   - 启动MCP服务器（stdio模式）"
	@echo "  server-start-sse - 启动MCP服务器（SSE模式）"
	@echo "  server-start-websocket - 启动MCP服务器（WebSocket模式）"
	@echo "  server-stop    - 停止MCP服务器"
	@echo "  server-restart - 重启MCP服务器（stdio模式）"
	@echo "  server-restart-sse - 重启MCP服务器（SSE模式）"
	@echo "  server-status  - 查看服务器状态"
	@echo ""
	@echo "构建和运行:"
	@echo "  build          - 构建项目"
	@echo "  run-stdio      - 直接运行stdio模式的MCP服务器"
	@echo "  run-sse        - 直接运行SSE模式的MCP服务器"
	@echo "  run-websocket  - 直接运行WebSocket模式的MCP服务器"
	@echo ""
	@echo "文档:"
	@echo "  docs           - 生成文档"

# 安装依赖
install:
	@echo "安装项目依赖..."
	pip install -e .

install-dev:
	@echo "安装开发依赖..."
	pip install -e ".[dev]"
	pre-commit install

# 测试
test:
	@echo "运行所有测试..."
	pytest

test-unit:
	@echo "运行单元测试..."
	pytest -m "unit or not (integration or e2e)"

test-integration:
	@echo "运行集成测试..."
	pytest -m integration

test-e2e:
	@echo "运行端到端测试..."
	pytest -m e2e

test-coverage:
	@echo "运行测试并生成覆盖率报告..."
	pytest --cov=src --cov-report=html --cov-report=term-missing
	@echo "覆盖率报告已生成到 htmlcov/index.html"

# 代码质量
lint:
	@echo "运行代码检查..."
	flake8 src test
	black --check src test
	isort --check-only src test

format:
	@echo "格式化代码..."
	black src test
	isort src test

type-check:
	@echo "运行类型检查..."
	mypy src

# 清理
clean:
	@echo "清理临时文件和缓存..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

# 构建
build:
	@echo "构建项目..."
	python -m build

# 运行服务器（使用管理脚本）
server-start:
	@echo "启动MCP服务器（stdio模式）..."
	./manage_server.sh start

server-start-sse:
	@echo "启动MCP服务器（SSE模式）..."
	./manage_server.sh start sse

server-start-websocket:
	@echo "启动MCP服务器（WebSocket模式）..."
	./manage_server.sh start websocket

server-stop:
	@echo "停止MCP服务器..."
	./manage_server.sh stop

server-restart:
	@echo "重启MCP服务器（stdio模式）..."
	./manage_server.sh restart

server-restart-sse:
	@echo "重启MCP服务器（SSE模式）..."
	./manage_server.sh restart sse

server-status:
	@echo "查看服务器状态..."
	./manage_server.sh status

# 运行服务器（直接命令）
run-stdio:
	@echo "启动stdio模式的MCP服务器..."
	python -m src.main --transport stdio

run-sse:
	@echo "启动SSE模式的MCP服务器 (http://localhost:8000)..."
	python -m src.main --transport sse --host localhost --port 8000

run-websocket:
	@echo "启动WebSocket模式的MCP服务器 (ws://localhost:9000)..."
	python -m src.main --transport websocket --host localhost --port 9000

# 开发模式运行
dev-stdio:
	@echo "开发模式启动stdio MCP服务器..."
	DIFY_LOG_LEVEL=DEBUG python -m src.main --transport stdio

dev-sse:
	@echo "开发模式启动SSE MCP服务器..."
	DIFY_LOG_LEVEL=DEBUG python -m src.main --transport sse --host localhost --port 8000

# 文档
docs:
	@echo "生成文档..."
	mkdocs build

docs-serve:
	@echo "启动文档服务器..."
	mkdocs serve

# 健康检查
health-check:
	@echo "运行健康检查..."
	python -c "import asyncio; from src.mcp.server import create_server; asyncio.run(create_server().health_check())"

# 安全检查
security-check:
	@echo "运行安全检查..."
	bandit -r src/
	safety check

# 依赖检查
dep-check:
	@echo "检查依赖更新..."
	pip list --outdated

# 完整的CI检查
ci-check: lint type-check test-coverage security-check
	@echo "所有CI检查完成!"

# 发布准备
release-check: clean ci-check build
	@echo "发布检查完成!"

# 快速开发设置
dev-setup: install-dev
	@echo "开发环境设置完成!"
	@echo "现在可以运行: make dev-stdio"

# 示例数据
load-sample-data:
	@echo "加载示例数据..."
	python scripts/load_sample_data.py

# 数据库迁移（如果需要）
migrate:
	@echo "运行数据库迁移..."
	# 这里可以添加数据库迁移命令

# 监控和日志
logs:
	@echo "查看日志..."
	tail -f logs/dify-mcp-server.log

# 性能测试
perf-test:
	@echo "运行性能测试..."
	pytest -m "slow" --durations=0

# 内存分析
memory-profile:
	@echo "运行内存分析..."
	python -m memory_profiler scripts/memory_test.py

# 代码复杂度分析
complexity:
	@echo "分析代码复杂度..."
	radon cc src/ -a

# 生成requirements.txt
freeze:
	@echo "生成requirements.txt..."
	pip freeze > requirements.txt

# 更新依赖
update-deps:
	@echo "更新依赖..."
	pip install --upgrade pip
	pip install --upgrade -r requirements.txt

# 验证安装
verify-install:
	@echo "验证安装..."
	python -c "import src; print('✓ 项目导入成功')"
	python -c "from src.mcp.server import DifyMCPServer; print('✓ MCP服务器导入成功')"
	python -c "from src.api.client import DifyAPIClient; print('✓ API客户端导入成功')"
	@echo "✓ 所有核心模块验证通过!"