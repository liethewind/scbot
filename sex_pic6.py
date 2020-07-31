from datetime import datetime
import pc_linux,qqmoudule.mysql_cn
import xq
import socketio, requests, re, time, base64, random, json, psutil, cpuinfo, datetime, threading, sys, schedule
from queue import Queue, LifoQueue
import random
import string
with open('config.json', 'r', encoding='utf-8') as f:  # 从json读配置
    config = json.loads(f.read())
color_pickey = config['color_pickey']  # 申请地址api.lolicon.app
webapi = config['webapi']  # Webapi接口 http://127.0.0.1:8888
botqqs = config['botqqs']  # 机器人QQ号
setu_pattern = re.compile(config['setu_pattern'])  # 色图正则
setu_path = config['path']  # 色图路径
send_original_pic = config['send_original_pic']  # 是否发送原图
not_send_pic_info = config['not_send_pic_info']  # 是否只发图
setu_threshold = int(config['setu_threshold'])  # 发送上限
threshold_to_send = config['threshold_to_send']  # 超过上限后发送的文字
notfound_to_send = config['notfound_to_send']  # 没找到色图返回的文字
frequency_cap_to_send = config['frequency_cap_to_send']  # 达到频率上限后发送语句
wrong_input_to_send = config['wrong_input_to_send']  # 关键字错误返回的文字
before_nmsl_to_send = config['before_nmsl_to_send']  # 嘴臭之前发送的语句
before_setu_to_send_switch = config['before_setu_to_send_switch']  # 发色图之前是否发送消息
send_setu_at = config['send_setu_at']  # 发色图时是否@
before_setu_to_send = config['before_setu_to_send']  # 发色图之前的语句
group_blacklist = config['group_blacklist']
group_whitelist = config['group_whitelist']
group_r18_whitelist = config['group_r18_whitelist']
private_for_group_blacklist = config['private_for_group_blacklist']
private_for_group_whitelist = config['private_for_group_whitelist']
private_for_group_r18_whitelist = config['private_for_group_r18_whitelist']
RevokeMsg = config['RevokeMsg']
RevokeMsg_time = int(config['RevokeMsg_time'])
sentlist_switch = config['sentlist_switch']
good_morning = config['good_morning']
morning_keyword = config['morning_keyword']
good_night = config['good_night']
night_keyword = config['night_keyword']
morning_conf = config['morning_conf']
night_conf = config['night_conf']
morning_repeat = config['morning_repeat']
morning_num_msg = config['morning_num_msg']
night_repeat = config['night_repeat']
night_num_msg = config['night_num_msg']


frequency = config['frequency']
frequency_additional = config['frequency_additional']
reset_freq_time = config['reset_freq_time']

clear_sentlist_time = int(config['clear_sentlist_time'])
# -----------------------------------------------------
sio = socketio.Client()
q_pic = LifoQueue(maxsize=0)
q_text = LifoQueue(maxsize=0)
q_withdraw = Queue(maxsize=0)
# -----------------------------------------------------
api = webapi + '/v1/LuaApiCaller'
sent_list = []
freq_group_list = {}
morning_list = {}
night_list = {}
# night_list = {123456:[13546,12345]}
time_tmp = time.time()
print('获取配置成功~')


# -----------------------------------------------------


class GMess:
    # 群消息
    def __init__(self, message):
        # print(message)
        self.messtype = 'group'  # 标记群聊
        self.CurrentQQ = message['CurrentQQ']  # 接收到这条消息的QQ
        self.FromQQG = message['CurrentPacket']['Data']['FromGroupId']  # 来源QQ群
        self.QQGName = message['CurrentPacket']['Data']['FromGroupName']  # 来源QQ群昵称
        self.FromQQ = message['CurrentPacket']['Data']['FromUserId']  # 哪个QQ发过来的
        self.FromQQName = message['CurrentPacket']['Data']['FromNickName']  # 来源QQ名称(群内)
        self.MsgSeq = message['CurrentPacket']['Data']['MsgSeq']
        self.MsgRandom = message['CurrentPacket']['Data']['MsgRandom']
        self.MsgType = message['CurrentPacket']['Data']['MsgType']
        if self.MsgType == 'TextMsg':  # 普通消息
            self.Content = message['CurrentPacket']['Data']['Content']  # 消息内容
            self.At_Content = ''
        elif self.MsgType == 'AtMsg':  # at消息
            self.At_Content = re.sub(r'.*@.* ', '',
                                     json.loads(message['CurrentPacket']['Data']['Content'])['Content'])  # AT消息内容
            self.Content = ''  # 消息内容
        else:
            self.At_Content = ''
            self.Content = ''  # 消息内容


class Mess:
    # 私聊消息
    def __init__(self, message):
        # print(message)
        self.messtype = 'private'  # 标记私聊
        self.CurrentQQ = message['CurrentQQ']  # 接收到这条消息的QQ
        self.QQ = message['CurrentPacket']['Data']['ToUin']  # 接收到这条消息的QQ
        self.FromQQ = message['CurrentPacket']['Data']['FromUin']  # 哪个QQ发过来的
        self.MsgType = message['CurrentPacket']['Data']['MsgType']
        if self.MsgType == 'TextMsg':  # 普通消息
            self.Content = message['CurrentPacket']['Data']['Content']  # 消息内容
            self.FromQQG = 0
        elif self.MsgType == 'TempSessionMsg':  # 临时消息
            self.FromQQG = message['CurrentPacket']['Data']['TempUin']  # 通过哪个QQ群发起的
            self.Content = json.loads(message['CurrentPacket']['Data']['Content'])['Content']
        else:
            self.Content = ''
            self.FromQQG = 0


