import threading
import re
import requests
import queue
import time
import json
import pandas
import csv
import xlwt
all_list = []
all_que= queue.Queue()
Header = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/78.0.3904.108 Safari/537.36'}
#Url_st = 'http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=lof&rs=&gs=0&sc=dm&st=asc&sd=2019-03-23&ed=2020-03-23&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1'


class Get_page(threading.Thread):
    def __init__(self, threadID, page, header1):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.page = page
        self.header = header1
        self.data = queue.Queue()


    def run(self):

        try:
            global all_que
            #threading.Lock().acquire()
            self.data.put(self.make_list(self.page, self.header))
            all_que.put(self.make_list(self.page, self.header))
        finally:
            #threading.Lock().release()
            pass
        print("结束 " + self.threadID)

    def make_list(self, url, header):#数据处理
        page_temp = requests.get(url, headers=header)
        fund_data = re.findall(r'(?<={datas:[[]).+(?=[]],allRecords)', page_temp.text)
        fun_str = ",".join(fund_data)
        fund = re.sub(r'(")', "", fun_str)
        fund = re.sub(r',(\d{4}-\d{1,2}-\d{1,2})', "", fund)

        fund_data = fund.split(',')
        flag = 0
        for i in range(len(fund_data) - 1, -1, -1):
            flag += 1

            if flag <= 8:
                fund_data.pop(i)
            if flag == 23:
                flag = 0

        return fund_data

    def add_list(self,fund):
        threading.Lock.acquire()






sum_of_fundpage=0
sum_of_JJ_num = 0

def Get_all_page(header, url_st):#获取所有url

    page = requests.get(url_st, headers=header)

    fund_list = re.findall(r'(?<=,allPages:)[\d]{1,4}(?=,allNum:)', page.text)
    fund_num = re.findall(r'(?<=allRecords:)[\d]{0,5}(?=,pageIndex)', page.text)

    global sum_of_fundpage
    global sum_of_JJ_num

    sum_of_fundpage = int(fund_list[0])
    sum_of_JJ_num = int(fund_num[0])
    print(sum_of_fundpage)
    sun_url = queue.Queue(sum_of_fundpage)
    url_st_fix = re.sub(r'(?<=ft=).*(?=&rs=)',code_type,url_st)

    for i in range(1,sum_of_fundpage+1,1):
      url_st_fix=re.sub(r'(?<=&pi=).*(?=&pn=)', str(i), url_st_fix)
      sun_url.put(url_st_fix)
    return sun_url

def make_csv(data):


    columns = ["基金编号","基金名称","基金代号","单位净值","累计净值","日增长率","近一周","近一个月","近三个月","近六个月","近一年","近两年","近三年","今年以来","成立以来"]
    index=[str(i) for i in range(sum_of_JJ_num)]
    df1=pandas.DataFrame(data,index=index,columns=columns)
    print(df1)
    df1.to_excel(r'C:\Users\mimilam\Desktop\list.xls')


def divide(ls, each):
    """
            分割链表
    """
    dividedLs = []
    eachExact = float(each)
    groupCount = int(len(ls) / each)
    groupCountExact = len(ls) / eachExact
    start = 0
    for i in range(groupCount):
        dividedLs.append(ls[start:start + each])
        start = start + each
    if groupCount < groupCountExact:  # 假如有余数，将剩余的所有元素加入到最后一个分组
        dividedLs.append(ls[groupCount * each:])
    return dividedLs


code_type = ''


def Get_start_url():
    JJ_kind={ '股票': 'gp', '混合': 'hh', '债券': 'zq', '指数': 'zs', 'qdii': 'qdii', 'fof': 'fof','lof': 'lof'}
    print('请输入你要查询的基金类型：' +'ps:股票、混合、债券、指数、qdii、fof、lof,全部')

    global code_type

    code = input('请输入： ')
    code_type = JJ_kind[code]
    st_url='http://fund.eastmoney.com/data/rankhandler.aspx?op=ph&dt=kf&ft=' + code_type+ '&rs=&gs=0&sc=dm&st=asc&sd=2019-03-23&ed=2020-03-23&qdii=&tabSubtype=,,,,,&pi=1&pn=50&dx=1'
    return  st_url


if __name__ == '__main__':
    Url_st = Get_start_url()

    page_que = Get_all_page(Header, Url_st)
    thread_id = []
    for i in range(1, sum_of_fundpage+1, 1):
        thread_id.append('th'+str(i))
    for thread_DD in thread_id:
        thread = Get_page(thread_DD, page_que.get(), Header)
        thread.setDaemon(True)
        thread.start()
    for thread_DD in thread_id:
        thread.join()
    for i in range( sum_of_fundpage ):
        a=all_que.get()

        all_list.extend(divide(a,15))
    make_csv(all_list)















