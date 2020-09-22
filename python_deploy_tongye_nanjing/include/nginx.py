import os,sys
import datetime,time
import re
import shutil
from env import *

nginx_package = r_soft_dir + 'nginx/Package'
html_dir = '/html'
ipaddr = sys.argv[1]
pyname = os.path.basename(__file__)

################################## 备份yum源，rpm安装Nginx ##################################
def nginx_init():
    alert_start(ipaddr,pyname)
    check_dir(html_dir,nginx_package)
    yum_bak()
    os.system('chown -R ' + common_user + ':' + common_user + ' ' + html_dir )
    os.chdir(nginx_package)
    try:
        os.system('rpm -ih ' + nginx_package + os.sep + '*.rpm >/dev/null 2>&1')
    except Exception:
        os.system('yum -y remove nginx >/dev/null 2>&1')
        os.system('rpm -ih ' + nginx_package + os.sep + '*.rpm >/dev/null 2>&1')

################################## 备份yum默认配置文件 ##################################
def nginx_back():
    print('\t',[s()],' 备份配置文件 ','\n')
    nginx_config = '/etc/nginx/conf.d/default.conf'
    nginx_config_bak = '/etc/nginx/conf.d/default.conf_bak'
    if not os.path.exists(nginx_config):
        os.system('yum -y remove nginx >/dev/null 2>&1 && rm -rf /etc/nginx  /var/log/nginx')
        os.system('rpm -ih ' + nginx_package + os.sep + '*.rpm >/dev/null 2>&1')
    try:
        os.rename(nginx_config,nginx_config_bak)
    except Exception:
        os.system('yum -y remove nginx >/dev/null 2>&1 && rm -rf /etc/nginx  /var/log/nginx')
        os.system('rpm -ih ' + nginx_package + os.sep + '*.rpm >/dev/null 2>&1')
        os.rename(nginx_config, nginx_config_bak)

################################## 修改nginx_pid文件目录 ##################################
def nginx_cofing():
    print('\t',[s()],' 修改Nginx配置文件 ','\n')
    src_file = nginx_package + os.sep + '80.interbank.conf'
    dst_file = '/etc/nginx/conf.d/'
    try:
        shutil.copy(src_file,dst_file)
    except FileNotFoundError:
        print('\t',[s()]," 文件未找到 ")
        sys.exit(1)
    file = '/etc/nginx/nginx.conf'
    with open(file,'r',encoding='UTF-8') as f_obj:
        content = f_obj.read()
        i = re.sub('user  nginx;','',content)
        with open(file,'w',encoding='UTF-8') as f_word:
            f_word.write(i)
    words = {"/var/run/nginx.pid":"/etc/nginx/nginx.pid"}
    replace(file,**words)

################################## 配置Nginx反向代理，默认开放端口8080 ##################################
def deploy_nginx():
    print('\t',[s()],' 开始配置反向代理 ','\n')
    for hostname, app in app_list.items():
        for j in app:
            if 'datatransfer' in j:
                deploy_ip = hostname
    file = '/etc/nginx/conf.d/80.interbank.conf'
    aa = {'127.0.0.1:8888':deploy_ip + ":8080"}
    try:
        replace(file,**aa)
    except Exception:
        print('\t',[s()],' 反向代理IP不存理 ','\n')

################################## 判断Nginx启动状态 ##################################
def nginx_status():
    nginx_proce = os.popen('ps -ef|grep nginx|grep -v grep').read()
    p = str(nginx_proce).find('/usr/sbin/nginx')
    print('\t',[s()], ' 启动Nginx ', '\n')
    if not p ==-1:
        print('\t',[s()]," Nginx启动成功! ",'\n')
    else:
        print('\t',[s()]," Nginx启动失败! ",'\n')
        sys.exit(1)
    time.sleep(2)

################################## 为Nginx服务创建开机自启动文件 ##################################
def nginx_service():
    print('\t',[s()], ' 创建Zookeeper开机自启动文件 ', '\n')
    if not os.path.exists(r_service_dir):
        os.system('mkdir -p ' + r_service_dir)
    nginx_service_file = r_service_dir + 'nginx.service'
    with open(nginx_service_file, 'w',encoding='UTF-8') as f_obj:
        f_obj.write("[Unit]\nDescription=nginx - high performance web server\nDocumentation=http://nginx.org/en/docs/\nAfter=network-online.target remote-fs.target nss-lookup.target\nWants=network-online.target\n\n[Service]\nUser="+common_user+"\nGroup="+common_user+"\nType=forking\nPIDFile=/etc/nginx/nginx.pid\nExecStart=/usr/sbin/nginx -c /etc/nginx/nginx.conf\nExecReload=/bin/kill -s HUP $MAINPID\nExecStop=/bin/kill -s TERM $MAINPID\n\n[Install]\nWantedBy=multi-user.target\n")
    dest_file = '/lib/systemd/system/nginx.service'
    shutil.copyfile(nginx_service_file,dest_file)
    os.system('systemctl daemon-reload')
    for files in ['/etc/logrotate.d/nginx','/etc/nginx','/etc/sysconfig/nginx','/etc/sysconfig/nginx-debug','/usr/lib64/nginx','/usr/libexec/initscripts/legacy-actions/nginx','/usr/share/nginx','/var/cache/nginx','/var/log/nginx']:
        os.system('chown -R ' + common_user + ':'+ common_user + ' ' + files)
    os.system('chown root:root /usr/sbin/nginx && chmod 755 /usr/sbin/nginx')
    os.system('setcap cap_net_bind_service=+eip /usr/sbin/nginx')
    print('\t',[s()]," nginx 重启... ",'\n')
    os.system('/usr/sbin/nginx -s stop')
    os.system('su - ' + common_user +' -c /usr/sbin/nginx')
    os.system('systemctl enable nginx.service')
    nginx_status()
    alert_over(pyname)

################################## 主函数开始 ##################################
def main():
    nginx_init()
    nginx_back()
    nginx_cofing()
    deploy_nginx()
    nginx_service()

if __name__ == '__main__':
    main()