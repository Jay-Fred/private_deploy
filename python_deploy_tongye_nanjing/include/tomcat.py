import os,sys
import datetime,time
import re
import shutil
from env import *

jdk_package = r_soft_dir + "jdk/java.tar.gz"
jdk_dir = midsoft + 'java'
tomcat_package = r_soft_dir + 'tomcat/tomcat.tar.gz'
ipaddr = sys.argv[1]
pyname = os.path.basename(__file__)

################################## 判断jdk环境并安装jdk ##################################
def jdk_install():
    profile_file = '/etc/profile'
    with open(profile_file, 'r', encoding='UTF-8') as f_obj:
        contents = f_obj.read()
        strings = re.search('export JAVA_HOME(.*)', contents)
        if strings:
            pass
        else:
            print(ipaddr + "  开始安装 JDK 环境 " + s(), "\n")
            check_dir(midsoft,jdk_package)
            print('\t',[s()]," 开始解压 "+jdk_package,"\n")
            os.system("tar zxf "+ jdk_package +" -C "+ midsoft)
            profile = '/etc/profile'
            with open('/etc/profile',encoding='UTF-8') as f:
                content = f.read()
                string = re.search('export JAVA_HOME(.*)|export CLASSPATH(.*)',content)
                if string:
                    print('\t',[s()],' JAVA_HOME在/etc/profile中已存在，准备清除. 清除的变量如下：\n\t'+string.group())
                    i = re.sub(r'export JAVA_HOME(.*)|export CLASSPATH(.*)','',content)
                    with open('/etc/profile','w',encoding='UTF-8') as f_obj:
                        f_obj.write(i)
            a = {'/java/bin':''}
            replace(profile,**a)

            with open('/etc/profile','a',encoding='UTF-8') as f_profile:
                f_profile.write("\nexport JAVA_HOME="+midsoft+"java\nexport PATH="+midsoft+"java/bin:$PATH\nexport CLASSPATH=.:"+midsoft+"java/lib/dt.jar:"+midsoft+"java/lib/tools.jar")
            time.sleep(2)
            os.system('source /etc/profile')
            os.system("source ~/.bashrc")
            print('\t',[s()],"  安装 jdk 环境结束 ","\n")

################################## 二进制安装tomcat，并设置环境变量 ##################################
def check_env():
    alert_start(ipaddr, pyname)
    tomcat_package = r_soft_dir + 'tomcat/tomcat.tar.gz'
    check_dir(tomcat_dir, tomcat_package)
    os.system('tar zxf ' + tomcat_package +' -C ' + r_soft_dir + 'tomcat/')
    files = os.listdir(r_soft_dir + 'tomcat/')
    for ips, ap in app_list.items():
        for tom in ap[::-1]:
            for file in files:
                if tom in file and ipaddr == ips:
                    try:
                        shutil.copytree(r_soft_dir + 'tomcat/' + file, tomcat_dir + file)
                    except Exception:
                        pass
    f = open('/etc/profile',encoding='UTF-8')
    content = f.read()
    string = re.search('TOMCAT_HOME',content)
    if string:
        print('\t',[s()],' TOMCAT_HOME在/etc/profile中已存在，准备清除. 清除的变量如下：\n\t'+string.group())
        i = re.sub(r'export TOMCAT_HOME(.*)','',content)
        f = open('/etc/profile','w',encoding='UTF-8')
        f.write(i)
        f.close()
    f.close()
    with open('/etc/profile','a',encoding='UTF-8') as f_obj:
        f_obj.write("\nexport TOMCAT_HOME="+ tomcat_dir)
    os.system('source /etc/profile')
    os.system("source ~/.bashrc")

################################## 修改所有tomcat启动文件中的安装路径 ##################################
def catalina():
    print('\t',[s()],' 修改所有Tomcat安装路径 ','\n')
    dirs = os.listdir(tomcat_dir)
    for dir in dirs:
        try:
            with open(os.path.join(tomcat_dir,dir)+os.sep+'bin/catalina.sh',encoding='UTF-8') as f:
                content = f.read()
                string = re.search('/usr/local/installed',content)
                if string:
                    i = re.sub(r'/usr/local/installed/',tomcat_dir,content)
                    with open(os.path.join(tomcat_dir,dir)+os.sep+'bin/catalina.sh','w',encoding='UTF-8') as f_obj:
                        f_obj.write(i)
        except FileNotFoundError:
            pass

################################## 创建tomcat所需目录 ##################################
def mkdir_dir():
    print('\t',[s()],' 创建所需目录及授权 ','\n')
    for dirs in ['/usr/local/installed/interbank','/usr/local/installed/interbank/ratingReport','/usr/local/installed/interbank/financeExcel','/usr/local/installed/interbank/mybondExcel','/usr/local/installed/interbank/excel','/usr/local/installed/interbank/taskFile','/usr/local/installed/interbank/logo','/usr/local/installed/interbank/batchSaveUserExcel','/usr/local/installed/interbank/ibApiFile','/usr/local/installed/ocx/ocx']:
        try:
            os.system('mkdir -p ' + dirs)
        except Exception:
            pass
    for files in ['/usr/local/installed/interbank','/usr/local/installed/ocx',tomcat_dir + '/tomcat*']:
        os.system('chown -R ' + common_user + ':' + common_user + ' ' + files)

################################## 为tomcat创建开机自启动文件 ##################################
def tomcat_service():
    print('\t',[s()]," 创建tomcat开机自启动文件 ","\n")
    if not os.path.exists(r_service_dir):
        os.system('mkdir -p '+ r_service_dir)
    tomcat_service_file = r_service_dir + 'Tomcat.service'
    list1 = []
    for item in os.listdir(tomcat_dir):
        if item.startswith('tomcat'):
            list1.append(item)
    with open(tomcat_service_file,'w',encoding='UTF-8') as f_obj:
        f_obj.write("#!/bin/bash\n\n#tomcat部署启动顺序流程：\n#1.tomcat-8.0.30-decision-server-8388\n#2.tomcat-8.0.30-interbank-server-8788\n#3.tomcat-8.0.30-interbank-quartz-8988\n#4.tomcat-8.0.30-monitor-server-8188\n#5.tomcat-8.0.30-monitor-web-8288\n#6.tomcat-8.0.30-interbank-client-8888\n#7.tomcat-8.0.30-datatransfer-client-8080\n\n    source /etc/profile\n#启动顺序为\n    tomcat_service=(" + (('%s ' * len(list1)).strip() + ' ') % tuple(list1) + ")\n    for i in ${tomcat_service[@]};do\n    if [ -d /service/$i ];then\n      cd /service;nohup supervise /service/$i >/dev/null 2>&1 &\n      sleep 60\n    fi\ndone\n\nexit 0\n")

################################## 判断tomcat是否开机自启动  ##################################
def boot_up():
    service = 'Tomcat.service'
    bootup(service)
    alert_over(pyname)

################################## 主函数开始  ##################################
def main():
    jdk_install()
    check_env()
    catalina()
    mkdir_dir()
    tomcat_service()
    boot_up()

if __name__ == '__main__':
    main()