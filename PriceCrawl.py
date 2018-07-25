"""
实时股价爬取
"""

from libs.common import *
from libs.mail import *
from libs.settings import *


class PriceCrawl(object):
    def __init__(self):
        self.__module = self.__class__.__name__

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

    def get_crawl_task(self):
        """
        从数据库获取待爬列表
        """
        pass

    def main(self):
        try:
            task = self.get_crawl_task()
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
