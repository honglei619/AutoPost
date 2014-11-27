# -*- coding: cp936 -*-
#自动表单提交:v1.3
#by honglei619#gmail.com 2012-7-14
#v1.5版修订：将所有变量均放到独立的py文件中，方便其他用户修改参数
#2.0版修订：将各个功能函数封装成类，增强代码重用性

'''
v1.0
2012-07-29 添加Alarm_system函数
           功能：当丢包达到用户设定阙值产生短信报警并记录到日志文件
2012-07-30 修改函数Brower(url,user,password)表单提交数据、及insert_page地址
           添加Alarm_system(Inter_loss_persent=3,Mpls_loss_persent=3)函数
           两个网关ping延时参数，默认为3%
2012-07-31 屏蔽Brower()函数中insert_data提交部分参数，detail[id]对于每打开一次网页id均变化，暂时无法确定故暂不提交
           源文件代码中有两个：name参数及id参数，可尝试使用id来提交
           修改Delfile（）函数，将result.txt文件也做清空处理，防止出现总是重复读取历史结果；
           将主函数中Delfile（）函数方法提到最上以供在下次运行之前进行查询；
V1.1
2012-07-31 添加CheckResult(filename, lookup)函数，对提交表单结果进行短信通知
           修改Brower(url,user,password)函数，添加局部变量check_page抓取网页源代码使用
           修改Delfile（）函数，将check.txt文件也做清空处理，防止出现读取历史记录导致功能错乱；
v1.2
2012-08-17 添加random模块，用于设置随机时间种子，使提交表单时间随机，防止出现每日提交时间相似;
v1.3
2012-08-23 修改短信提示参数：将检测结果反馈到短信提示中；
2013-06-14 因表单更改，添加提交表单数据（机房温湿度、UPS、是否漏水等，205-212行）；
'''
import re
import string
import telnetlib
import time
import linecache
import urllib2
import urllib
import cookielib
#插入短信报警函数
from sms_alarm import send_mail
#插入随机模块
import random

#######################################################
def TelnetROS(host,user,password):
    '''
    telnetRos(host,user,password)
    host:ROS主机地址
    user:具备telnet，写权限的ros账号
    password：登陆密码
    '''
    HOST=host
    PORT='23'
    user= user
    password= password
    command_1='ping x.x.x.x c 120'
    command_2='ping x.x.x.x c 120'
    command_3='quit'

    tn=telnetlib.Telnet(HOST,PORT)
    tn = telnetlib.Telnet(HOST)
#输入用户名
    tn.read_until(b"Login: ")
    tn.write(user.encode('UTF-8') + b"\n")
#输入密码
    tn.read_until(b"Password: ")
    tn.write(password.encode('UTF-8') + b"\n")
#执行所设定的命令
    tn.read_until(b'>')
    tn.write(command_1.encode('UTF-8')+b"\r\n")
    time.sleep(120)

    tn.read_until(b'>')
    tn.write(command_2.encode('UTF-8')+b"\r\n")
    time.sleep(120)
#只有执行断开连接命令之后EOF，read_all函数才能抽取所有运行后的结果
    tn.read_until(b'>')
    tn.write(command_3.encode('UTF-8')+b"\r\n")

#执行结果全部写入result.txt文件中
    result=tn.read_all()
    file_object=open('result.txt','wb')
    file_object.write(result)
    file_object.close()
#关闭telnet连接
    tn.close()

##########################################################

def WriteData(filename,num):
    '''
    从result文件中提取带ping的结果两行数据，并写入相应的ping结果文件中以备下面函数调用
    writeData（filename,num）
    filename:写入的文件名称
    num:需要提取结果所在的行数
    '''
    ping=linecache.getline('result.txt',num)
    file_object = open(filename,'a')
    file_object.write(ping)
    file_object.close()

#########################################################
#以读方式打开internet.txt文件
def Strdeal(fileName):
    '''
    读取WriteData函数记录的两行数据，并提取相关参数值赋值给全局变量
    global _loss：数据包丢失数量
    global _min：最小延时
    global _avg：平均延时
    global _max：最大延时
    '''
#定义全局变量
    global _loss
    global _min
    global _avg
    global _max
    file_object=open(fileName,"r")
#读取文件第一行信息
    line=file_object.readline()
#re.search函数会在字符串内查找模式匹配,只到找到第一个匹配然后返回，
#如果字符串没有匹配，则返回None
#取出0%
    loss=re.search(r"[0-9]+%",line).group()
