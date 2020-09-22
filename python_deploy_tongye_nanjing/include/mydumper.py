import os
import datetime,time
import re
from env import *
ipaddr = sys.argv[1]
pyname = os.path.basename(__file__)

################################## 编译安装mydupmer ##################################
def mydump_install():
    alert_start(ipaddr,pyname)
    time.sleep(2)
    mydump_file = r_soft_dir + 'mydumper/mydumper-0.9.1.tar.gz'
    mysqldump_package = r_soft_dir + 'mydumper/Package'
    check_dir(mysqldump_package,mydump_file)
    os.system('tar zxf ' + mydump_file + " -C " + install_dir)
    time.sleep(2)
    yum_bak()
    yum_file = '/etc/yum.repos.d/mydumper.repo'
    with open(yum_file,'w',encoding='UTF-8') as f_obj:
        f_obj.write("[MyDumper]\nname=MyDumper\nbaseurl=file://"+ mysqldump_package +"\ngpgcheck=0\nenabled=1")
    print('\t',[s()], ' 安装编译mydumper ', '\n')
    os.chdir(install_dir + os.sep + "mydumper-0.9.1")
    os.system('yum clean all >/dev/null 2>&1 && yum makecache >/dev/null 2>&1 && yum -y install gcc-c++ cmake glib2-devel mysql-devel zlib-devel pcre-devel >/dev/null 2>&1 && cmake ./ >/dev/null 2>&1 && make >/dev/null 2>&1 && make install >/dev/null 2>&1')
    alert_over(pyname)

def main():
    mydump_install()

if __name__ == '__main__':
    main()