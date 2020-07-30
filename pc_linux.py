import requests,os,shutil,time,random,string
from selenium import webdriver
from lxml import etree
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

url = 'https://status.robertsspaceindustries.com/'

get = requests.get(url).text

selector = etree.HTML(get)

# gjmsg = selector.xpath('//span[@class="hidden sm:inline"]/text()')[1].strip()
# def mssg(msg):
#     if msg == "Degraded Performance":
#         return('持续性宇宙服务器当前状态: 性能低下')
#     elif msg == "Under Maintenance":
#         return('持续性宇宙服务器当前状态: 维护中')
#     elif msg == "Partial Outage":
#         return('持续性宇宙服务器当前状态: 部分宕机')
def mssg1():
    gjmsg = selector.xpath('//span[@class="hidden sm:inline"]/text()')[0].strip()
    if gjmsg == "Operational":
        return('官网当前状态: 正常运行')
    elif gjmsg == "Under Maintenance":
        return('官网当前状态: 维护中')
    elif gjmsg == "Partial Outage":
        return('官网当前状态: 部分宕机')
def mssg2():
    gjmsg = selector.xpath('//span[@class="hidden sm:inline"]/text()')[1].strip()
    if gjmsg == "Degraded Performance":
        return('持续性宇宙服务器当前状态: 性能低下')
    elif gjmsg == "Under Maintenance":
        return('持续性宇宙服务器当前状态: 维护中')
    elif gjmsg == "Partial Outage":
        return('持续性宇宙服务器当前状态: 部分宕机')

def mssg3():
    gjmsg = selector.xpath('//span[@class="hidden sm:inline"]/text()')[2].strip()
    if gjmsg == "Operational":
        return('可登录状态: 正常')
    elif gjmsg == "Under Maintenance":
        return('可登陆状态: 维护中')
    elif gjmsg == "Partial Outage":
        return('可登陆状态: 部分宕机')
def mssg4():
    return("“锤头鲨”是一艘带有多个炮塔的快速巡逻舰，专门用于战斗机，同样适合于支持舰队中的大型主力舰或作为战斗机集团的旗舰。官网价格:$725\n游戏币价格:12459900\n获取方式:舰队周或周年庆开放购买或者客服PY$1325包中也包含锤头鲨,游戏内赫斯顿空港可游戏币购买\n船员:12位\n货仓容量:40\n最大速度:1000\n生命值:60800\n护盾:179868\n常规DPS:14162\n量子燃料:11000\n武器配置\n6个S5可动载人炮台\n24个S4武器槽位\n32枚S3导弹")
def get_image():
    display = Display(visible=0)
    display.start()
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')
    #chrome_options.add_argument('blink-settings=imagesEnabled=false')
    chrome_options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_size(1200,900) 

    url = "https://status.robertsspaceindustries.com/"
    driver.get(url)

    body_element = driver.find_elements_by_tag_name('body')
    body_height = body_element[0].size.get('height')
    body_width = body_element[0].size.get('width')
    if body_height and body_width and int(body_height) > 0 and int(body_width) > 0:
        driver.set_window_size(int( body_width),int(body_height))
    #imgpath = ('pic/' + ''.join(random.sample(string.digits,9)) + '.png')
    imgpath = "pic/getimg2.png"
    driver.save_screenshot(imgpath)
    driver.quit()     
    
    print("Screenshot of success")

if __name__ == "__main__":
    mssg()