#计算字符串长度
    strlen=len(loss)
#长度为2的时候直接截取第一位，并转换成数字
    if strlen==2:
        _loss=int(loss[0:1])
#长度不为2的时候截取2位，并转换成数字
    else:
        _loss=int(loss[0:2])
#读取文件第二行信息
    line=file_object.readline()
#取出12/12.0/13
    mam=re.search(r"[0-9]+/.*/[0-9]+",line).group()
#分割字符串，分别赋值给变量
    _min,_avg,_max=int(mam.split("/")[0]),float(mam.split("/")[1]),int(mam.split("/")[2])
#返回参数
    return _loss,_min,_avg,_max
#关闭文件
    file_object.close()

#############################################################
def Delfiles():
    '''
    清空存储结果的临时文件，以防止再次运行strdeal函数截取到历史结果
    '''
    file_object=open('internet.txt','w+')
    file_object.write("")
    file_object.close()
    file_object=open('mpls.txt','w+')
    file_object.write("")
    file_object.close()
    file_object=open('result.txt','w+')
    file_object.write("")
    file_object.close()
    file_object=open('check.txt','w+')
    file_object.write("")
    file_object.close()

#############################################################

def Brower(url,user,password):
    '''
    Brower(url,user,password)
    url:表单提交地址；
    user:登陆系统账号；
    password:登陆系统的密码；
    '''
#获取当前日期
    system_day=time.strftime('%Y-%m-%d',time.localtime(time.time()))
#登陆页面提交地址
    login_page = "http://x.x.x.x/itams/index.php/Public/checkLogin"
#更新报表提交地址
    insert_page="http://x.x.x.x/itams/index.php/Dailycheck/insert"
#检查地址
    check_page="http://x.x.x.x/itams/index.php/Dailycheck"
    try:
#获得一个cookieJar实例
        cj = cookielib.CookieJar()
#cookieJar作为参数，获得一个opener的实例
        opener=urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#伪装成一个正常的浏览器，避免有些web服务器拒绝访问。
        opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
#生成Post数据，含有登陆用户名密码。
        data = urllib.urlencode({"username":user,"password":password})
        insert_data=urllib.urlencode([#('undefined','')
#日期参数-必须参数不可缺
('base[areaId]','21')
,('base[createUserId]','117')
,('base[checkDate]',system_day)
,('base[itTeam]','1')
,('base[itTeamMember]','name,')
,('base[asset][nb]','26')
,('base[asset][tpc]','9')
,('base[asset][ser]','2')
,('base[asset][net]','0')
,('base[pingMPLS][sent]','120')
,('base[pingMPLS][lost]',Mpls_loss)
,('base[pingMPLS][max]',Mpls_max)
,('base[pingMPLS][avg]',Mpls_avg)
,('base[pingInternet][sent]','120')
,('base[pingInternet][lost]',Inter_loss)
,('base[pingInternet][max]',Inter_max)
,('base[pingInternet][avg]',Inter_avg)
,('base[tracerouteState]','1')
,('base[localDnsState]','1')
,('base[pingInternet][temperature1]','23')
,('base[pingInternet][humidity1]','22')
,('base[pingInternet][temperature2]','23')
,('base[pingInternet][humidity2]','41')
,('base[pingInternet][temperature3]','41')
,('base[pingInternet][humidity3]','41')
,('base[pingInternet][UPS]','1')
,('base[pingInternet][water]','1')
#detail[id]对于每打开一次网页添加报表id均变化，暂时无法确定故暂不提交
#,('detail[139401][runningState]','1')
#,('detail[139401][logState]','1')
#,('detail[139401][tagState]','1')
#,('detail[139401][dustproofState]','1')
#,('detail[139401][socketState]','1')
#,('detail[139401][cardportState]','1')
#,('detail[139401][remoteState]','1')
,('base[dcState]','1')
,('base[dcToolsState]','1')
,('base[dcLogState]','1')
,('base[dnsServiceState]','1')
,('base[dcMemo]','')
,('base[antivirusServiceState]','1')
,('base[antivirusServiceLogState]','1')
,('base[antivirusServiceUpdateState]','1')
,('base[antivirusMemo]','')
,('base[viaHasNoAgentClient]','1')
,('base[viaNewOrOutdatedUser]','1')
,('base[viaUpdateFilter]','1')
,('base[viaMemo]','')
#修改日检查表所需的插入ID
#,('base[id]','13743')
])
#以post的方法访问登陆页面，访问之后cookieJar会自定保存cookie
        opener.open(login_page,data)
        opener.open(insert_page,insert_data)
        opener.open(check_page,data)
