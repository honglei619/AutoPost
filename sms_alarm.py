#!/usr/bin/python
#coding=utf-8
#FileName: sms_alarm.py V1.0
'''
2012-07-31   修改content 编码格式由原来的UTF-8修改为gb2312以使发送邮件内容支持中文
'''
import smtplib
import sys
import email

from email.mime.text import MIMEText
#========================================
#需要配置
send_mail_host="smtp.126.com"      # 发送的smtp
send_mail_user="username"
send_mail_user_name="system_alarm"
send_mail_pswd="password"
send_mail_postfix="126.com"  #发邮件的域名

get_mail_user="PhoneNum"

#以下不用配置=============================

get_mail_postfix="139.com"
get_mail_host="pop.139.com"


#========================================
def send_mail(sub,content): 
    '''
    sub:主题
    content:内容
    send_mail("xxxxx@xxx.xxx","主题","内容")
    '''
    send_mail_address=send_mail_user_name+"<"+send_mail_user+"@"+send_mail_postfix+">"
    msg=email.mime.text.MIMEText(content,_subtype="html",_charset="gb2312")
    msg['Subject']=sub
    msg['From']=send_mail_address
    msg['to']=to_adress="139SMSserver<"+get_mail_user+"@"+get_mail_postfix+">"
    try:
        stp = smtplib.SMTP()
        stp.connect(send_mail_host)
        stp.login(send_mail_user,send_mail_pswd)
        stp.sendmail(send_mail_address, to_adress, msg.as_string())
        stp.close()
        return True
    except Exception, e:
        print str(e)
        return False


if __name__ == '__main__':
    if send_mail('sub',content):
        print "发送成功"
    else:
        print "发送失败"


