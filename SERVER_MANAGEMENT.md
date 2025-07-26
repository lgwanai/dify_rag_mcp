# Dify RAG MCP Server 管理指南

本项目提供了一个便捷的shell脚本来管理MCP服务器的启动、停止和重启操作。

## 管理脚本使用方法

### 基本语法
```bash
./manage_server.sh {start|stop|restart|status} [transport_type]
```

### 可用命令

- **start** - 启动MCP服务器
- **stop** - 停止MCP服务器
- **restart** - 重启MCP服务器
- **status** - 显示服务器状态

### 传输类型

- **stdio** - 标准输入/输出（默认）
- **sse** - 服务器发送事件（HTTP）
- **websocket** - WebSocket

### 使用示例

#### 启动服务器
```bash
# 使用默认的stdio传输方式启动
./manage_server.sh start

# 使用SSE传输方式启动
./manage_server.sh start sse

# 使用WebSocket传输方式启动
./manage_server.sh start websocket
```

#### 停止服务器
```bash
./manage_server.sh stop
```

#### 重启服务器
```bash
# 重启并使用stdio传输
./manage_server.sh restart

# 重启并使用SSE传输
./manage_server.sh restart sse
```

#### 查看状态
```bash
./manage_server.sh status
```

#### 查看帮助
```bash
./manage_server.sh help
```

## 服务器端点信息

根据选择的传输类型，服务器将在以下端点提供服务：

- **STDIO**: 通过标准输入/输出进行通信
- **SSE**: `http://localhost:8000/sse/`
- **WebSocket**: `ws://localhost:8000/ws`

## 日志和PID文件

- **日志文件**: `server.log` - 包含服务器运行日志
- **PID文件**: `.server.pid` - 包含服务器进程ID（由脚本管理）

## 注意事项

1. **权限**: 确保脚本有执行权限：
   ```bash
   chmod +x manage_server.sh
   ```

2. **端口冲突**: 如果使用SSE或WebSocket模式，确保端口8000未被其他服务占用

3. **环境配置**: 确保已正确配置`.env`文件或`config/config.yaml`中的API密钥

4. **依赖检查**: 启动前确保已安装所有必要的Python依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 故障排除

### 服务器启动失败
1. 检查日志文件`server.log`中的错误信息
2. 确认API配置是否正确
3. 检查端口是否被占用
4. 验证Python环境和依赖

### 无法停止服务器
1. 脚本会先尝试优雅关闭（SIGTERM）
2. 如果10秒后仍未关闭，会强制终止（SIGKILL）
3. 手动清理：`rm -f .server.pid`

### 状态检查不准确
脚本通过PID文件跟踪服务器状态。如果服务器是通过其他方式启动的，脚本可能无法正确检测状态。

## 手动启动方式

如果不使用管理脚本，也可以手动启动服务器：

```bash
# STDIO模式
python src/main.py --transport stdio

# SSE模式
python src/main.py --transport sse

# WebSocket模式
python src/main.py --transport websocket
```

## 集成到系统服务

可以将此脚本集成到系统服务管理器中（如systemd），实现开机自启动和服务监控。

### systemd服务示例

创建服务文件 `/etc/systemd/system/dify-rag-mcp.service`：

```ini
[Unit]
Description=Dify RAG MCP Server
After=network.target

[Service]
Type=forking
User=your_username
WorkingDirectory=/path/to/dify-rag-mcp
ExecStart=/path/to/dify-rag-mcp/manage_server.sh start sse
ExecStop=/path/to/dify-rag-mcp/manage_server.sh stop
ExecReload=/path/to/dify-rag-mcp/manage_server.sh restart sse
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable dify-rag-mcp
sudo systemctl start dify-rag-mcp
```