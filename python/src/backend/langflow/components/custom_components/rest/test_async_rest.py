import aiohttp
import asyncio
import time
import httpx

def test_aiohttp():
    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.read()
    
    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(1000):
                task = asyncio.ensure_future(fetch(session, 'https://www.baidu.com'))
                tasks.append(task)
            responses = await asyncio.gather(*tasks)
    
    print("aiohttp:")
    
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end_time = time.time()
    
    print('Time taken: ', end_time - start_time)

def test_httpx():
    async def main():
        async with httpx.AsyncClient() as client:
            for i in range(1000):
                response = await client.get('https://www.baidu.com')
 
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    end_time = time.time()
    
    print('Time taken: ', end_time - start_time)

async def main():
    # 知识库调用测试
    try:
        async with httpx.AsyncClient() as client:
            url = "http://172.22.102.61:48080/admin-api/agent/text/langFlowAsk"
            body = {
                "query": "tcp的优点",
                "knowledge_base_ids": ["54db9bf6fbef4489831b032a353e0592"],
                "maximum_number_of_recalls": 3,
                "minimum_matching_degree": 0.5,
                "search_strategy": "fulltext",
                "tenant_id": "1",
            }
            response = await client.post(url=url, json=body, timeout=20)
            if response.is_success:
                # 解析响应数据
                knowledge_call_response_dict = response.json()
                response_code = knowledge_call_response_dict.get("code")
                response_msg = knowledge_call_response_dict.get("msg")
                if response_code != 0:
                    raise ValueError(f"知识库检索失败，具体原因: {response_msg}")
                
                if not (response_data := knowledge_call_response_dict.get("data")):
                    raise ValueError(f"知识库检索结果为空")
                print(f"res_data: {response_data}")
            else:
                print(f"error: {response.status_code}")
    except httpx.TimeoutException:
        raise ValueError("知识库调用请求超时")
    except httpx.HTTPStatusError as e:
        raise ValueError(f"知识库调用请求状态异常, 状态码: {e.response.status_code}") from e
    except:
        raise
    
if __name__ == "__main__":
    asyncio.run(main())