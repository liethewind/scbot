import requests

from lxml import etree

url = 'https://status.robertsspaceindustries.com/'

get = requests.get(url).text

selector = etree.HTML(get)

gjmsg = selector.xpath('//span[@class="hidden sm:inline"]/text()')[1].strip()
def mssg():
    if gjmsg == "Degraded Performance":
        return('持续性宇宙服务器当前状态: 性能低下')
    elif gjmsg == "Under Maintenance":
        return('持续性宇宙服务器当前状态: 维护中')
    elif gjmsg == "Partial Outage":
        return('持续性宇宙服务器当前状态: 部分宕机')

#print(gjmsg)
if __name__ == '__main__':
    mssg()