def send_text(mess, msg, atuser=0):
    if mess.messtype == 'group':
        t = 2  # 群聊
        toid = mess.FromQQG
    else:
        toid = mess.FromQQ  # 来自谁
        if mess.FromQQG == 0:  # 0为好友会话
            t = 1
        else:
            t = 3  # 3为临时会话
    params = {'qq': mess.CurrentQQ,  # bot的qq
              'funcname': 'SendMsg'}
    data = {"toUser": toid,
            "sendToType": t,
            "sendMsgType": "TextMsg",
            "content": msg,
            "groupid": mess.FromQQG,
            "atUser": atuser}
    try:
        res = requests.post(api, params=params, json=data, timeout=3)
        ret = res.json()['Ret']
    except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
        ret = '超时~'
    except (ValueError, KeyError):
        ret = '返回错误~'
    except:
        ret = ("未知错误:", sys.exc_info()[0])
    print('文字消息执行状态:[Ret:{}]'.format(ret))
    return


def send_pic(mess, msg, atuser=0, picurl='', picbase64='', picmd5=''):
    if mess.messtype == 'group':
        t = 2  # 群聊
        toid = mess.FromQQG
    else:
        toid = mess.FromQQ  # 来自谁
        if mess.FromQQG == 0:  # FromQQG为0是好友会话
            t = 1
        else:
            t = 3  # 3为临时会话
    params = {'qq': mess.CurrentQQ,
              'funcname': 'SendMsg'}
    data = {"toUser": toid,
            "sendToType": t,
            "sendMsgType": "PicMsg",
            "content": msg,
            "groupid": mess.FromQQG,
            "atUser": atuser,
            "picUrl": picurl,
            "picBase64Buf": picbase64,
            "fileMd5": picmd5}
    try:
        res = requests.post(api, params=params, json=data, timeout=10)
        ret = res.json()['Ret']
    except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
        ret = '超时~'
    except (ValueError, KeyError):
        ret = '返回错误~'
    except BaseException as e:
        # ret = ("未知错误:", sys.exc_info()[0])
        ret = ("未知错误:", e)
    print('图片消息执行状态:[Ret:{}]'.format(ret))
    return


def withdraw_message(mess):
    params = {'qq': mess.FromQQ,
              'funcname': 'RevokeMsg'}
    data = {"GroupID": mess.FromQQG,
            "MsgSeq": mess.MsgSeq,
            "MsgRandom": mess.MsgRandom}
    time.sleep(RevokeMsg_time)
    try:
        res = requests.post(api, params=params, json=data, timeout=3)
        ret = res.json()['Ret']
    except (requests.exceptions.ConnectTimeout, requests.exceptions.Timeout):
        ret = '超时~'
    except (ValueError, KeyError):
        ret = '返回错误~'
    except:
        ret = ("未知错误:", sys.exc_info()[0])
    print('撤回消息执行状态:[Ret:{}]'.format(ret))
    return


def get_cpu_info():
    info = cpuinfo.get_cpu_info()  # 获取CPU型号等
    cpu_count = psutil.cpu_count(logical=False)  # 1代表单核CPU，2代表双核CPU
    xc_count = psutil.cpu_count()  # 线程数，如双核四线程
    cpu_percent = round((psutil.cpu_percent()), 2)  # cpu使用率
    try:
        model = info['hardware_raw']  # cpu型号
    except:
        model = info['brand_raw']  # cpu型号
    try:  # 频率
        freq = info['hz_actual_friendly']
    except:
        freq = 'null'
    cpu_info = (model, freq, info['arch'], cpu_count, xc_count, cpu_percent)
    return cpu_info


def get_memory_info():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    total_nc = round((float(memory.total) / 1024 / 1024 / 1024), 3)  # 总内存
    used_nc = round((float(memory.used) / 1024 / 1024 / 1024), 3)  # 已用内存
    available_nc = round((float(memory.available) / 1024 / 1024 / 1024), 3)  # 空闲内存
    percent_nc = memory.percent  # 内存使用率
    swap_total = round((float(swap.total) / 1024 / 1024 / 1024), 3)  # 总swap
    swap_used = round((float(swap.used) / 1024 / 1024 / 1024), 3)  # 已用swap
    swap_free = round((float(swap.free) / 1024 / 1024 / 1024), 3)  # 空闲swap
    swap_percent = swap.percent  # swap使用率
    men_info = (total_nc, used_nc, available_nc, percent_nc, swap_total, swap_used, swap_free, swap_percent)
    return men_info


def uptime():
    now = time.time()
    boot = psutil.boot_time()
    boottime = datetime.datetime.fromtimestamp(boot).strftime("%Y-%m-%d %H:%M:%S")
    nowtime = datetime.datetime.fromtimestamp(now).strftime("%Y-%m-%d %H:%M:%S")
    up_time = str(datetime.datetime.utcfromtimestamp(now).replace(microsecond=0) - datetime.datetime.utcfromtimestamp(
        boot).replace(microsecond=0))
    alltime = (boottime, nowtime, up_time)
    return alltime


