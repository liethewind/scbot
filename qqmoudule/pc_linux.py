import requests,os,shutil,time,random,string
from selenium import webdriver
from lxml import etree
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

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
    imgpath = "pic/getimg.png"
    driver.save_screenshot(imgpath)
    driver.quit()     
    
    print("Screenshot of success")

if __name__ == "__main__":
    get_image()
