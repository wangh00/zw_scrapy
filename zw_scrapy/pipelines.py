# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import gzip
import os
from io import BytesIO

from sqlalchemy import text
from zw_scrapy.untils import write_sql, mysql_engine

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from zw_scrapy.settings import SAVE_FILE

class ZwScrapyPipeline:
    def process_item(self, item, spider):
        content = item['content']
        output_path = os.path.join(SAVE_FILE, item['file_path'])

        content_bytes = content.encode('utf-8')
        if not os.path.exists(output_path.rsplit('\\', 1)[0]):
            os.makedirs(output_path.rsplit('\\', 1)[0])
        with gzip.open(output_path, 'wb') as f:
            f.write(content_bytes)
        spider.logger.info(f"已保存：{output_path}")
        return item

