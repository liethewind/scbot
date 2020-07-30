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
            "content": "本群已开启舰船价格配置查询功能(初版)\n需要全程@机器人\n输入指令:舰船查询\t舰船查询可查询舰船厂商\n输入指令:圣盾\t输入厂商可查询该厂商所有船只\n输入指令:锤头鲨\t输入船只可查看详细数据\n\n初代版本,还请包涵",
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
            self.push_text(i,"舰船查询")
            self.push_pic(i,url)

if __name__ == "__main__":
    # 实例化类
    pume = push_message()
    # 定义发送群组
    group_list = [782905877,723481562,723481562,1030367337,1057135024,1018604511]
    #group_list = [555061148,1030367337,830432074,123189407,1018604511,1057135024,450971267]
    # 发送图片消息
    pume.push_quere_pic(group_list,"http://bot.stisd.cn/cdn/pic/xx.jpg")
