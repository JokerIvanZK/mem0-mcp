# mem0-mcp

Self-hosted [mem0](https://github.com/mem0ai/mem0) REST API 的 MCP 封装。

官方 `mem0-mcp-server` 硬编码连 Mem0 Cloud；本包直接调自托管实例
（mem0ai/mem0 仓库 `server/` 目录部署的服务），数据与 Web 面板完全同源。

## 工具

| Tool | API |
|------|-----|
| `add_memory` | `POST /memories` |
| `search_memories` | `POST /search` |
| `list_memories` | `GET /memories` |
| `delete_memory` | `DELETE /memories/{id}` |

## 使用（任意 MCP 客户端）

```json
{
  "mcpServers": {
    "mem0": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/JokerIvanZK/mem0-mcp.git", "mem0-mcp"],
      "env": {
        "MEM0_BASE_URL": "https://your-mem0-host/apiv1",
        "MEM0_API_KEY": "m0sk-xxx",
        "MEM0_DEFAULT_USER_ID": "your-name"
      }
    }
  }
}
```

自测：`MEM0_BASE_URL=... MEM0_API_KEY=... uvx --from git+... mem0-mcp --selftest`
