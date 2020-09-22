import os,sys
import shutil
import re,copy
import platform
import datetime,time
from include.env import *
import paramiko
import requests
import json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
app_list_copy = copy.deepcopy(app_list)

################################## 上传脚本，根据安装顺序列表远程安装引用并启动 ##################################
def main_install():
    new_list = []
    for hs, aps in app_list_copy.items():
        upload_dir(hs, user_root, passwd_root, py_dir, r_py_dir)
        new_list.extend(aps)
        client.connect(hostname=hs, port=22, username=user_root, password=passwd_root)
        stdin, stdout, stderr = client.exec_command('python3 ' + r_py_dir + "init.py " + hs)
        info = stdout.read().decode('utf-8')
        print('\n',info)
    ack = input(" 是否继续安装：[Y/N] ")
    if ack == 'Y':
        scale = 100
        print("\n" + " 开始安装 ".center(scale // 2, "-"))
        print("\n" + "安装软包如下：")
        start = time.perf_counter()
        fx = ['gcc','tomcat','zookeeper']
        applicat_list = ['mysql_master','mysql_slave','mysql','mydumper','nginx','redis','supervise']
        for appli in applicat_list:
            if appli in new_list:
                fx.append(appli)
        print(fx)

        for i in fx:
            if i in ('nginx' , 'redis' , 'supervise' , 'mydumper'):
                print("\n" + " 开始安装 " + i, end=' ')
                print('........', end='', flush=True)
                time.sleep(0.5)
                print('\n\r', end='')
                try:
                    other(i)
                except Exception:
                    sys.exit(1)
                print(" 安装 " + i + " 结束 ")
            elif i == "mysql":
                print("\n" + " 开始安装 " + i, end=' ')
                print('........', end='', flush=True)
                time.sleep(0.5)
                print('\n\r', end='')
                try:
                    other(i)
                except Exception:
                    sys.exit(1)
                print(" 安装 " + i + " 结束 ")
            elif i == "zookeeper":
                print("\n" + " 开始安装 " + i, end=' ')
                print('........', end='', flush=True)
                time.sleep(0.5)
                print('\n\r', end='')
                try:
                    zookeeper()
                except Exception:
                    sys.exit(1)
                print(" 安装 " + i + " 结束 ")
            else:
                print("\n" + " 开始安装 " + i, end=' ')
                print('........', end='', flush=True)
                time.sleep(0.5)
                print('\n\r', end='')
                try:
                    eval(i)()
                except Exception:
                    sys.exit(1)
                print(" 安装 " + i + " 结束 ")
        print("\n" + "安装结束".center(scale // 2, "-"))
    else:
        sys.exit(0)

################################## 远程上传gcc软件包并安装 ##################################
def gcc():
    for host, appss in app_list_copy.items():
        gcc_file = soft_dir + 'gcc/'
        r_gcc_file = r_soft_dir + 'gcc/'
        java_file = soft_dir + 'jdk/'
        r_java_file = r_soft_dir + 'jdk/'
        upload_dir(host, user_root, passwd_root, java_file, r_java_file)
        upload_dir(host, user_root, passwd_root, gcc_file, r_gcc_file)
        install(host, user_root, passwd_root, 'python3 ' + r_py_dir + "gcc.py " + host)

################################## 读取配置文件安装mysql_master,生成主从同步日志文件 ##################################
def mysql_master():
    for host,app in app_list_copy.items():
        for j in app:
            if 'master' in j:
                global master_ip
                master_ip = host
                mysql_file = soft_dir + 'mysql/'
                r_mysql_file = r_soft_dir + 'mysql/'
                upload_dir(host, user_root, passwd_root, mysql_file, r_mysql_file)
                install(host, user_root, passwd_root, 'python3 ' + r_py_dir + "mysql.py " + host)
                del app_list_copy[host][app_list_copy[host].index(j)]

################################## 上传主从同步日志文件到mysql_slave并安装 ##################################
def mysql_slave():
    for x, y in app_list_copy.items():
        for z in y:
            if 'slave' in z:
                mysql_file = soft_dir + 'mysql/'
                r_mysql_file = r_soft_dir + 'mysql/'
                bin_file = '/tmp/bin.txt'
                r_bin_file = r_py_dir + 'bin.txt'
                if master_ip != paramiko_ip:
                    get_file(master_ip, user_root, passwd_root, r_bin_file, bin_file)
                    upload_file(x, user_root, passwd_root, bin_file, r_bin_file)
                else:
                    upload_file(x, user_root, passwd_root, r_bin_file, r_bin_file)
                upload_dir(x, user_root, passwd_root, mysql_file, r_mysql_file)
                install(x, user_root, passwd_root, 'python3 ' + r_py_dir + 'mysql_slave.py ' + x)
                del app_list_copy[x][app_list_copy[x].index(z)]

################################## 匹配tomcat列表远程安装tomcat ##################################
def tomcat():
    tomcat_file = soft_dir + 'tomcat/'
    r_tomcat_file = r_soft_dir + 'tomcat/'
    files = os.listdir(tomcat_file)
    for ips,ap in app_list_copy.items():
        upload_dir(ips, user_root, passwd_root, tomcat_file, r_tomcat_file)
        for tom in ap[::-1]:
            for file in files:
                if tom in file:
                    del app_list_copy[ips][app_list_copy[ips].index(tom)]
        install(ips, user_root, passwd_root, 'python3 ' + r_py_dir + 'tomcat.py ' + ips)

################################## 匹配zookeeper列表远程安装tomcat ##################################
def zookeeper():
    for hostt,aapp in app_list_copy.items():
        for jj in aapp:
            if 'zookeeper' in jj:
                zookeeper_file = soft_dir + 'zookeeper/'
                r_zookeeper_file = r_soft_dir + 'zookeeper/'
                upload_dir(hostt, user_root, passwd_root, zookeeper_file, r_zookeeper_file)
                install(hostt, user_root, passwd_root, 'python3 ' + r_py_dir + "zookeeper.py " + hostt)
                del app_list_copy[hostt][app_list_copy[hostt].index(jj)]

################################## 统一上传其他应用的软件包并远程安装 ##################################
def other(appname):
    for a, b in app_list_copy.items():
        if appname in b:
             app_file = soft_dir + appname + '/'
             r_app_file = r_soft_dir + appname + '/'
             upload_dir(a, user_root, passwd_root, app_file, r_app_file)
             install(a, user_root, passwd_root, 'python3 ' + r_py_dir + appname + ".py " + a)

################################## 根据定义的tomcat启动顺序启动tomcat ##################################
def start_tomcat():
    #tomcat部署启动顺序流程：
    #1.tomcat-8.0.30-decision-server-8388
    #2.tomcat-8.0.30-interbank-server-8788
    #3.tomcat-8.0.30-interbank-quartz-8988
    #4.tomcat-8.0.30-monitor-server-8188
    #5.tomcat-8.0.30-monitor-web-8288
    #6.tomcat-8.0.30-interbank-client-8888
    #7.tomcat-8.0.30-datatransfer-client-8080

    tomcat_service=['tomcat-8.0.30-decision-server-8388','tomcat-8.0.30-interbank-server-8788','tomcat-8.0.30-interbank-quartz-8988','tomcat-8.0.30-monitor-server-8188','tomcat-8.0.30-monitor-web-8288','tomcat-8.0.30-interbank-client-8888','tomcat-8.0.30-datatransfer-client-8080']
    dicts = {}
    d = {}
    tomcat = {}
    list1 = []
    for key,value in app_list.items():
        for app in value:
            for index,word in enumerate(tomcat_service):
                if app in word and index <= len(tomcat_service):
                    dicts[index] = key + " "+ word
    for aa in sorted(dicts):
        tomcat[aa] = dicts[aa]
    for i in tomcat.values():
        list1.append(i)
    for j in range(len(list1)):
        print("\n","  开始启动 " + list1[j].split(' ')[0] + '  ' + list1[j].split(' ')[1]  + '  ' + s())
        install(list1[j].split(' ')[0], user_root, passwd_root, "source /etc/profile;su - "+ common_user + ' ' + tomcat_dir+list1[j].split(' ')[1]+"/bin/startup.sh >/dev/null 2>&1")
################################## 向flask web服务器发送POST请求 ##################################
def network_map():
    url1 = 'http://10.1.90.216:9090'
    url2 = 'http://10.1.90.216:9090/test'
    payload = {}
    DMZ区 = {}
    代理服务器 = {}

    for i in proxy_ip:
        代理服务器[proxy_ip] = ["proxy_ip"]
    for i in proxy_ip:
        DMZ区[proxy_ip] = [""]
    payload["内网区"] = app_list
    payload["DMZ区"] = DMZ区
    payload["代理服务器"] = 代理服务器
    json_data = json.dumps(payload).encode('UTF-8')
    proxy = {"http": proxy_ip + ":" + proxy_port}
    response1 = requests.post(url=url1, data=json_data, proxies=proxy)
    time.sleep(5)
    response2 = requests.post(url=url2, data=json_data, proxies=proxy)
    print("-"*80)
    print("\n已向 " + url1 + " 和 " + url2 + " 发送POST请求，请求内容为:\n" + str(payload))

################################## 主函数开始 ##################################
def main():
    main_install()
    start_tomcat()
    network_map()

if __name__ == '__main__':
    main()