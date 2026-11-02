"""mem0 自托管 MCP 封装。

官方 mem0-mcp-server 硬编码连 Mem0 Cloud，此包直接调自托管 REST API
（即 mem0ai/mem0 仓库 server/ 目录部署的那套服务）。

环境变量:
  MEM0_BASE_URL         REST API 地址（如 https://mem0.example.com/apiv1）
  MEM0_API_KEY          面板签发的 m0sk- 开头 API key
  MEM0_DEFAULT_USER_ID  默认 user_id（默认 "ivan"）

自测: mem0-mcp --selftest
"""
import os
import sys
import httpx
from mcp.server.fastmcp import FastMCP

BASE_URL = os.environ.get("MEM0_BASE_URL", "")
API_KEY = os.environ.get("MEM0_API_KEY", "")
DEFAULT_USER = os.environ.get("MEM0_DEFAULT_USER_ID", "ivan")
TIMEOUT = 120  # LLM 抽取事实可能较慢

mcp = FastMCP("mem0")


def _hdr() -> dict:
    return {"X-API-Key": API_KEY}


def _post(path: str, payload: dict) -> str:
    r = httpx.post(f"{BASE_URL}{path}", headers=_hdr(), json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


@mcp.tool()
def add_memory(content: str, user_id: str = DEFAULT_USER) -> str:
    """存记忆：写入一段文本（服务端 LLM 自动抽取事实并去重/合并）。

    Args:
        content: 要记住的内容（用户说的话、偏好、事实等）
        user_id: 记忆归属用户，默认当前配置用户
    """
    return _post("/memories", {
        "messages": [{"role": "user", "content": content}],
        "user_id": user_id,
    })


@mcp.tool()
def search_memories(query: str, user_id: str = DEFAULT_USER, top_k: int = 5) -> str:
    """语义搜索记忆（自然语言查询，按相关度返回）。

    Args:
        query: 搜索词，如 "用户的饮食偏好"
        user_id: 限定用户
        top_k: 返回条数，默认 5
    """
    return _post("/search", {"query": query, "user_id": user_id, "top_k": top_k})


@mcp.tool()
def list_memories(user_id: str = DEFAULT_USER, limit: int = 100) -> str:
    """列出某用户的全部记忆。

    Args:
        user_id: 用户标识
        limit: 最多返回条数
    """
    r = httpx.get(f"{BASE_URL}/memories", headers=_hdr(),
                  params={"user_id": user_id, "top_k": limit}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


@mcp.tool()
def delete_memory(memory_id: str) -> str:
    """按 id 删除一条记忆（id 从 search/list 结果获取）。

    Args:
        memory_id: 记忆 UUID
    """
    r = httpx.delete(f"{BASE_URL}/memories/{memory_id}", headers=_hdr(), timeout=TIMEOUT)
    r.raise_for_status()
    return r.text


def main():
    if "--selftest" in sys.argv:
        if not BASE_URL or not API_KEY:
            sys.exit("请先设置 MEM0_BASE_URL 和 MEM0_API_KEY 环境变量")
        print(f"BASE_URL: {BASE_URL}")
        print(f"user: {DEFAULT_USER}, key: {API_KEY[:8]}...")
        print(_post("/search", {"query": "test", "user_id": DEFAULT_USER, "top_k": 1}))
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
