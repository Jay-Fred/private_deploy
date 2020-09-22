import os,sys
import shutil
import re
import platform
import datetime,time
from include.env import *
import socket

################################## 通过ping的丢包率测试内网之间连通性 ##################################
def ping():
    print([s()], " 测试 内网ip之间 的连通性 ")
    for addrs in app_list.keys():
        for j in app_list.keys():
            if addrs == j:
                pass
            else:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(hostname=addrs, port=22, username=user_root, password=passwd_root)
                stdin, stdout, stderr = ssh.exec_command('ping -c 5 -w 2 -W 1000' + j)
                output = stdout.read().decode('utf-8')
                keywords = re.findall('100% packet loss', output)
                if len(keywords) == 0:
                    print("内网 " + addrs + " ping内网 " + j + " 正常")
                else:
                    print("内网 " + addrs + " ping内网 " + j + " 异常")
                    sys.exit(1)
                ssh.close()

    ################################## 根据返回状态码判断 内网通过代理ip、端口调用domain_url ##################################
    print("\n",[s()], " 测试 内网ip 到 domain_url 的连通性 ")
    tomcat_list = ['datatransfer-client','monitor-web']
    for addrs,apps in app_list.items():
        for tomcat in tomcat_list:
            if tomcat in apps:
                for proxyip in proxy_ip.strip("[']").split(','):
                    for url in domain_url.strip("[']").split(','):
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                        ssh.connect(hostname=addrs, port=22, username=user_root, password=passwd_root)
                        stdin, stdout, stderr = ssh.exec_command('curl -L -s -o status_code --connect-timeout 30 ' + url + ' -x ' + proxyip + ':' + proxy_port + ' -w %{http_code}')
                        output = stdout.read().decode('utf-8')
                        if output != str(200):
                            print("内网 " + addrs + " 调 domain_url " + url + " 异常")
                        else:
                            print("内网 " + addrs + " 调 domain_url " + url + " 正常")
                        ssh.close()
def main():
    ping()

if __name__ == '__main__':
    main()