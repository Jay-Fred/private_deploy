import os,sys
import datetime
import re
from env import *
ipaddr = sys.argv[1]
pyname = os.path.basename(__file__)

################################## 二进制解压安装supervise  ##################################
def supervise_install():
    supervise_dir = install_dir + "supervise"
    supervise_pack = r_soft_dir + "supervise/admin.tar.gz"
    alert_start(ipaddr,pyname)
    check_dir(supervise_dir,supervise_pack)
    os.system('tar zxf ' + supervise_pack + " -C " + supervise_dir)
    os.chdir(supervise_dir + os.sep + "admin" + os.sep + "daemontools-0.76")
    os.system('sh package/install >/dev/null 2>&1')
    alert_over(pyname)

def main():
    supervise_install()
if __name__ == '__main__':
    main()
