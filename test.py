from src.services.s3 import S3Client

import asyncio



async def test():
    res = await S3Client().generate_presigned_urls_by_prefix('rooms/21', 3600)
    print(res)

asyncio.run(test())