def sysinfo():
    cpu_info = get_cpu_info()
    mem_info = get_memory_info()
    up_time = uptime()
    msg = 'CPU型号:{0}\r\n频率:{1}\r\n架构:{2}\r\n核心数:{3}\r\n线程数:{4}\r\n负载:{5}%\r\n{6}\r\n' \
          '总内存:{7}G\r\n已用内存:{8}G\r\n空闲内存:{9}G\r\n内存使用率:{10}%\r\n{6}\r\n' \
          'swap:{11}G\r\n已用swap:{12}G\r\n空闲swap:{13}G\r\nswap使用率:{14}%\r\n{6}\r\n' \
          '开机时间:{15}\r\n当前时间:{16}\r\n已运行时间:{17}'
    full_meg = msg.format(cpu_info[0], cpu_info[1], cpu_info[2], cpu_info[3], cpu_info[4], cpu_info[5], '*' * 20,
                          mem_info[0], mem_info[1], mem_info[2], mem_info[3], mem_info[4],
                          mem_info[5], mem_info[6], mem_info[7], up_time[0], up_time[1], up_time[2])
    return full_meg



class Setu:
    def __init__(self, msg_in, tag='', num=1, r18=0):
        self.msg_in = msg_in
        self.tag = tag
        self.num = num  # 尝试获取的数量
        self.num_real = 0  # 实际的数量
        self.num_real_api_1 = 0  # api1的实际的数量
        self.api_1_num = 0  # api1
        self.r18 = r18
        self.setudata = None
        self.msg = []  # 待发送的消息
        self.download_url = []
        self.base64_codes = []

    def build_msg(self, title, artworkid, author, artistid, page, url_original):
        if not_send_pic_info:
            if send_setu_at and self.msg_in.messtype == 'group':
                msg = '[ATUSER({qq})]'.format(qq=self.msg_in.FromQQ)
            else:
                msg = ''
        else:
            purl = "www.pixiv.net/artworks/" + str(artworkid)  # 拼凑p站链接
            uurl = "www.pixiv.net/users/" + str(artistid)  # 画师的p站链接
            page = 'p' + str(page)
            if send_setu_at and self.msg_in.messtype == 'group':
                msg = '[ATUSER({qq})]\r\n标题:{title}\r\n{purl}\r\npage:{page}\r\n作者:{author}\r\n{uurl}\r\n原图:{url_original}'.format(
                    qq=self.msg_in.FromQQ, title=title, purl=purl, page=page, author=author,
                    uurl=uurl, url_original=url_original)
            else:
                msg = '标题:{title}\r\n{purl}\r\npage:{page}\r\n作者:{author}\r\n{uurl}\r\n原图:{url_original}'.format(
                    title=title, purl=purl, page=page, author=author,
                    uurl=uurl, url_original=url_original)
        return msg

    def base_64(self, filename):
        with open(filename, 'rb') as f:
            coding = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
            print('本地base64转码~')
            return coding.decode()

    def api_0(self):
        url = 'http://api.yuban10703.xyz:2333/setu_v3'
        params = {'type': self.r18,
                  'num': self.num,
                  'tag': self.tag}
        try:
            res = requests.get(url, params, timeout=5)
            setu_data = res.json()
            status_code = res.status_code
            print('从yubanのapi获取到{0}张setu'.format(setu_data['count']))  # 打印获取到多少条
            if status_code == 200:
                self.num_real = setu_data['count']  # 实际获取到多少条
                for data in setu_data['data']:
                    filename = data['filename']
                    if filename in sent_list and sentlist_switch:  # 如果发送过
                        print('发送过~')
                        self.num_real -= 1
                        continue
                    url_original = 'https://cdn.jsdelivr.net/gh/laosepi/setu/pics_original/' + filename
                    msg = self.build_msg(data['title'], data['artwork'], data['author'], data['artist'], data['page'],
                                         url_original)
                    self.msg.append(msg)
                    if setu_path == '':  # 非本地
                        self.base64_codes.append('')
                        if send_original_pic:  # 发送原画
                            self.download_url.append(url_original)
                        else:
                            self.download_url.append('https://cdn.jsdelivr.net/gh/laosepi/setu/pics/' + filename)
                    else:  # 本地
                        self.base64_codes.append(self.base_64(setu_path + filename))
                        self.download_url.append('')
                        # self.download_url.append(data[send_pic_type])
                    sent_list.append(filename)  # 记录发送过的图
        except Exception as e:
            print(e)

    def api_1(self):
        # 兼容api
        if self.r18 == 1:
            r18 = 0
        elif self.r18 == 3:
            r18 = 2
        elif self.r18 == 2:
            r18 = 1
        else:
            r18 = 0
        url = 'https://api.lolicon.app/setu/'
        params = {'r18': r18,
                  'apikey': color_pickey,
                  'num': self.api_1_num,
                  'size1200': not send_original_pic,
                  'proxy': 'disable'}
        if (len(self.tag) != 0) and (not self.tag.isspace()):  # 如果tag不为空(字符串字数不为零且不为空)
            params['keyword'] = self.tag
        try:
            res = requests.get(url, params, timeout=5)
            setu_data = res.json()
            status_code = res.status_code
            assert status_code == 200
            self.num_real_api_1 = setu_data['count']  # 实际获取到多少条
            print('从lolicon获取到{0}张setu'.format(setu_data['count']))  # 打印获取到多少条
            for data in setu_data['data']:
                msg = self.build_msg(data['title'], data['pid'], data['author'], data['uid'], data['p'], '无~')
                self.msg.append(msg)
                self.download_url.append(data['url'])
                self.base64_codes.append('')
        except Exception as e:
            print(e)

    def main(self):
        self.api_0()
        if self.num_real < self.num:  # 如果实际数量小于尝试获取的数量
            self.api_1_num = self.num - self.num_real
            self.api_1()
            if self.num_real == 0 and self.num_real_api_1 == 0:  # 2个api都没获取到数据
                q_text.put({'mess': self.msg_in, 'msg': notfound_to_send, 'atuser': 0})
                # freq_group_list[self.msg_in.FromQQG] -= self.num
                return
        for i in range(len(self.msg)):
            # print('进入队列')
            q_pic.put({'mess': self.msg_in, 'msg': self.msg[i], 'download_url': self.download_url[i],
                       'base64code': self.base64_codes[i]})


