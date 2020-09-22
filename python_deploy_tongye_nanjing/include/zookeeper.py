import os
import datetime,time
import re
import sys
import socket
import fcntl
import struct
from env import *

################################## 定义安装zookeeper所需软件包及安装目录 ##################################
jdk_package = r_soft_dir + "jdk/java.tar.gz"
jdk_dir = midsoft + 'java'
zk_data = midsoft + "zookeeper/data"
zk_logs = midsoft + "zookeeper/logs"
zk_dir = midsoft + 'zookeeper'
zk_package =  r_soft_dir +  "zookeeper/zookeeper.tar.gz"
zk_conf = midsoft + "zookeeper/conf/zoo.cfg"
zk_myid = midsoft + 'zookeeper/data/myid'
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
            print('\t',[s()], "  安装 jdk 环境结束","\n")

################################## 根据配置文件判断zookeeper是否为单机版或集群版 ##################################
def zk_install():
    i = 0
    for key,value in app_list.items():
        word = re.findall("zookeeper(.*)",str(value))
        leng = len(word)
        i += leng
    if i>=2:
        alert_start(ipaddr, pyname)
        print('\t',[s()]," 开始安装zookeeper集群版 ",'\n')
        zookeeper_profile()
        zookeeper_cfg()
        zk_config()
        zk_service()
        zookeeper_service()
    else:
        alert_start(ipaddr, pyname)
        print('\t',[s()]," 开始安装zookeeper单机版 ",'\n')
        zookeeper_profile()
        zookeeper_cfg()
        zookeeper_start()
        zookeeper_service()

################################## 二进制安装zookeeper，设置环境变量 ##################################
def zookeeper_profile():
    print('\t',[s()],' 添加环境变量 ','\n')
    check_dir(midsoft,zk_package)
    os.system("tar zxf "+ zk_package +" -C "+ midsoft)
    profile = '/etc/profile'
    with open('/etc/profile',encoding='UTF-8') as f_pro:
        content = f_pro.read()
        string = re.search('export ZOOKEEPER_HOME(.*)',content)
        if string:
            print('\t',[s()],' ZOOKEEPER_HOME在/etc/profile中已存在，准备清除. 清除的变量如下：\n\t'+string.group())
            i = re.sub(r'export ZOOKEEPER_HOME(.*)','',content)
            with open('/etc/profile','w',encoding='UTF-8') as f_obj:
                f_obj.write(i)
    b = {'/zookeeper/bin':''}
    replace(profile,**b)
    with open('/etc/profile','a',encoding='UTF-8') as f_profile:
        f_profile.write("\nexport ZOOKEEPER_HOME="+midsoft+"zookeeper\nexport PATH="+midsoft+"zookeeper/bin:$PATH\n")
    os.system('source /etc/profile')
    os.system("source ~/.bashrc")

################################## 修改zookeeper数据目录和日志目录 ##################################
def zookeeper_cfg():
    print('\t',[s()],' 修改zookeeper数据目录和日志目录 ','\n')
    with open(zk_conf,encoding='UTF-8') as f_zkconf:
        content = f_zkconf.read()
        string = re.search('dataDir(.*)|dataLogDir(.*)',content)
        if string:
            i = re.sub(r'dataDir(.*)|dataLogDir(.*)','',content)
            with open(zk_conf,'w',encoding='UTF-8') as f_obj:
                f_obj.write(i)
    with open(zk_conf,'a',encoding='UTF-8') as f_cfg:
        f_cfg.write("dataDir=" + zk_data + "\ndataLogDir=" + zk_logs + "\n")
    os.system('source /etc/profile')
    os.system("source ~/.bashrc")

