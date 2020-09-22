import os,sys
import datetime,time
import re
import shutil
import pymysql
from env import *

mysql_dir = install_dir + 'mysql'
my_cnf = r_soft_dir + 'mysql/my.cnf'
mysql_package = r_soft_dir + 'mysql/Package'
mysql_log_dir = mysql_dir + os.sep + 'log'
mysql_data_dir = mysql_dir + os.sep + 'data'
ipaddr = sys.argv[1]
pyname = os.path.basename(__file__)

################################## 备份yum源，配置mysql源安装mysql ##################################
def mysql_yum():
    yum_bak()
    yum_file = '/etc/yum.repos.d/Mysql_Redis.repo'
    with open(yum_file,'w',encoding='UTF-8') as f:
        f.write("[Mysql_Redis]\nname=Mysql_Redis\nbaseurl=file://"+mysql_package+"\ngpgcheck=0\nenabled=1\n")
    os.system('yum clean all >/dev/null 2>&1 && yum makecache >/dev/null 2>&1 && yum -y install mysql-community-server >/dev/null 2>&1')
    os.system('systemctl start mysqld && systemctl enable mysqld && systemctl daemon-reload')
    time.sleep(2)

################################## 判断mysql服务启动状态 ##################################
def mysql_status():
    mysqld_proce = os.popen('ps -ef|grep mysqld | grep -v grep').read()
    p = str(mysqld_proce).find('/usr/sbin/mysqld')
    print('\t',[s()], ' 启动mysqld ', '\n')
    if not p ==-1:
        print('\t',[s()]," Mysql启动成功 ",'\n')
    else:
        print('\t',[s()]," Mysql启动失败! ",'\n')
        sys.exit(1)
    time.sleep(2)

################################## 创建mysql用户、密码和所需目录 ##################################
def mysql_conf():
    print('\t',[s()],' 开始创建Mysql用户，初始密码为:mysql ','\n')
    os.system('groupadd mysql && useradd -g  mysql ' + mysql_user )
    os.system("echo "+ mysql_passwd +" | passwd --stdin " + mysql_user +" >/dev/null 2>&1")
    print('\t',[s()],' 创建数据目录和日志目录 ','\n')
    for dirs in [mysql_dir,mysql_log_dir,mysql_data_dir]:
        try:
            os.mkdir(dirs)
        except Exception:
            pass
    time.sleep(2)

################################## 修改mysql数据目录和日志目录 ##################################
def string():
    print('\t',[s()],' 备份my_cnf文件 ','\n')
    my_src = '/etc/my.cnf'
    my_bak = '/etc/my.cnf_bak'
    try:
        os.rename(my_src, my_bak)
        shutil.copyfile(my_cnf,my_src)
    except Exception:
        print('\t',[s()], ' /etc/my.cnf 文件不存在！！！ ', '\n')
        sys.exit(1)
    e = {'/usr/local/mysql':mysql_dir}
    replace(my_src,**e)
    os.system('cp -r /var/lib/mysql/* ' + mysql_data_dir)

################################## 创建慢sql文件和错误日志文件 ##################################
def Touch():
    print('\t',[s()],' 创建慢sql文件和错误日志文件 ','\n')
    slow_log_file = mysql_log_dir + os.sep + 'mysql-slow.log'
    err_log_file = mysql_log_dir + os.sep + 'mysql.err'
    for files in slow_log_file,err_log_file:
        if not os.path.exists(files):
            with open(files,'w',encoding='UTF-8') as f_obj:
                f_obj.close()
    os.system('chown -R ' + mysql_user + ':' + mysql_user + ' ' + mysql_dir)
    print('\t',[s()],' 重启mysqld ','\n')
    os.system('systemctl daemon-reload && systemctl restart mysqld')
    time.sleep(3)
    mysql_status()

################################## 软连接mysql.sock文件 ##################################
def link():
    print('\t',[s()],' 创建sock链接 ','\n')
    link_src = '/var/lib/mysql/mysql.sock'
    link_dest = mysql_log_dir + os.sep + 'mysql.sock'
    if os.path.exists(link_src):
        os.remove(link_src)
    os.symlink(link_dest,link_src)
    for files in ['/etc/my.cnf','/usr/share/mysql','/var/run/mysqld',mysql_dir,link_src]:
        os.system('chown -R '+ mysql_user + ':' + mysql_user + ' ' + files)

