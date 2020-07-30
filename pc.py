import requests

from lxml import etree

url = 'https://status.robertsspaceindustries.com/'

get = requests.get(url).text

selector = etree.HTML(get)
tjmsg = selector.xpath('//span[@class="hidden sm:inline"]/text()')[0].strip()
gjmsg = selector.xpath('//span[@class="hidden sm:inline"]/text()')[1].strip()
cjmsg = selector.xpath('//span[@class="hidden sm:inline"]/text()')[2].strip()
def mssg():
    if gjmsg == "Operational":
	    return("持续性宇宙服务器当前状态:正常运行" )
    elif gjmsg == "Degraded Performance":
        return('持续性宇宙服务器当前状态: 性能低下')
    elif gjmsg == "Under Maintenance":
        return('持续性宇宙服务器当前状态: 维护中')
    elif gjmsg == "Partial Outage":
         return('持续性宇宙服务器当前状态: 部分宕机')
#    elif tjmsg == "Operational":
#         return('星际公民官网当前状态: 正常运转')
#    elif tjmsg == "Degraded Performance":
#        return('星际公民官网当前状态: 性能低下')
#    elif tjmsg == "Partial Outage":
#        return('星际公民官网当前状态: 部分宕机')
#    elif tjmsg == "Under Maintenance":
#        return('星际公民官网当前状态: 维护中')
#print(gjmsg)
if __name__ == '__main__':
    print(mssg())