################################## 为zookeeper创建开机自启动文件 ##################################
def zookeeper_service():
    print('\t',[s()],' 创建Zookeeper开机自启动文件 ','\n')
    if not os.path.exists(r_service_dir):
        os.system('mkdir -p '+ r_service_dir)
    zookeeper_service_file = r_service_dir + 'zookeeper.service'
    with open(zookeeper_service_file,'w',encoding='UTF-8') as f_obj:
        f_obj.write("[Unit]\nDescription=Zookeeper service\nAfter=network.target\n[Service]\nUser="+common_user+"\nGroup="+common_user+"\nSyslogIdentifier=root\nEnvironment="+zk_dir+"\nPIDFile="+zk_dir+"/data/zookeeper_server.pid\nExecStart="+jdk_dir+"/bin/java \\\n  -Dzookeeper.log.dir="+zk_dir+"/logs/zookeeper.log \\\n  -Dzookeeper.root.logger=INFO,ROLLINGFILE \\\n  -cp "+zk_dir+"/zookeeper-3.4.9.jar:"+zk_dir+"/lib/* \\\n  -Dlog4j.configuration=file:"+zk_dir+"/conf/log4j.properties \\\n  -Dcom.sun.management.jmxremote \\\n  -Dcom.sun.management.jmxremote.local.only=false \\\n  org.apache.zookeeper.server.quorum.QuorumPeerMain \\\n  "+zk_dir+"/conf/zoo.cfg\n[Install]\nWantedBy=multi-user.target\n")

################################## 启动单机版zookeeper ##################################
def zookeeper_start():
    print('\t',[s()],' 启动Zookeeper ','\n')
    os.system('chown -R ' + common_user + ":" + common_user + ' ' + midsoft)
    os.system("su - "+common_user+" -c '"+ midsoft +"zookeeper/bin/zkServer.sh start >/dev/null 2>&1'")
    zk_status = os.popen('ps -ef | grep zookeeper | grep -v grep').read()
    p = str(zk_status).find('/zookeeper/bin')
    if not p ==-1:
        print('\t',[s()]," Zookeeper启动成功 ","\n")
    else:
        print('\t',[s()]," Zookeeper启动失败!， 退出！！ ","\n")
        os.sys.exit(1)

################################## 修改zookeeper配置文件，设置zookeeper为集群 ##################################
def zk_config():
    print('\t',[s()],' 清除环境变量，配置集群模式 ','\n')
    f = open(zk_conf,encoding='UTF-8')
    content = f.read()
    string = re.search('server(.*)',content)
    if string:
        print('\t',[s()],'server.*在'+zk_conf+'中已存在，准备清除.... 清除的变量如下：\n'+string.group())
        i = re.sub(r'server(.*)','',content)
        f = open(zk_conf,'w',encoding='UTF-8')
        f.write(i)
        f.close()
    f.close()
    for hostname, app in app_list.items():
        for j in app:
            if 'zookeeper' in j:
                with open(zk_conf,'a') as f_obj1:
                    f_obj1.write("server."+hostname.split('.')[3]+"="+ hostname + ":2888:3888\n")
    with open(zk_myid,'a',encoding='UTF-8') as f_obj2:
        f_obj2.write(ipaddr.split('.')[3])
    os.system('source /etc/profile')
    os.system("source ~/.bashrc")

################################## 启动集群版zookeeper ##################################
def zk_service():
    print('\t',[s()],' 启动Zookeeper集群 ','\n')
    for files in [midsoft,zk_conf,zk_myid]:
        os.system('chown -R '+common_user+':'+common_user + ' ' +files)
    os.system("su - "+common_user+" -c '"+ midsoft +"zookeeper/bin/zkServer.sh start >/dev/null 2>&1'")
    zk_status = os.popen('ps -ef | grep zookeeper | grep -v grep').read()
    p = str(zk_status).find('/zookeeper/bin')
    if not p ==-1:
        print('\t',[s()]," Zookeeper启动成功 ",'\n')
    else:
        print('\t',[s()]," Zookeeper启动失败， 退出！！ ",'\n')
        os.sys.exit(1)
    time.sleep(2)

################################## 判断zookeeper是否开机自启动 ##################################
def boot_up():
    service = 'zookeeper.service'
    bootup(service)
    alert_over(pyname)

################################## 主函数开始 ##################################
def main():
    jdk_install()
    zk_install()
    boot_up()

if __name__ == '__main__':
    main()
