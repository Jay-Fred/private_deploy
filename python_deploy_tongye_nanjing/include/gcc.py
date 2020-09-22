import os,sys
import shutil
import datetime,time
from env import *
ipaddr = sys.argv[1]
pyname = os.path.basename(__file__)

################################## 初始化环境，设置打开文件句柄最大为65536 ##################################
def Init_openfiles():
    alert_start(ipaddr,pyname)
    print('\t',[s()]," 初始化 openfiles ",'\n')
    time.sleep(1)
    filename = '/etc/security/limits.conf'
    with open(filename,'a',encoding='UTF-8') as f_limits:
        f_limits.write("* soft nofile 65536      # open files  (-n)\n* hard nofile 65536\n")

################################## 关闭防火墙及SELINUX ##################################
def Disable_selinux():
    print('\t',[s()],' 关闭防火墙、SELINUX ','\n')
    file_selinux = '/etc/selinux/config'
    d = {'SELINUX=enforcing':'SELINUX=disabled'}
    replace(file_selinux,**d)
    os.system('systemctl stop firewalld && systemctl disable firewalld.service')

################################## 备份yum源 ##################################
def back_yum():
    time.sleep(2)
    yum_bak()

################################## 安装GCC编译工具 ##################################
def gcc_yum():
    print('\t',[s()],' 开始安装Gcc ','\n')
    time.sleep(2)
    yum_file = '/etc/yum.repos.d/Gcc.repo'
    gcc_package = r_soft_dir + "gcc/Package"
    with open(yum_file,'w',encoding='UTF-8') as f:
        f.write("[Gcc]\nname=Gcc\nbaseurl=file://"+gcc_package +"\ngpgcheck=0\nenabled=1")
    try:
        os.system('yum clean all >/dev/null 2>&1 && yum makecache >/dev/null 2>&1 && yum install gcc-c++ -y >/dev/null 2>&1')
        alert_over(pyname)
    except Exception:
        sys.exit(0)

################################## 主函数执行开始 ##################################
def main():
    Init_openfiles()
    Disable_selinux()
    back_yum()
    gcc_yum()

if __name__ == '__main__':
    main()