################################## 登陆mysql，修改mysql密码 ##################################
def alert_passwd():
    print('\t',[s()],' 修改登陆密码 ','\n')
    f = '/var/log/mysqld.log'
    with open(f,encoding='UTF-8') as f_obj:
        content = f_obj.read()
        word = re.findall(r'root@localhost:(.*)',content)
        for line in word:
            src_passwd = line.strip()
    try:
        os.system("mysql -uroot --connect-expired-password  -p'" + src_passwd + '\''" -e \"ALTER USER root@localhost IDENTIFIED BY \'" + general_passwd + "';\"""")
        time.sleep(3)
    except Exception:
        print('\t',[s()], ' 修改密码错误，退出 ', '\n')
        sys.exit(1)

################################## 授权mysql和root用户 ##################################
def grant_root():
    print('\t',[s()],' 授权 ','\n')
    conn = pymysql.connect(
        host = 'localhost',
        user = 'root',
        passwd = general_passwd,
        port = 3306,
        charset='utf8'
    )
    cursor = conn.cursor()
    cursor.execute("grant all privileges on *.* to 'root'@'%' identified by '" + general_passwd + "';")
    cursor.execute("grant all privileges on *.* to "+ mysql_user +"@'%' identified by '" + general_passwd + "';")
    cursor.execute("flush privileges;")
    cursor.close()
    conn.close()

################################## 配置mysql主从，设置主从同步日志 ##################################
def master_mynf():
    print('\t',[s()],' 开始配置mysql主从 ','\n')
    print('\t',[s()],' 关闭防火墙 ','\n')
    os.system('systemctl stop firewalld')
    print('\t',[s()],' 修改master my_cnf ','\n')
    file = '/etc/my.cnf'
    with open(file,encoding='UTF-8') as f:
        content = f.read()
        string = re.search('log_bin(.*)|server_id(.*)',content)
        if string:
            i = re.sub(r'log_bin(.*)|server_id(.*)','',content)
            with open('/etc/my.cnf','w',encoding='UTF-8') as f_obj1:
                f_obj1.write(i)
    with open('/etc/my.cnf','a',encoding='UTF-8') as f_obj2:
        f_obj2.write('log_bin=mysql-bin\nserver_id='+str(ipaddr.split('.')[3]))
    os.system("rm -rf " + mysql_data_dir + os.sep + "auto.cnf")
    os.system('systemctl restart mysqld')
    mysql_status()

################################## 在mysql_master 上创建主从同步用户并授权mysql_slave ##################################
def mysql_master():
    for hostname, app in app_list.items():
        for j in app:
            if 'slave' in j:
                mysql_slave_ip = hostname
    print('\t',[s()],' 创建主从同步所需用户 ','\n')
    conn = pymysql.connect(
        host = 'localhost',
        user = 'root',
        passwd = general_passwd,
        port = 3306,
        charset='utf8'
    )
    cursor = conn.cursor()
    cursor.execute("grant replication slave  on *.* to 'repl'@'" + mysql_slave_ip + "' identified by '" + general_passwd + "';")
    cursor.execute('flush privileges;')
    cursor.execute('show master status;')
    result = cursor.fetchall()
    File = result[0][0]
    Position = result[0][1]
    print('\t',[s()],' 打印maste同步信息,已保存至bin.txt ','\n')
    print('\t',[s()], " 主节点File为： "+ str(File).rstrip()," 主节点Position为： "+ str(Position).rstrip(), '\n')
    txt = r_py_dir + 'bin.txt'
    with open(txt,'w',encoding='UTF-8') as tmp:
        tmp.write(str(File)+',')
        tmp.write(str(Position))
    cursor.close()
    conn.close()
    alert_over(pyname)

################################## 主函数开始，判断mysql是否为单机或集群 ##################################
def main():
    i = 0
    for key, value in app_list.items():
        word = re.findall("mysql(.*)", str(value))
        leng = len(word)
        i += leng
    if i >= 2:
        alert_start(ipaddr, pyname)
        print('\t',[s()], " 开始安装mysql集群版 ",'\n')
        mysql_yum()
        mysql_status()
        mysql_conf()
        string()
        Touch()
        link()
        alert_passwd()
        grant_root()
        master_mynf()
        mysql_master()
    else:
        alert_start(ipaddr, pyname)
        print('\t',[s()], " 开始安装mysql单机版 ", '\n')
        mysql_yum()
        mysql_status()
        mysql_conf()
        string()
        Touch()
        link()
        alert_passwd()
        grant_root()
        alert_over(pyname)

if __name__ == '__main__':
    main()