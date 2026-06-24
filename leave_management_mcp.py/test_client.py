import asyncio
from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

async def main():
    async with streamablehttp_client("http://127.0.0.1:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List all tools
            tools = await session.list_tools()
            print("Tools:", [t.name for t in tools.tools])
            
            # List all resources
            resources = await session.list_resources()
            print("Resources:", resources)

asyncio.run(main())