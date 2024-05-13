import traceback
from concurrent.futures import ThreadPoolExecutor, wait
from queue import Queue
from sys import stdout
from time import strftime, localtime

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

connection_url = URL.create(
    "mssql+pymssql",
    username="xxx",
    password="xxx",
    host="192.168.1.150",
    # port=5432,
    database="xxx",
)

# conn_str = f'mssql+pyodbc://sa/{encoded_database_name}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server'

mysql_engine = create_engine(connection_url, pool_recycle=3600)


def log_console(info):
    local_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    stdout.write(f'{local_time}\t{info}\r\n')


def read_sql(db_engine, sql, value_data=()):
    # sql = sql % value_data
    # print(sql)
    # sql = text(sql)
    with db_engine.connect() as conn:
        result = conn.execute(sql, value_data)
        info_list = result.fetchall()
    return info_list


def write_sql(db_engine, sql, value_data=()):
    with db_engine.connect() as conn:
        conn.execute(sql, value_data)

# def write_sql(db_engine, sql, value_data=()):
#     sql = sql % value_data
#     sql = text(sql)
#     with db_engine.connect() as conn:
#         conn.execute(sql)
#         conn.commit()


def execute(engine, sql, **params):
    # print(params)
    with engine.connect() as connection:
        transaction = connection.begin()  # 开始sql 事务
        try:
            stmt = text(sql)
            # 执行查询操作
            result = connection.execute(stmt, params)
            transaction.commit()  # 数据写入执行成功，数据提交到数据库文件
            return result
        except Exception as ee:
            transaction.rollback()  # 数据写入失败或者sql执行失败，会回滚这个事务中所有执行的sql，数据库中就不会出现报错整段数据
            print('出现错误，数据已回滚！')
            traceback.print_exc()
            raise ee


def read_sql_data_dict_list(db_engine, sql, value_data=()):
    with db_engine.connect() as conn:
        all_result = conn.execute(sql, value_data)
        data_dict_list = [dict(zip(result.keys(), result)) for result in all_result]
    return data_dict_list


class ThreadPool:
    def __init__(self, thread_num, queue_add_number=3):
        self.pool = ThreadPoolExecutor(max_workers=thread_num)
        self.queue = Queue(thread_num + queue_add_number)
        self.future_list = []
        for _ in range(thread_num):
            future = self.pool.submit(self._run)
            self.future_list.append(future)

    def _run(self):
        while True:
            signal, function, args, kwargs = self.queue.get()
            if signal is True:
                break
            function(*args, **kwargs)

    def _add_close_signal(self):
        for _ in range(len(self.future_list) + 5):
            self.queue.put((True, None, None, None))

    def add_task(self, function, args=(), kwargs=None):
        if kwargs is None:
            kwargs = {}
        self.queue.put((False, function, args, kwargs))

    def wait_done(self):
        self._add_close_signal()
        wait(self.future_list)


def get_new_proxy(proxy):
    proxy_list = ['http://192.168.1.171:42000', 'http://192.168.1.171:38118']
    proxy_list.remove(proxy)
    remaining_proxy = proxy_list[0] if len(proxy_list) > 0 else None
    return remaining_proxy