def send_setu(mess, setu_keyword):
    num = setu_keyword.group(1)  # 提取数量
    tag = setu_keyword.group(2)  # 提取tag
    R18 = setu_keyword.group(3)  # 是否r18
    r18 = random.choices([0, 1], [1, 10], k=1)  # 从普通和性感中二选一
    # ------------------------------------------群聊黑白名单-------------------------------------------------------

    if mess.messtype == 'group':  # 群聊
        if group_blacklist != [] and group_whitelist != []:  # 如果群黑白名单中有数据
            if mess.FromQQG in group_blacklist:  # 如果在黑名单直接返回
                return
            if mess.FromQQG not in group_whitelist and group_whitelist != []:  # 如果不在白名单里,且白名单不为空,直接返回
                return
        if R18 != '':
            if mess.FromQQG in group_r18_whitelist:
                r18 = 2
            else:
                q_text.put({'mess': mess, 'msg': '本群未开启r18~', 'atuser': 0})
                return
    # ------------------------------------------临时会话黑白名单----------------------------------------------

    elif mess.messtype == 'private' and mess.FromQQG != 0:  # 临时会话
        if private_for_group_blacklist != [] and private_for_group_whitelist != []:  # 是临时会话且黑白名单中有数据
            if mess.FromQQG in private_for_group_blacklist:  # 如果在黑名单直接返回
                return
            if mess.FromQQG not in private_for_group_whitelist and private_for_group_whitelist != []:  # 如果不在白名单里,且白名单不为空,直接返回
                return
        if R18 != '':
            if mess.FromQQG in private_for_group_r18_whitelist:
                r18 = 2
            else:
                q_text.put({'mess': mess, 'msg': '本群未开启r18~', 'atuser': 0})
                return
    elif mess.FromQQG == 0 and R18 !='':  # 好友会话
        r18 = 2

    # 阿巴阿巴阿巴阿巴阿巴阿巴--------------------num部分----------------------------------------------------
    if num != '':  # 如果指定了色图数量
        try:  # 将str转换成int
            num = int(num)
            if num > setu_threshold:  # 如果指定数量超过设定值就返回指定消息
                # send_text(mess, threshold_to_send)
                q_text.put({'mess': mess, 'msg': threshold_to_send, 'atuser': 0})
                return
            if num <= 0:
                q_text.put({'mess': mess, 'msg': '¿', 'atuser': 0})
                # send_text(mess, '¿')
                return
        except:  # 如果失败了就说明不是整数数字
            # send_text(mess, wrong_input_to_send)
            q_text.put({'mess': mess, 'msg': wrong_input_to_send, 'atuser': 0})
            return
    else:  # 没指定的话默认是1
        num = 1
    # -----------------------------频率控制--------------------------------------------------------
    try:
        if mess.messtype == 'group':  # 只控制群聊
            if str(mess.FromQQG) not in frequency_additional.keys() and frequency != 0:  # 非自定义频率的群且限制不为0
                if (num + int(freq_group_list[mess.FromQQG])) > int(frequency) or (num > frequency):  # 大于限制频率
                    q_text.put(
                        {'mess': mess,
                         'msg': frequency_cap_to_send.format(reset_freq_time=reset_freq_time, frequency=int(frequency),
                                                             num=int(freq_group_list[
                                                                         mess.FromQQG]), refresh_time=round(
                                 reset_freq_time - (time.time() - time_tmp))),
                         'atuser': 0})
                    return
                freq_group_list[mess.FromQQG] += num  # 计数
            else:
                if int(frequency_additional[str(mess.FromQQG)]):  # 如果自定义频率不为0
                    if num + int(freq_group_list[mess.FromQQG]) > int(frequency_additional[str(mess.FromQQG)]) or (
                            num > int(frequency_additional[str(mess.FromQQG)])):  # 大于限制频率
                        q_text.put({'mess': mess,
                                    'msg': frequency_cap_to_send.format(reset_freq_time=reset_freq_time, frequency=int(
                                        frequency_additional[str(mess.FromQQG)]),
                                                                        num=int(freq_group_list[mess.FromQQG]),
                                                                        refresh_time=round(
                                                                            reset_freq_time - (
                                                                                    time.time() - time_tmp))),
                                    'atuser': 0})
                        return
                    freq_group_list[mess.FromQQG] += num
    except:
        freq_group_list[mess.FromQQG] = num
    # --------------------------------------------------------------------------------------------------
    if before_setu_to_send_switch:
        q_text.put({'mess': mess, 'msg': before_setu_to_send, 'atuser': 0})
    setu = Setu(mess, tag, num, r18)
    setu.main()


