import os,sys
import datetime,time
import re
import shutil
import paramiko
from subprocess import *
import configparser
from configparser import ConfigParser
import socket
import fcntl
import struct

################################## 读取配置文件，获取配置信息 ########################################
s = lambda:time.strftime('%Y-%m-%d %H:%M:%S ')
project_path = os.path.dirname(os.path.abspath(__file__))
file = project_path + '/config.ini'
config = configparser.RawConfigParser()
config.read(file)
soft_dir = config.get('soft','soft_dir')
r_soft_dir = config.get('soft','r_soft_dir')
py_dir = config.get('soft','py_dir')
r_py_dir = config.get('soft','r_py_dir')
service_dir = config.get('soft','service_dir')
r_service_dir = config.get('soft','r_service_dir')
install_dir = config.get('deploy','common')
tomcat_dir = config.get('deploy','tomcat_dir')
midsoft = config.get('deploy','midsoft')
user_root = config.get('user','user_root')
passwd_root = config.get('user','passwd_root')
common_user = config.get('user','common_user')
common_passwd = config.get('user','common_passwd')
mysql_user = config.get('user','mysql_user')
mysql_passwd = config.get('user','mysql_passwd')
general_passwd = config.get('user','general_passwd')
proxy_ip = config.get('other','proxy_ip')
proxy_port = config.get('other','proxy_port')
domain_url = config.get('other','domain_url')
paramiko_ip = config.get('other','paramiko_ip')
ip_list = config.items('ip_list')
app_list = dict(ip_list)
for key,app in app_list.items():
    app_list[key] = eval(app)

################################## 检查密码复杂性：密码策略包含 数字、大小写、特殊字符、长度为8位以上要求 ########################################
def checkpasswd(password):
    if re.match(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*[\d])(?=.*[!@#$%^&*_])[\w\d!@#$%^&*_]{8,20}$", password):
        print('\t',[s()]," 密码符合复杂性要求 ",'\n')
    else:
        print('\t',[s()]," 密码不符合复杂性要求！！！" ,'\n')
        sys.exit(1)

################################## 检测目录及软件包是否存在 ##################################
def check_dir(dir,package):
    if not os.path.exists(dir):
        os.mkdir(dir)
        print('\t',[s()]," 安装目录为： "+ dir,'\n')
        print('\t',[s()]," 安装所需软件包目录为： "+ package,'\n')
    elif not os.path.exists(package):
        print('\t',[s()]," 检查安装包不存在 ")
        sys.exit(1)

################################## 备份 Yum源配置文件 ##################################
def yum_bak():
    src_path = '/etc/yum.repos.d/'
    dest_path = '/etc/yum.repos.d/yum_bak/'
    print('\t',[s()], " 开始备份yum文件 ", '\n')
    if not os.path.exists(dest_path):
        os.mkdir(dest_path)
    if os.path.exists(src_path):
        for root, dirs, fnames in os.walk(src_path):
            for fname in sorted(fnames):
                try:
                    fpath = os.path.join(root, fname)
                    shutil.copy(fpath, dest_path)
                except shutil.SameFileError:
                    pass

################################## 配置文件字符串替换 ##################################
def replace(filename,**kwargs):
    if os.path.exists(filename):
        with open(filename,'r+',encoding='UTF-8') as f_obj:
            content = f_obj.read()
            for k, v in kwargs.items():
               o =  content.replace(k,v)
               with open(filename,'w',encoding='UTF-8') as f_j:
                   f_j.write(o)

################################## 目录上传 ##################################
def upload_dir(hostname,username,passwd,local_dir,remote_dir):
    try:
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname, port=22, username=username, password=passwd)
        ssh.exec_command('mkdir -p ' + remote_dir)
        ssh.close()
        t=paramiko.Transport((hostname,22))
        t.connect(username=username,password=passwd)
        sftp=paramiko.SFTPClient.from_transport(t)
        for root,dirs,files in os.walk(local_dir):
            for filespath in files:
                local_file = os.path.join(root,filespath)
                a = local_file.replace(local_dir,'')
                remote_file = os.path.join(remote_dir,a)
                try:
                    sftp.put(local_file,remote_file)
                except Exception:
                    pass
            for name in dirs:
                local_path = os.path.join(root,name)
                a = local_path.replace(local_dir,'')
                remote_path = os.path.join(remote_dir,a)
                try:
                    sftp.mkdir(remote_path)
                except Exception:
                    pass
        t.close()
    except Exception:
        pass

################################## 单个文件上传 ##################################
def upload_file(hostname,username,passwd,local_file,remote_file):
    try:
        t=paramiko.Transport((hostname,22))
        t.connect(username=username,password=passwd)
        sftp=paramiko.SFTPClient.from_transport(t)
        sftp.put(local_file,remote_file)
        t.close()
    except Exception as e:
        print(e)
        return False

################################## 单个文件下载 ##################################
def get_file(hostname,username,passwd,remote_file,local_file):
    t=paramiko.Transport((hostname,22))
    t.connect(username=username,password=passwd)
    sftp = paramiko.SFTPClient.from_transport(t)
    sftp.get(remote_file,local_file)
    sftp.close()

################################## 远程执行命令 ##################################
def install(hostname,username,passwd,command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=hostname, port=22, username=username, password=passwd)
    stdin, stdout, stderr = ssh.exec_command(command)
    result = stdout.read().decode('utf-8')
    with open('install.log','a',encoding='UTF-8') as f_obj:
        f_obj.write(result)
    channel = stdout.channel
    status = channel.recv_exit_status()
    if status == 1:
        print(result)
        sys.exit(1)
    ssh.close()

################################## 调用系统命令 ##################################
def command(shell):
    p = Popen(shell,
              stdout=PIPE,
              stderr=PIPE,
              shell=True
              )
    p.wait()
    out = p.stdout.read().decode('utf-8')
    return out
################################## 判断服务是否开机自启动 ##################################
def bootup(service):
    status = command("systemctl list-unit-files " + service + " | awk 'NR==2{print $2}'")
    if status.rstrip() == 'enabled':
        print('\t',[s()]," 服务 " + service + " 已开启自启动 ",'\n')
    elif status == 'disabled':
        print('\t',[s()]," 服务 " + service + " 未开启自启动 ",'\n')
        print('\t',[s()]," 正在为服务 " + service + " 设置开启自启动 ",'\n')
        command("systemctl enable " + service + " 2>&1 >/dev/null")
    else:
        print('\t',[s()]," 服务 " + service + " 尚未部署开机自启动 ",'\n')
        print('\t',[s()]," 开始为服务 " + service + " 部署开机自启动 ",'\n')
        des_file = '/lib/systemd/system/' + service
        try:
            shutil.copyfile(r_service_dir + service, des_file)
            os.system('systemctl daemon-reload')
            command("systemctl enable " + service + " 2>&1 >/dev/null")
        except FileNotFoundError:
            print('\t',[s()]," 文件未找到或文件不存在 ",'\n')

################################## 提示安装函数 ##################################
def alert_start(ipaddr,pyname):
    print(ipaddr + "  开始安装 " + pyname + " 脚本 " + s() , "\n")

def alert_over(pyname):
    print('\t', [s()], " 安装 " + pyname + " 脚本结束 ", '\n')
