"""
实时股价爬取
"""
import asyncio

import aiohttp
import pymongo

from libs.common import *
from libs.mail import *
from libs.settings import *

SH_URL = 'http://hq.sinajs.cn/list=sh%s'
SZ_URL = 'http://hq.sinajs.cn/list=sz%s'
HK_URL = 'http://hq.sinajs.cn/list=rt_hk%s'

# 并发数量
CONCURRENT_COUNT = 5


class PriceCrawl(object):
    def __init__(self):
        self.__module = self.__class__.__name__
        host = MONGODB_HOST
        port = MONGODB_PORT
        user = MONGODB_USER
        pwd = MONGODB_PWD
        db_name = MONGODB_DBNAME
        self.client = pymongo.MongoClient(host=host, port=port)
        self.db = self.client[db_name]
        if user and user != '':
            self.db.authenticate(name=user, password=pwd)
        self.times = 0

    @staticmethod
    def write_file_log(msg, __module='', level='error'):
        filename = os.path.split(__file__)[1]
        if level == 'debug':
            logging.getLogger().debug('File:' + filename + ', ' + __module + ': ' + msg)
        elif level == 'warning':
            logging.getLogger().warning('File:' + filename + ', ' + __module + ': ' + msg)
        else:
            logging.getLogger().error('File:' + filename + ', ' + __module + ': ' + msg)

    # debug log
    def debug(self, msg, func_name=''):
        __module = "%s.%s" % (self.__module, func_name)
        self.write_file_log(msg, __module, 'debug')

    # error log
    def error(self, msg, func_name=''):
        __module = "%s.%s" % (self.__module, func_name)
        self.write_file_log(msg, __module, 'error')

    @staticmethod
    async def fetch(session, url):
        """
        并发请求网页
        """
        async with session.get(url, timeout=10, allow_redirects=True) as response:
            return await response.read()

    async def get_stock_info(self, stock):
        """
        获取股票信息
        """
        code = stock['stock_code']
        _type = stock['stock_type']
        if _type == 'hk':
            url = HK_URL % code
        elif _type == 'sh':
            url = SH_URL % code
        elif _type == 'sz':
            url = SZ_URL % code
        else:
            return False
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            response = await self.fetch(session=session, url=url)
            response = str(response, encoding='gbk')
            if _type == 'hk':
                current_price = self.get_hk_current_price(response)
            elif _type == 'sh':
                current_price = self.get_sh_current_price(response)
            elif _type == 'sz':
                current_price = self.get_sz_current_price(response)
            else:
                current_price = None
            self.times += 1
            print(self.times, url, stock['stock_name'], current_price)

    def get_crawl_list(self):
        """
        从数据库获取待爬列表
        """
        result = self.db['monitor_task'].find()
        return list(result)

    @staticmethod
    def get_hk_current_price(content):
        """
        获取 HK 股票的当前价格
        """
        # ['var hq_str_rt_hk08525="BYLEASING', '百应租赁', '1.970', '1.280', '2.130', '1.430', '1.500', '0.220', '17.188', '1.490', '1.500',
        # '53709340.000', '31460000', '0.000', '0.000', '2.130', '1.430', '2018/07/18', '11:06:23', '2|3', 'N|N|N', '0.000|0.000|0.000',
        # '0|||0.000|0.000|0.000', '|0', 'Y";\n']
        """
        1.970：今日开盘
        1.280：昨日收盘
        2.130：最高价
        1.430：最低价
        1.500：当前价格
        """
        content = content.split(',')
        current_price = content[6]
        return current_price

    @staticmethod
    def get_sh_current_price(content):
        """
        获取 SH 股票的当前价格
        """
        # var hq_str_sh601166 = "兴业银行,15.410,15.300,15.270,15.420,15.120,15.270,15.280,34044862,519094256.000,
        # 10200,15.270,127700,15.260,180100,15.250,116000,15.240,109200,15.230,42100,15.280,155200,15.290,194653,
        # 15.300,172700,15.310,69300,15.320,2018-07-25,13:53:36,00";
        """
        1.970：今日开盘
        1.280：昨日收盘
        2.130：最高价
        1.430：最低价
        1.500：当前价格
        """
        content = content.split(',')
        current_price = content[7]
        return current_price

    @staticmethod
    def get_sz_current_price(content):
        """
        获取 SZ 股票的当前价格
        """
        # var hq_str_sz000423 = "东阿阿胶,53.620,53.600,53.280,53.700,53.260,53.260,53.280,1763100,94207206.200,7900,53.260,5800,53.250," \
        # "1100,53.240,400,53.230,6500,53.220,12000,53.280,600,53.320,3800,53.330,3900,53.350,300,53.360,2018-07-25,13:53:33,00";
        """
        
        """
        content = content.split(',')
        current_price = content[7]
        return current_price

    def handle_crawl(self, task):
        """
        处理股票爬虫任务
        """
        try:
            for i in range(0, len(task), CONCURRENT_COUNT):
                start = i
                stop = min(i + CONCURRENT_COUNT, len(task))
                batch_task = list()
                for j in range(start, stop):
                    batch_task.append(task[j])
                if len(batch_task) > 0:
                    loop = asyncio.get_event_loop()
                    tasks = [self.get_stock_info(stock=stock) for stock in batch_task]
                    loop.run_until_complete(asyncio.wait(tasks))

        except Exception as e:
            self.error(str(e), get_current_func_name())

    def main(self):
        try:
            crawl_list = self.get_crawl_list()
            while True:
                self.handle_crawl(crawl_list)
                time.sleep(0.1)
        except Exception as e:
            self.error(str(e), get_current_func_name())


if __name__ == '__main__':
    if not os.path.exists('logs'):
        os.makedirs('logs')
    init_log(console_level=logging.DEBUG, file_level=logging.DEBUG,
             logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + ".log")
    # 专门存储错误日志
    init_log(console_level=logging.ERROR, file_level=logging.ERROR,
             logfile="logs/" + str(os.path.split(__file__)[1].split(".")[0]) + "_error.log")
    master = PriceCrawl()
    master.main()