def greet(mess, flag):
    if flag:  # morning
        conf = morning_conf
        list_tmp = morning_list
        repeat_msg = morning_repeat
        num_msg_tmp = morning_num_msg
    else:
        conf = night_conf
        list_tmp = night_list
        repeat_msg = night_repeat
        num_msg_tmp = night_num_msg
    try:  # 计数
        if mess.FromQQ in list_tmp[mess.FromQQG]:  # 判断重复
            q_text.put({'mess': mess, 'msg': repeat_msg, 'atuser': 0})
            return
        list_tmp[mess.FromQQG].append(mess.FromQQ)
    except:
        list_tmp[mess.FromQQG] = [mess.FromQQ]  # 出错就说明没有这个群,添加
    num_msg = num_msg_tmp.format(num=len(list_tmp[mess.FromQQG]))
    now_time = datetime.datetime.now()  # 获取当前时间
    for msg, time_range in conf.items():
        d_time = datetime.datetime.strptime(str(now_time.date()) + time_range[0], '%Y-%m-%d%H:%M')
        d_time1 = datetime.datetime.strptime(str(now_time.date()) + time_range[1], '%Y-%m-%d%H:%M')
        if d_time > d_time1:  # 如果前面的时间大于后面的就加一天
            d_time1 = datetime.datetime.strptime(
                str((now_time + datetime.timedelta(days=1)).date()) + time_range[1], '%Y-%m-%d%H:%M')
        if d_time <= now_time < d_time1:
            q_text.put({'mess': mess, 'msg': num_msg + msg, 'atuser': 0})
            return
    q_text.put({'mess': mess, 'msg': '未匹配到时间~~', 'atuser': 0})
    return


def judgment_delay(new_group, group, time_old):  # 判断延时
    if new_group != group or time.time() - time_old >= 1.1:
        # print('{}:不延时~~~~~~~~'.format(new_group))
        return
    else:
        # print('{}:延时~~~~~~~~'.format(new_group))
        time.sleep(1.1)
        return


def sendpic_queue():
    sent_group = {'time': time.time(), 'group': 0}
    while True:
        data = q_pic.get()  # 从队列取出数据
        judgment_delay(data['mess'].FromQQG, sent_group['group'], sent_group['time'])
        send_pic(data['mess'], data['msg'], 0, data['download_url'], data['base64code'])  # 等待完成
        q_pic.task_done()
        sent_group['time'] = time.time()
        sent_group['group'] = data['mess'].FromQQG


def sendtext_queue():
    sent_group = {'time': time.time(), 'group': 0}
    while True:
        data = q_text.get()
        judgment_delay(data['mess'].FromQQG, sent_group['group'], sent_group['time'])
        send_text(data['mess'], data['msg'], data['atuser'])
        q_text.task_done()
        sent_group['time'] = time.time()
        sent_group['group'] = data['mess'].FromQQG


def base2_64(filename):
    with open(filename, 'rb') as f:
        coding = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
        print('本地base64转码~')
        return coding.decode()



def heartbeat():  # 定时获取QQ连接,偶尔会突然断开
    # while True:
    #     time.sleep(60)
    for botqq in botqqs:
        sio.emit('GetWebConn', str(botqq))  # 取得当前已经登录的QQ链接


def withdraw_queue():  # 撤回队列
    while True:
        data = q_withdraw.get()
        # withdraw_message(data['mess'])
        t = threading.Thread(target=withdraw_message,
                             args=(data['mess'],))
        t.start()
        q_withdraw.task_done()


def sentlist_clear():  # 重置发送列表
    # while True:
    #     time.sleep(clear_sentlist_time)
    sent_list.clear()


def reset_freq_group_list():  # 重置时间
    global time_tmp
    if reset_freq_time:
        # time.sleep(reset_freq_time)
        for key in freq_group_list.keys():
            freq_group_list[key] = 0
        time_tmp = time.time()


def rest_greet_list():
    morning_list.clear()
    night_list.clear()


def run_all_schedule():
    while True:
        schedule.run_pending()
        time.sleep(0.5)


@sio.event
def connect():
    time.sleep(1)  # 等1s,不然可能连不上
    for botqq in botqqs:
        sio.emit('GetWebConn', str(botqq))  # 取得当前已经登录的QQ链接
    print('连接成功')


