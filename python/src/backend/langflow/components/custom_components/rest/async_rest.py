import aiohttp
import asyncio

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def post(url, body):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, data=body) as response:
            return await response.text()

async def main():
    url = "http://172.22.102.61:48080/admin-api/agent/text/langFlowAsk"
    body = {
        "query": "介绍如何摆脱push",
        "knowledge_base_ids": ["d728b8d382914250a634bf4aa0134d0d"],
        "maximum_number_of_recalls": 2,
        "minimum_matching_degree": 0.5,
        "search_strategy": "fulltext",
        "tenant_id": 1
    }
    res = await post(url, body=body)
    print(res)

# 运行异步任务
asyncio.run(main())
