import requests
#import pc_linux


#test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())

class push_message:

    def __init__(self):
        self.qqapi = "http://180.76.160.99:8888"
        self.getapi = (self.qqapi + "/v1/Github/InstallService")
        self.pushapi = (self.qqapi + "/v1/LuaApiCaller?funcname=SendMsg&qq=2630354273")

    def push_text(self,sendqq,message):
        data = {
        "toUser": sendqq,
        "sendToType": 2,
        "sendMsgType": "TextMsg",
        "content": message,
        "groupid": 0,
        "atUser": 0
        }
        requests.get(self.getapi)
        res = requests.post(self.pushapi,json=data)

    def push_pic(self,sendqq,picrul):
        data = {
            "toUser": sendqq,
            "sendToType": 2,
            "sendMsgType": "PicMsg",
            # "content": test_yz_msg,
            "content": "二测重构代码成类",
            "groupid": 0,
            "atUser": 0,
            "picUrl": picrul,
            "picBase64Buf": "",
            "fileMd5": ""
        }
        requests.get(self.getapi)
        res = requests.post(self.pushapi,json=data)
        print(res)

    # 发送群组消息函数
    def push_quere_pic(self,qqqu,url):
        #pc_linux.get_image()
        for i in qqqu:
            self.push_text(i,"今日公民服务器播报")
            self.push_pic(i,url)

if __name__ == "__main__":
    # 实例化类
    pume = push_message()
    # 定义发送群组
    group_list = [782905877,723481562]
    # group_list = [555061148,1030367337,830432074,123189407,1018604511,1057135024,450971267]
    # 发送图片消息
    pume.push_quere_pic(group_list,"http://bot.stisd.cn/cdn/pic/getimg.png")