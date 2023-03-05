import sys, time, traceback, datetime, random, requests, cache
from pbf import PBF
from utils.RegCmd import RegCmd
from statement.TextStatement import TextStatement
from statement.AtStatement import AtStatement
from statement.FaceStatement import FaceStatement
from menu import Menu
from PbfStruct import yamldata
from banwords import BanWords

_name = "基础插件"
_version = "1.0.0"
_description = "机器人基础插件"
_author = "xzyStudio"
_cost = 0.00
_markdown = '''
# basic
pigBotFrameworkPlugin

# 基础插件
功能：基础功能

# 作者
- XzyStudio猪比作者
'''

class basic(PBF):
    def __enter__(self):
        return [
            RegCmd(
                name = "群聊设置",
                usage = "群聊设置",
                alias = ["设置列表"],
                permission = "anyone",
                function = "basic@printConfig",
                description = "查看群聊的设置",
                mode = "群聊管理",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "菜单",
                usage = "菜单",
                alias = ["help", "帮助"],
                permission = "anyone",
                function = "basic@menu",
                description = "查看所有指令",
                mode = "只因器人",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "func ",
                usage = "func <要执行的语句>",
                permission = "xzy",
                function = "basic@runFunc",
                description = "执行语句",
                mode = "只因器人",
                isHide = 0,
                type = "command"
            ),
            RegCmd(
                name = "回复|",
                usage = "见机器人的私聊提示",
                permission = "owner",
                function = "basic@replyPM",
                description = "回复私聊消息",
                mode = "只因器人",
                hidden = 1,
                type = "command"
            ),
            RegCmd(
                name = "指令帮助 ",
                usage = "指令帮助 <指令内容>",
                permission = "anyone",
                function = "basic@commandhelp",
                description = "查看指令帮助",
                mode = "只因器人",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "转图片 ",
                usage = "转图片 <消息内容>",
                permission = "owner",
                function = "basic@sendImage",
                description = "将文字转为图片",
                mode = "实用功能",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "chatgpt ",
                usage = "chatgpt <内容>",
                permission = "anyone",
                function = "basic@chatgpt",
                description = "chatgpt",
                mode = "ChatGPT",
                hidden = 0,
                type = "command"
            ),
            RegCmd(
                name = "人机验证 ",
                usage = "见提示",
                permission = "anyone",
                function = "basic@increaseVerifyCommand",
                description = "入群人机验证",
                mode = "群聊管理",
                hidden = 1,
                type = "command"
            ),
            RegCmd(
                name = "Request上报基本功能",
                usage = "",
                permission = "anyone",
                function = "basic@requestListener",
                description = "监听request事件",
                mode = "只因器人",
                hidden = 1,
                type = "request"
            ),
            RegCmd(
                name = "Notice上报基本功能",
                usage = "",
                permission = "anyone",
                function = "basic@noticeListener",
                description = "监听notice事件",
                mode = "只因器人",
                hidden = 1,
                type = "notice"
            )
        ]
    
    def menu(self):
        Menu(self.data).sendModedMenu()
    
    def printConfig(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        settings = self.data.groupSettings
        
        messageList = [
            FaceStatement(151),
            TextStatement('本群机器人配置：')
        ]
        for i in cache.get('settingName'):
            if int(i.get('isHide')) == 1:
                continue
            
            messageList.append(TextStatement(' ', 1))
            messageList.append(FaceStatement(54))
            messageList.append(TextStatement(i.get('name')))
            messageList.append(TextStatement('：'))
            messageList.append(TextStatement(i.get('description'), 1))
            messageList.append(TextStatement('    值：'))
            messageList.append(TextStatement(settings.get(i.get('description'))))
            
            if i.get('other') != '':
                messageList.append(TextStatement(' ', 1))
                messageList.append(TextStatement('    描述：'))
                messageList.append(TextStatement(i.get('other')))
        self.client.msg(messageList).send()
    
    def sendImage(self):
        self.client.data.message = self.data.message
        self.client.msg().image()
        
    def runFunc(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        
        if 'runFunc(' in message:
            self.client.msg(
                FaceStatement(189),
                TextStatement('递归警告：禁止在runFunc中调用自己！')
            ).send()
        else:
            try:
                exec(message)
            except Exception as e:
                msg = traceback.format_exc()
                self.client.msg(
                    FaceStatement(189),
                    TextStatement('错误截获\n{0}'.format(msg))
                ).send()
                
    def replyPM(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        uuid = self.data.uuid
        
        message1 = message.split('|')
        userid = message1[0]
        messageid = message1[1]
        message = message1[2]
        
        self.client.msg(Statement('reply', id=messageid), TextStatement(message)).custom(userid)
        self.client.msg(FaceStatement(151), TextStatement('回复成功！')).custom(uid)
        
    def commandhelp(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        message = self.data.message
        print(message)
        
        for i in cache.get('commandListenerList'):
            content = i.name.strip()
            if message==content:
                if i.permission == 'admin' or i.permission == 'ao':
                    promisetext = '管理员'
                elif i.permission == 'owner':
                    promisetext = '我的主人'
                elif i.permission == 'anyone':
                    promisetext = '任何人'
                elif i.permission == 'ro':
                    promisetext = '真正的主人'
                elif i.permission == 'xzy':
                    promisetext = '最高管理员'
                
                alias: str = ''
                for l in i.alias:
                    alias += l + ' '
                
                self.client.msg(
                    FaceStatement(189),
                    TextStatement('指令帮助', 1),
                    FaceStatement(54),
                    TextStatement('指令内容：'),
                    TextStatement(i.name, 1),
                    FaceStatement(54),
                    TextStatement('指令用法：'),
                    TextStatement(i.usage, 1),
                    FaceStatement(54),
                    TextStatement('指令解释：'),
                    TextStatement(i.description, 1),
                    FaceStatement(54),
                    TextStatement('指令权限：'),
                    TextStatement(promisetext, 1),
                    FaceStatement(54),
                    TextStatement('指令分类：'),
                    TextStatement(i.mode, 1),
                    FaceStatement(54),
                    TextStatement('指令别名：'),
                    TextStatement(alias, 1),
                    FaceStatement(54),
                    TextStatement('指令执行：'),
                    TextStatement(i.function)
                ).send()
                return 
        self.client.msg('没有这个指令呢qwq').send()
            
    def requestListener(self):
        se = self.data.se
        botSettings = self.data.botSettings
        uid = se.get('user_id')
        settings = self.data.groupSettings
        gid = se.get('group_id')
        isGlobalBanned = self.data.isGlobalBanned
        
        if se.get('request_type') == 'group':
            if se.get('sub_type') == 'invite' and botSettings.get('autoAcceptGroup') and isGlobalBanned == None:
                # 邀请机器人加群
                print('group invite')
                return '{"approve":true}'
            elif uid == yamldata.get('chat').get('owner'):
                # 最高管理员一律同意
                print('group invite')
                return '{"approve":true}'
            elif settings.get('autoAcceptGroup') != 0 and se.get('sub_type') == 'add':
                # 有人要加群
                print('group add')
                if isGlobalBanned == None:
                    return '{"approve":true}'
                else:
                    self.client.msg(
                        FaceStatement(151),
                        TextStatement(f'已禁止用户{uid}加群', 1),
                        TextStatement(f'原因：{isGlobalBanned.get("reason")}')
                    ).custom(None, gid)
            elif settings.get('autoAcceptGroup') == 0:
                self.client.msg(
                    FaceStatement(151),
                    TextStatement('管理员快来，有人要加群！')
                ).send()
                
        elif se.get('request_type') == 'friend' and botSettings.get('autoAcceptFriend'):
            print('friend')
            if isGlobalBanned == None:
                return '{"approve":true}'
            else:
                self.client.msg(
                    FaceStatement(151),
                    TextStatement(f'已禁止用户{uid}加好友', 1),
                    TextStatement(f'原因：{isGlobalBanned.get("reason")}')
                ).custom(botSettings.get('owner'))
                self.client.msg(
                    FaceStatement(151),
                    TextStatement(f'已禁止用户{uid}加好友', 1),
                    TextStatement(f'原因：{isGlobalBanned.get("reason")}')
                ).custom(botSettings.get('second_owner'))
                
    def noticeListener(self):
        userCoin = self.data.userCoin
        se = self.data.se
        gid = se.get('group_id')
        cid = se.get('channel_id')
        uid = se.get('user_id')
        message = se.get('message')
        settings = self.data.groupSettings
        uuid = self.data.uuid
        botSettings = self.data.botSettings
        
        if se.get('notice_type') == 'group_ban' and se.get('user_id') == se.get('self_id'):
            # 禁言机器人
            self.checkBan()
        
        elif se.get('notice_type') == 'group_recall' and settings.get('recallFlag') != 0 and se.get('operator_id') != botSettings.get('myselfqn') and se.get('user_id') != botSettings.get('myselfqn'):
            # 消息防撤回
            data = self.client.CallApi('get_msg', {"message_id":se.get('message_id')})
            if BanWords(self.data).find(data.get('data').get('message')) == False and 'http' not in data.get('data').get('message'):
                self.client.msg(
                    FaceStatement(54),
                    TextStatement('消息防撤回：', 1),
                    AtStatement(se.get('operator_id')),
                    TextStatement('撤回了'),
                    AtStatement(se.get('user_id')),
                    TextStatement('发送的一条消息', 1),
                    TextStatement('消息内容：'),
                    TextStatement(data.get('data').get('message'))
                ).send()
            else:
                self.client.msg(
                    FaceStatement(54),
                    AtStatement(se.get('operator_id')),
                    TextStatement('撤回了'),
                    AtStatement(se.get('user_id')),
                    TextStatement('发送的一条不可见人的消息')
                ).send()
            
        elif se.get('notice_type') == 'notify':
            # 戳机器人
            if se.get('sub_type') == 'poke' and se.get('target_id') == botSettings.get('myselfqn') and botSettings.get("chuo"):
                chuo = botSettings.get("chuo").split()
                chuoReply = chuo[random.randint(0, len(chuo)-1)]
                self.client.msg(
                    AtStatement(se.get('user_id')),
                    TextStatement(chuoReply)
                ).send()
                
        elif se.get('notice_type') == 'group_increase':
            # 有人进群
            if settings.get('increase') != 0:
                message = f"[CQ:at,qq={se.get('user_id')}] {settings.get('increase_notice')}"
                userdata = self.client.CallApi("get_stranger_info", {'user_id':uid}).get("data")
                replaceList = [
                    ["{user}", uid],
                    ["{userimg}", f"[CQ:image,cache=0,url=http://q1.qlogo.cn/g?b=qq&nk={uid}&s=100,file=http://q1.qlogo.cn/g?b=qq&nk={uid}&s=100]"],
                    ["{username}", userdata.get("nickname")],
                    ["{userlevel}", userdata.get("level")]
                ]
                for i in replaceList:
                    if i[0] in message:
                        message = message.replace(i[0], str(i[1]))
                
                self.client.msg().raw(message)
                if uid == botSettings.get("myselfqn"):
                    self.client.msg().raw("使用提示：机器人有很多功能，而所有这些功能并不一定适用于所有群聊，如果您不想启用某个功能，可以使用指令「修改设置」来更改去群聊设置。\n禁言机器人永远是一个最坏的做法！")
            if settings.get('increase_verify') != 0:
                self.increaseVerify()
            
        elif se.get('notice_type') == 'group_decrease' and settings.get('decrease') != 0:
            # 有人退群
            if se.get('sub_type') == 'leave':
                message = self.data.groupSettings.get("decrease_notice_leave")
                userdata = self.client.CallApi("get_stranger_info", {'user_id':uid}).get("data")
                replaceList = [
                    ["{user}", uid],
                    ["{userimg}", f"[CQ:image,cache=0,url=http://q1.qlogo.cn/g?b=qq&nk={uid}&s=100,file=http://q1.qlogo.cn/g?b=qq&nk={uid}&s=100]"],
                    ["{username}", userdata.get("nickname")],
                    ["{userlevel}", userdata.get("level")]
                ]
                for i in replaceList:
                    if i[0] in message:
                        message = message.replace(i[0], str(i[1]))
                
                self.client.msg().raw(message)
            
            elif 'kick' in se.get('sub_type'):
                message = self.data.groupSettings.get("decrease_notice_kick")
                userdata = self.client.CallApi("get_stranger_info", {'user_id':uid}).get("data")
                replaceList = [
                    ["{user}", uid],
                    ["{userimg}", f"[CQ:image,cache=0,url=http://q1.qlogo.cn/g?b=qq&nk={uid}&s=100,file=http://q1.qlogo.cn/g?b=qq&nk={uid}&s=100]"],
                    ["{username}", userdata.get("nickname")],
                    ["{userlevel}", userdata.get("level")],
                    ["{operator}", se.get("operator")]
                ]
                for i in replaceList:
                    if i[0] in message:
                        message = message.replace(i[0], str(i[1]))
                
                self.client.msg().raw(message)
        
        elif se.get('notice_type') == 'essence':
            # 精华消息
            if se.get('sub_type') == 'add' and settings.get('delete_es') != 0:
                self.client.CallApi('delete_essence_msg', {'message_id':se.get('message_id')})
                self.client.msg(
                    TextStatement('已自动撤回成员'),
                    AtStatement(se.get('sender_id')),
                    TextStatement('设置的精华消息')
                ).send()
            elif se.get('sub_type') == 'delete' and se.get('operator_id') != botSettings.get('myselfqn'):
                data = self.client.CallApi('get_msg', {"message_id":se.get('message_id')})
                
                self.client.msg(
                    TextStatement('很不幸，'),
                    AtStatement(se.get('operator_id')),
                    TextStatement('撤回了一个精华消息', 1),
                    TextStatement(f"消息内容：{data.get('data').get('message')}")
                ).send()
    
    def increaseVerifyCommand(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        for i in range(len(increaseVerifyList)):
            if increaseVerifyList[i].get('uid') == uid and increaseVerifyList[i].get('gid') == gid:
                if increaseVerifyList[i].get('pswd') == self.data.message:
                    increaseVerifyList[i]['pswd'] = None
                else:
                    self.client.msg().raw('你这验证码太假了！')
                break
    
    def increaseVerify(self):
        uid = self.data.se.get('user_id')
        gid = self.data.se.get('group_id')
        pswd = self.generate_code(4)
        limit = self.data.groupSettings.get('increase_verify')
        increaseVerifyList.append({"uid":uid,"gid":gid,"pswd":pswd})
        self.client.msg(
            AtStatement(uid),
            TextStatement(f'请在{limit}秒内发送指令“人机验证 {pswd}”'),
            TextStatement('注意中间有空格！')
        ).send()
        l = 0
        for i in range(len(increaseVerifyList)):
            if increaseVerifyList[i].get('uid') == uid and increaseVerifyList[i].get('gid') == gid:
                l = i
                break
        while limit >= 0:
            if increaseVerifyList[l].get('pswd') == None:
                increaseVerifyList[l]["pswd"] = "continue"
                self.client.msg().raw('[CQ:at,qq={0}] 恭喜，验证通过！'.format(uid))
                increaseVerifyList.pop(l)
                return
            limit -= 1
            time.sleep(1)
        self.client.msg().raw('[CQ:at,qq={0}] 到时间啦，飞机票一张！'.format(uid))
        self.client.CallApi('set_group_kick', {'group_id':gid,'user_id':uid})
        increaseVerifyList.remove(l)
    
    def getVerifyStatus(self):
        for i in range(len(increaseVerifyList)):
            if increaseVerifyList[i].get('uid') == self.data.se.get('user_id') and increaseVerifyList[i].get('gid') == self.data.se.get('group_id'):
                if increaseVerifyList[i]["pswd"] == "continue":
                    return False
                return True
        return False
    
    def checkBan(self):
        if self.data.se.get("sub_type") == "lift_ban":
            # 解禁言
            return 
        
        self.mysql.commonx("UPDATE `botSettings` SET `bannedCount`=%s WHERE `qn`=%s", (int(self.data.groupSettings.get("bannedCount"))+1, self.data.se.get("group_id")))
        
        if int(self.data.groupSettings.get("bannedCount"))+1 >= int(self.data.botSettings.get("bannedCount")):
            # 超过次数，自动退群
            self.client.CallApi('set_group_leave', {"group_id":self.data.se.get("group_id")})
            self.mysql.commonx("UPDATE `botSettings` SET `bannedCount`=0 WHERE `qn`=%s", (self.data.se.get("group_id")))
            if self.data.groupSettings.get("connectQQ"):
                self.client.msg(TextStatement("[自动消息] 请注意，您关联的群组（{}）因违反机器人规定致使机器人退群，您将会承担连带责任".format(self.data.se.get("group_id")))).custom(self.data.groupSettings.get("connectQQ"))
            self.client.msg(TextStatement("[提示] 群：{}\n关联成员：{}\n行为：禁言{}次\n已自动退群".format(self.data.se.get("group_id"), self.data.groupSettings.get("connectQQ"), int(self.data.groupSettings.get("bannedCount"))+1))).custom(self.botSettings.get("owner"))
        
        cache.refreshFromSql('groupSettings')
    
    def chatgpt(self):
        try:
            from PbfStruct import chatbot

            self.send(f"[CQ:reply,id={self.data.se.get('message_id')}] 正在获取...")

            message = ""
            for i in chatbot.ask(self.data.message):
                message = i.get('message')
            
            self.send(f"[CQ:reply,id={self.data.se.get('message_id')}] {message}")
        except Exception as e:
            self.send(f"[CQ:reply,id={self.data.se.get('message_id')}] 发生错误，可能是正在生成回答（同一会话不支持并发）或者请求频率超限！\n具体错误详见日志")
            self.logger.warning(traceback.format_exc())

increaseVerifyList = []