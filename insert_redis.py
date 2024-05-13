import json
from concurrent.futures import ThreadPoolExecutor
import redis
from zw_scrapy.untils import mysql_engine, read_sql


redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
def task(line):
    try:
        print(line)
        data = {'id': line[0], 'file_name': line[1]}
        json_data = json.dumps(data)
        redis_client.rpush('zwspider:start_urls', json_data)
    except Exception as e:
        print(e)
def main():
    with ThreadPoolExecutor(16) as pool:
        for i in read_sql(mysql_engine,'select id,[文件名] from [zwqk20231129] WHERE id BETWEEN 225 AND 228 order by id '):
            # print(i)
            pool.submit(task,i)
if __name__ == '__main__':
    main()
