import os,sys
import datetime,time
import re
from env import *

redis_package = r_soft_dir +  "redis/redis.tar.gz"
redis_config = midsoft +  "redis/config/redis.conf"
ipaddr = sys.argv[1]
pyname = os.path.basename(__file__)

################################## 判断Redis软件包、安装目录及密码复杂性 ##################################
def check_package():
    alert_start(ipaddr,pyname)
    check_dir(midsoft,redis_package)
    checkpasswd(general_passwd)
    redis_run = '/var/run/redis'
    if not os.path.exists(redis_run):
        os.system('mkdir -p ' + redis_run)

################################## 清除旧的Redis环境变量，添加新环境变量 ##################################
def init_profile():
    print('\t',[s()],' 检查环境变量 ','\n')
    filename = '/etc/profile'
    with open('/etc/profile',encoding='UTF-8') as f:
        content = f.read()
        string = re.search('export REDIS_HOME(.*)',content)
        if string:
            print('\t',[s()],' REDIS_HOME在/etc/profile中已存在，准备清除. 清除的变量如下：\n\t'+string.group())
            i = re.sub(r'export REDIS_HOME(.*)','',content)
            with open('/etc/profile','w',encoding='UTF-8') as f_obj1:
                f_obj1.write(i)
    with open(filename,'a',encoding='UTF-8') as f_obj2:
        f_obj2.write("\nexport REDIS_HOME="+midsoft+"redis\nexport PATH=$PATH:"+midsoft+"redis/src\n")
    os.system('source /etc/profile')
    os.system("source ~/.bashrc")

################################## 开始二进制解压安装Redis ##################################
def redis_install():
    print('\t',[s()],' 安装Redis ','\n')
    os.system('tar zxf ' + redis_package + ' -C ' + midsoft)
    time.sleep(3)
    if os.path.exists(redis_config):
        dd = {'/usr/local/software':midsoft,'lhdnapa12#':general_passwd}
        replace(redis_config,**dd)
    os.system('chown -R ' + common_user + ":" + common_user + " "+ midsoft + "*")

################################## 启动Redis并判断服务启动状态 ##################################
def start_redis():
    os.system("su "+common_user+" -c 'nohup "+midsoft+ "redis/src/redis-server "+midsoft+"redis/config/redis.conf &'")
    redis_port = os.popen('ps -ef|grep redis|grep -v grep').read()
    p = str(redis_port).find('6379')
    print('\t',[s()],' 启动Redis服务 ','\n')
    if not p ==-1:
        print('\t',[s()]," Redis启动成功 ",'\n')
    else:
        print('\t',[s()]," Redis启动失败! ",'\n')
        sys.exit(1)

################################## 为Redis服务创建开启自启动文件 ##################################
def redis_service():
    print('\t',[s()]," 创建redis开机自启动文件 ","\n")
    if not os.path.exists(r_service_dir):
        os.system('mkdir -p '+ r_service_dir)
    redis_service_file = r_service_dir + 'redis.service'
    with open(redis_service_file,'w',encoding='UTF-8') as f_obj:
        f_obj.write("[Unit]\nDescription=Redis\nAfter=network.target\n[Service]\nUser="+common_user+"\nGroup="+common_user+"\nType=forking\nExecStart="+midsoft+"redis/src/redis-server "+midsoft+"redis/config/redis.conf\nExecReload=/bin/kill -s HUP $MAINPID\nExecStop=/bin/kill -s QUIT $MAINPID\nPrivateTmp=true\n[Install]\nWantedBy=multi-user.target\n")

################################## 判断Redis是否开机自启动  ##################################
def boot_up():
    service = 'redis.service'
    bootup(service)
    alert_over(pyname)

################################## 主函数开始  ##################################
def main():
    check_package()
    init_profile()
    redis_install()
    start_redis()
    redis_service()
    boot_up()

if __name__ == '__main__':
    main()