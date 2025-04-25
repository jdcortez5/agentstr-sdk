from server import create_server
from mcp.server.fastmcp import FastMCP
import os

mcp = FastMCP("nostr-tools", host=os.environ['UVICORN_HOST'], port=int(os.environ['UVICORN_PORT']))

create_server(mcp)

if __name__ == "__main__":
    mcp.run(transport="sse")