#以带cookie的方式访问页面
        op=opener.open(url)
#读取页面源码
        data= op.read()
        insert_data=op.read()
        return data
        return insert_data
    except Exception,e:
        print str(e)

##################################################
def Alarm_system(Inter_loss_persent=3,Mpls_loss_persent=3):
    '''
    alarm_system(Inter_loss_persent=3,Mpls_loss_persent=3):
    Inter_loss_persent:数据包丢失百分比短信报警阙值,默认为3%即丢失4个包发送报警消息
    '''
    system_data=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
    if (Inter_loss>Inter_loss_persent):
        send_mail('Inter_Error',post_inter_err)
        file_object=open('log.txt','a')
        file_object.write(system_data)
        file_object.write(',Alarm,Internet ping loss too much,pls check out!\n')
        file_object.close()
    if (Mpls_loss>Mpls_loss_persent):
        send_mail('Mpls_Error',post_mpls_err)
        file_object=open('log.txt','a')
        file_object.write(system_data)
        file_object.write(',Alarm,Mpls ping loss too much,pls check out!\n')
        file_object.close()

def CheckResult(filename, lookup):
    with open(filename, 'rt') as handle:
        for ln in handle:
            if lookup in ln:
                return True
        else:
           return False



if __name__=='__main__':
#清空历史文件记录
    Delfiles()
#telnet ros
    TelnetROS('x.x.x.x','test','test')
#记录internet结果
    f=WriteData('internet.txt',123)
    f=WriteData('internet.txt',124)
#记录mpls结果
    f=WriteData('mpls.txt',253)
    f=WriteData('mpls.txt',254)
#返回ping结果并赋值
    Strdeal('internet.txt')
    Inter_loss = _loss
    #Inter_min = _min
    Inter_avg = _avg
    Inter_max = _max
    Inter_temp=[' 互联网丢包: ',Inter_loss,'%互联网平均延时: ',Inter_avg,'ms互联网最大延时:',Inter_max]
    Inter_temp[1]=Inter_loss
    Inter_temp[3]=Inter_avg
    Inter_temp[5]=Inter_max
    Inter_post=str(Inter_temp[0])+str(Inter_temp[1])+str(Inter_temp[2])+str(Inter_temp[3])+str(Inter_temp[4])+str(Inter_temp[5])
    Strdeal('mpls.txt')
    Mpls_loss = _loss
    #Mpls_min = _min
    Mpls_avg = _avg
    Mpls_max = _max
    #拼接
    Mpls_temp=['专线丢包:',Mpls_loss,'%专线平均延时:',Mpls_avg,'ms专线最大延时：',Mpls_max]
    Mpls_temp[1]=Mpls_loss
    Mpls_temp[3]=Mpls_avg
    Mpls_temp[5]=Mpls_max
    Mpls_post=str(Mpls_temp[0])+str(Mpls_temp[1])+str(Mpls_temp[2])+str(Mpls_temp[3])+str(Mpls_temp[4])+str(Mpls_temp[5])
    post_success=str('日检查表提交成功----- ')+str(Inter_post)+str('ms')+str(Mpls_post)+str('ms')
    post_inter_err=str('互联网丢包严重----- ')+str(Inter_post)+str('ms')
    post_mpls_err =str('专线丢包严重----- ')+str(Mpls_post)+str('ms')

#报警函数
    Alarm_system()
#设置随机休眠时间
    sleep_time = random.randint(100,600)
    time.sleep(sleep_time)
#POST表单
    Brower("http://x.x.x.x/itams/index.php/Dailycheck/","username","password")
#检查表单是否提交成功
    check=Brower("http://x.x.x.x/itams/index.php/Dailycheck/","username","password")
    file_object=open('check.txt','w+')
    file_object.write(check)
    file_object.close()
#将网页源码保存为check.txt文件，然后在此文件查找本日日期，找到返回true
    system_day=time.strftime('%Y-%m-%d',time.localtime(time.time()))
    print system_day
    if CheckResult('check.txt',system_day)==True:
        send_mail("Success",post_success)
    else:
        send_mail("failure","杯具！系统自动提交日检查表失败，请登陆系统手动提交！")
