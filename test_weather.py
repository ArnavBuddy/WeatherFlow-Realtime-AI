import httpx
import asyncio

async def test():
    try:
        print("Testing wttr.in...")
        async with httpx.AsyncClient() as client:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = await client.get(f"https://wttr.in/Delhi?format=%C,+%t", headers=headers, timeout=10.0)
            print(f"Status: {response.status_code}")
            print(f"Result: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())