@sio.event
def OnGroupMsgs(message):
    # print(message)
    a = GMess(message)
    cnsql = qqmoudule.mysql_cn.cn_sql()
    qbcs = cnsql.set_sql("select 厂商 from tb_tmp1;")
    qbcm = cnsql.set_sql("select 船只中文翻译 from sc.tb_tmp1;")
    now_time = datetime.datetime.now().strftime('%H%M')
    setu_keyword = setu_pattern.match(a.Content)
    if setu_keyword:
        send_setu(a, setu_keyword)
        return
    # -----------------------------------------------------
    #if a.Content == '服务器状态':
    #    test_yz_msg = pc_linux.mssg()
    #    q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
    #    pc_linux.get_image()
    #    q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://127.0.0.1:18000/cdn/pic/getimg.png',
    #                'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
    #    returna
    if a.Content == '舰船价格查询':
        msg = ["请输入要查询的厂商中文名称:\n圣盾(Aegis Dynamics)\n铁砧航空(Anvil Aerospace)\n十字军工业(Crusader Industries)\n联合外域(Consolidated Outland)\n锡安(Aopoa)\n埃斯佩利亚(Esperia)\n武藏工业(Musashi Industrial & Starflight Concern)\n粪车(Tumbril)\n南船航空(ARGO Astronautics)\n灰猫工业(Greycat Industrial)\n起源悦动(Origin Jumpworks GmbH)\n宛剫尔(Vanduul)\n巴奴(Banu)\n德雷克星际(Drake Interplanetary)\n克鲁格星际(Kruger Intergalactic)\n罗伯茨航天工业(Roberts Space Industries)\n\n\n[[详细厂商查询输入例:查询圣盾]]"]
        for i in msg:
            q_text.put({'mess': a, 'msg': i, 'atuser': 0})
        return
        if a.Content == '查询圣盾':
            msg = ["圣盾厂商船只简要价格表\n锤头鲨\n当前现金价格:$725 游戏币价格:12459900\n当前状态:可飞\n\n\ntest\n\n\n[[详细船只查询输入例:锤头鲨详情]]"]
            for i in msg:
                      q_text.put({'mess': a, 'msg': i, 'atuser': 0})
            return

    if a.At_Content == '舰船查询':
        sqls = cnsql.set_sql("select 厂商 from tb_tmp1;")
        xinxi = ("\n".join(sqls))
        msg = ("船只厂商信息如下: \n%s\n\n查询案例,@我,输入: 圣盾" % (xinxi))
        q_text.put({'mess': a, 'msg': msg, 'atuser': 0})

    if a.At_Content in qbcs:
        sqls = cnsql.set_sql("select 船只中文翻译 from tb_tmp1 where 厂商 = '%s'" % (a.At_Content))
        xinxi = ("\n".join(sqls))
        msg = ("该厂商下舰船全部信息如下：\n%s\n查询案例,@我,输入: 锤头鲨" % xinxi)
        q_text.put({'mess': a, 'msg': msg, 'atuser': 0})
    if a.Content == '网易云' or a.Content == '网抑云' or a.Content == '到点了上号':
        msg = random.choice(['生而为人 我很抱歉', '你只知道她的左口袋里放着糖，不知道她的右口袋里放着刀和耳机。', '口袋里藏着把戏.袖子里藏着花招','温柔吗？半条命换得','小生不才，未得姑娘青睐，扰姑娘良久，姑娘勿怪，自此所有爱慕之意止于唇齿，匿与年华，姑娘往南走，小生往北瞧，不再打扰姑娘，今生就此别过，望姑娘日后善其身，遇良人予君欢喜城，暖色浮余生。','你的一生，我只借一程。从此我好好走，你慢慢来，我们都别回头。','上帝很有意思 猫喜欢吃鱼 猫缺不能下水 鱼喜欢吃蚯蚓 鱼缺不能上岸 你喜欢他 他缺不喜欢你 人啊 总喜欢自己没有的东西 其实猫吃老鼠也很香 鱼吃虾也很快活 你不去爱他 也能够很幸福 可是猫最爱吃的还是鱼 鱼最爱吃的还是蚯蚓 你最爱的 还是他','枕头里藏满了发霉的梦\n梦里注满了无法拥抱的人','一个人 一座城 一生心疼','药好贵啊，西酞普兰118，舍曲林92，帕罗西汀262。真希望有一天喝药的时候，有一个人能给我喂颗糖，真的好苦，不想喝下去了。','一个女孩让我帮她寄快递，给了我一个空纸箱，让我打包。我好奇的问她：这是寄给谁的？\n她说：我喜欢很久的一个男生\n我懵了一下：可是，里面没有东西啊\n她说：有些东西只有我自己能看见\n我一听更有趣了，神秘的问她：到底是什么\n她说：一箱情愿','现在北京时间7：28，我家傻丫头还在睡觉，听着她睡觉的呼吸声，特别安稳，很庆幸我能做到让她有安全感；我在努力，不让她受伤难过委屈，但是老惹她生气嘿嘿；不知道我还能活多久，胃癌晚期嘛，我爱她，真的很爱很爱很爱，所以很珍惜一起相处的时光；她那么可爱，想想听不到她声音了就想哭……','本来带了一群兄弟想去砸场子的，可是看到了她穿着婚纱，特别特别漂亮。','高中时迟到必须罚唱一首歌，为了唱这首歌给那个女孩听，我故意迟到过','14岁，“妈我有女朋友了。”“太小，分了” 16岁，“妈我有女朋友了。”“不行，分了。” 18岁，“妈我有女朋友了。”“高考，分了。” 24岁，“妈我有女朋友了。”“在一起多久了？” “十年” 刚好遇见你，留下足迹才美丽','2016年2月11日消息：台南地震寻获情侣遗体，两人紧紧环抱，男友双手环抱女友、拱起双肩紧紧护住，搜救人员一度无法将两人分开，忍不住鼻酸说：“你已经尽力保护她了！”看着相片中他们幸福的眼睛，一瞬间就想起了这里面的一句话：如果转换了时空身份和姓名，但愿认得你眼睛。','哪有不分手的恋爱啊，只有不伤手的立白','再理性的分析爱情，到最后不都是奋不顾身吗？','一直怀念高中和同桌没被捅破的爱情，28岁还没谈过恋爱，父母到处为我安排相亲。跑去看到女孩竟然就是高中同桌。我激动的脑子发热，开口就问：谈吗？女孩：谈！我又问：订婚？女孩：订！双方父母目瞪口呆，沉默了很久。相亲宴就在这四句话六个字之后变成了订婚宴','我是个俗气至顶的人，见山是山，见海是海，见花便是花。唯独见了你，云海开始翻涌，江潮开始澎湃，昆虫的小触须挠着全世界的痒。你无需开口，我和天地万物便通通奔向你。','你爱过一个人吗？从满心欢喜到满目疮痍······','考研可能也失败了，妈妈明天因为心脏有问题要去看，继父不管，我亲爹关机不敢接我电话，那些亲人除了我阿姨在为我们东奔西跑，我才23岁了我承受了那么多，听着这首歌会哭的','重度抑郁啦，不能给家里添麻烦，不买药啦，自己百度怎么缓解情绪。不告诉朋友啦，因为无从开口，平时我都是逗他们开心的。不告诉男朋友啦，怕他害怕，找个机会提分手叭。我一直在努力治愈自己，努力给别人温暖，我只是有时候坚持不下去，等等我好不好，我擦擦眼泪马上来。'])
        q_text.put({'mess': a, 'msg': msg, 'atuser': 0})
    if a.At_Content in qbcm:
        sqls = cnsql.set_sql("select * from sc.tb_tmp1 where 船只中文翻译 like  '%s'" % (a.At_Content))
        xinxi = cnsql.czgsh(sqls)
        print("select * from sc.tb_tmp1 where 船只中文翻译 like  '%%%s%%'" %a.At_Content)
        msg = ("该船全部信息如下：\n%s" %xinxi)
        q_text.put({'mess': a, 'msg': msg, 'atuser': 0})    

    if a.Content == '服务器状态':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://bot.stisd.cn/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return
    if a.Content == '服务器':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://bot.stisd.cn/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return    
    if a.Content == '萝卜服务器':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://bot.stisd.cn/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return
    if a.Content == '公民服务器':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://bot.stisd.cn/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return
    if a.Content == '锤头鲨详情':
        #test_yz_msg = ["“锤头鲨”是一艘带有多个炮塔的快速巡逻舰，专门用于战斗机，同样适合于支持舰队中的大型主力舰或作为战斗机集团的旗舰。官网价格:$725\n游戏币价格:12459900\n获取方式:舰队周或周年庆开放购买或者客服PY$1325包中也包含锤头鲨,游戏内赫斯顿空港可游戏币购买\n船员:12位\n货仓容量:40\n最大速度:1000\n生命值:60800\n护盾:179868\n常规DPS:14162\n量子燃料:11000\n武器配置\n6个S5可动载人炮台\n24个S4武器槽位\n32枚S3导弹"]

        test_yz_msg = (pc_linux.mssg4())
        q_text.put({'mess': a, 'msg': '正在请求服务器' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://bot.stisd.cn/cdn/pic/chuitou.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/chuitou.png')})
        return
    # -----------------------------------------------------
        # if int(now_time) / 10 == 0:
        #     test_yz_msg = pc_linux.mssg()
        #     q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        #     pc_linux.get_image()
        #     q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://127.0.0.1:18000/cdn/pic/getimg.png',
        #                 'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        #     return
    # -----------------------------------------------------
    if a.Content == 'sysinfo':
        msg = sysinfo()
        q_text.put({'mess': a, 'msg': msg, 'atuser': 0})
        # send_text(a, msg)
        return

    if a.Content == '哲学八连':
        msg = ["ass♂we♂can","boy♂next♂door","酸萝卜♂别吃","deep♂dark♂fantasy","去年勃起♂至今","fa♂q","oh♂yes♂sir"]
        for i in msg:
            q_text.put({'mess': a, 'msg': i, 'atuser': 0})
        return
    if a.Content == 'BOT路线图':
        msg = ["目前可公开的情报:\n服务器状态定时播报:已完成\n舰船价格查询:数据库编写中(优先级较高)\n服务器查询语句模糊匹配:编写中\n服务器状态突发播报:构思中\n服务器状态变化播报:构思中"]
        for i in msg:
            q_text.put({'mess': a, 'msg': i, 'atuser': 0})
        return
    #if a.Content == '锤头鲨详情':
    #    msg = ["“锤头鲨”是一艘带有多个炮塔的快速巡逻舰，专门用于战斗机，同样适合于支持舰队中的大型主力舰或作为战斗机集团的旗舰。官网价格:$725\n游戏币价格:12459900\n获取方式:舰队周或周年庆开放购买或者客服PY$1325包中也包含锤头鲨,游戏内赫斯顿空港可游戏币购买\n船员:12位\n货仓容量:40\n最大速度:1000\n生命值:60800\n护盾:179868\n常规DPS:14162\n量子燃料:11000\n武器配置\n6个S5可动载人炮台\n24个S4武器槽位\n32枚S3导弹"]
    #    for i in msg:
    #        q_text.put({'mess': a, 'msg': i, 'atuser': 0})
    #    return
    # -----------------------------------------------------

    #if a.Content == 's1mple不敢啥了':
    #    msg = ["他再也不敢拿切了辣椒的手摸JB了"]
    #    for i in msg:
    #        q_text.put({'mess': a, 'msg': i, 'atuser': 0})
    #    return
    #if a.Content == 'lie':
    #    msg = ["lie TMD没JB"]
    #    for i in msg:
     #       q_text.put({'mess': a, 'msg': i, 'atuser': 0})
     #   return
    if a.Content == '公民服务器':
        test_se_msg = pc.mssg()
        q_text.put({'mess': a, 'msg': test_se_msg , 'atuser': 0})
        return
    if a.Content == '星际三连':
        msg = ["这是什么游戏?手机能玩吗?在哪里下载?"]
        for i in msg:
            q_text.put({'mess': a, 'msg': i, 'atuser': 0})
        return
    if a.Content == '劝退三连':
        msg = ["传销理财软件,穷逼没事别问,花钱就能下载"]
        for i in msg:
            q_text.put({'mess': a, 'msg': i, 'atuser': 0})
        return

    #if re.search("服务器..?",a.Content):
    #    test_sg_msg = pc.mssg()
    #    q_text.put({'mess': a, 'msg': test_sg_msg , 'atuser': 0})
    #return
    # -----------------------------------------------------
    # -----------------------------------------------------
    if RevokeMsg and a.MsgType == 'AtMsg' and (a.FromQQ in botqqs) and a.FromQQ == a.CurrentQQ:  # 是机器人发的就撤回
        # print(a.MsgSeq,a.MsgRandom)
        q_withdraw.put({'mess': a})
        return
    # -----------------------------------------------------
    if a.Content in morning_keyword and good_morning:
        greet(a, 1)
        return
    # -----------------------------------------------------
    if a.Content in night_keyword and good_night:
        greet(a, 0)
        return


@sio.event
def OnFriendMsgs(message):
    a = Mess(message)
    setu_keyword = setu_pattern.match(a.Content)
    if setu_keyword:
        send_setu(a, setu_keyword)
        return
    # -----------------------------------------------------
    #if a.Content == '服务器状态':
    #    test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
    #    q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
    #    pc_linux.get_image()
    #    q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://127.0.0.1:18000/cdn/pic/getimg.png',
    #                'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
    if a.Content == '服务器状态':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://127.0.0.1:18000/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return
    if a.Content == '服务器':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://127.0.0.1:18000/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return    
    if a.Content == '萝卜服务器':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://127.0.0.1:18000/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return
    if a.Content == '公民服务器':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://127.0.0.1:18000/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return
    if a.Content == '星际服务器':
        test_yz_msg = (pc_linux.mssg1() + "\n" + pc_linux.mssg2() + "\n" + pc_linux.mssg3())
        q_text.put({'mess': a, 'msg': '正在获取服务器信息。。。' , 'atuser': 0})
        pc_linux.get_image()
        q_pic.put({'mess': a, 'msg': test_yz_msg, 'download_url': 'http://127.0.0.1:18000/cdn/pic/getimg.png',
                    'base64code': base2_64('/IOTQQ-color_pic-master/pic/getimg.png')})
        return
    # -----------------------------------------------------
    if a.Content == 'sysinfo':
        msg = sysinfo()
        # send_text(a, msg)
        q_text.put({'mess': a, 'msg': msg, 'atuser': 0})
        return
    # -----------------------------------------------------
    if a.Content == '哲学八连':
        msg = ["ass♂we♂can","boy♂next♂door","酸萝卜♂别吃","deep♂dark♂fantasy","去年勃起♂至今","fa♂q","oh♂yes♂sir"]
        for i in msg:
            q_text.put({'mess': a, 'msg': i, 'atuser': 0})
        return
    if a.Content == '星际三连':
        msg = ["这是什么游戏?","手机能玩吗?","在哪里下载?"]
       	for i in msg:
            q_text.put({'mess': a, 'msg': i, 'atuser': 0})
        return
    if a.Content == '劝退三连':
        msg = ["传销理财软件","穷逼没事别问","花钱就能下载"]
        for i in msg:
            q_text.put({'mess': a, 'msg': i, 'atuser': 0})
        return

    # -----------------------------------------------------
    if a.Content == '报告宇宙状态':
        test_yz_msg = pc.mssg()
        q_text.put({'mess': a, 'msg': test_yz_msg , 'atuser': 0})
    return
    if a.Content == '星际公民服务器':
        test_sd_msg = pc.mssg()
        q_text.put({'mess': a, 'msg': test_sd_msg , 'atuser': 0})
        return
    if a.Content == '公民服务器':
        test_se_msg = pc.mssg()
        q_text.put({'mess': a, 'msg': test_se_msg , 'atuser': 0})
        return
    if a.Content == '报告服务器状态':
        test_sg_msg = pc.mssg()
        q_text.put({'mess': a, 'msg': test_sg_msg , 'atuser': 0})
        return


@sio.event
def OnEvents(message):
    ''' 监听相关事件'''
    # print(message)


if __name__ == '__main__':
    try:
        sio.connect(webapi, transports=['websocket'])
        # beat = threading.Thread(target=heartbeat)  # 保持连接
        text_queue = threading.Thread(target=sendtext_queue)  # 文字消息队列
        pic_queue = threading.Thread(target=sendpic_queue)  # 图片息队列
        withdrawqueue = threading.Thread(target=withdraw_queue)  # 撤回队列
        # sent_list_clear = threading.Thread(target=sentlist_clear)  # 定时清除发生过的列表
        # reset_freq_grouplist = threading.Thread(target=reset_freq_group_list)  # 定时清除发生过的列表
        # beat.start()
        text_queue.start()
        pic_queue.start()
        withdrawqueue.start()
        # sent_list_clear.start()
        # reset_freq_grouplist.start()
        schedule.every(reset_freq_time).seconds.do(reset_freq_group_list)
        schedule.every(clear_sentlist_time).seconds.do(sentlist_clear)  # 定时清除发生过的列表
        schedule.every(60).seconds.do(heartbeat)
        schedule.every().day.at("00:00").do(rest_greet_list)  # 0点刷新
        all_schedule = threading.Thread(target=run_all_schedule)  # 定时清除发生过的列表
        all_schedule.start()
        sio.wait()
    except BaseException as e:
        print(e)
