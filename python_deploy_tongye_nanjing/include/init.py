import os,sys
import shutil
import re
import platform
import datetime,time
from env import *
ipaddr = sys.argv[1]
pyname = os.path.basename(__file__)

################################## 获取系统配置信息：如cpu、内存、磁盘等 ##################################
def Print_sys_info():
    print("\033[31m————" * 6 + ipaddr + " 系统配置信息 " + s() + "————" * 6 + "\033[0m")
    print("\033[33m"+str([s()]),' 获取系统版本 '+"\033[0m",'\n')
    print(platform.platform()+"\n")
    uname = command('uname -a')
    print("\033[33m"+str([s()]),' 当前系统内核为：'+"\033[0m",'\n',uname)
    memory = command("free -m | grep Mem | awk '{print  $2}'")
    print("\033[33m"+str([s()])," Memory is : "+"\033[0m",'\n',memory)
    disk =  command('df -Th')
    print("\033[33m"+str([s()])," 当前磁盘使用情况为 ："+"\033[0m",'\n',disk)

def main():
    Print_sys_info()

if __name__ == '__main__':
    main()
