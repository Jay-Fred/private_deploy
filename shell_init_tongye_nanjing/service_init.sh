#!/bin/bash

read -p "Enter your Start User: " User
read -p "Enter your Start Group: " Group


Color_Text()
{
  echo -e " \e[0;$2m$1\e[0m"
}

Echo_Red()
{
  echo $(Color_Text "$1" "31")
}

Echo_Green()
{
  echo $(Color_Text "$1" "32")
}

Echo_Yellow()
{
  echo $(Color_Text "$1" "33")
}


#服务自启动情况监测 
check_init(){
    service_list=(nginx.service mysqld.service zookeeper.service redis.service Tomcat.service)
    for i in ${service_list[@]};do
    status=`systemctl list-unit-files $i |awk 'NR==2{print $2}'`
    if [ ! $status ];then
    Echo_Yellow "服务:$i 尚未部署开机自启动"
    elif [ $status = enabled ];then
    Echo_Green "服务:$i 已开启自启动"
    elif [ $status = disabled ];then
    Echo_Red "服务:$i 未开启自启动"
    fi
    done
}


#Nginx开启自启动
Nginx_init_enable(){
    systemctl enable nginx.service  2>&1 >/dev/null
    [ $? -eq 0 ] && Echo_Green "Nginx开机自启动设置成功" || Echo_Red "Nginx开机自启动设置失败"    
}

#Nginx关闭自启动
Nginx_init_disable(){
    systemctl disable nginx.service 2>&1 >/dev/null
    [ $? -eq 0 ] && Echo_Green "Nginx关闭开机自启动设置成功" || Echo_Red "Nginx关闭开机自启动设置失败"
}

#Mysql开启自启动
Mysql_init_enable(){
    systemctl enable mysqld.service 2>&1 >/dev/null
    [ $? -eq 0 ] && Echo_Green "Mysql开机自启动设置成功" || Echo_Red "Mysql开机自启动设置失败"    
}

#Mysql关闭自启动
Mysql_init_disable(){
    systemctl disable mysqld.service 2>&1 >/dev/null
    [ $? -eq 0 ] && Echo_Green "Mysql关闭开机自启动设置成功" || Echo_Red "Mysql关闭开机自启动设置失败"
}

#Zookeeper配置开机自启动
Zookeeper_init_install(){
    source /etc/profile
cat > /lib/systemd/system/zookeeper.service <<EOF
[Unit]
Description=Zookeeper service
After=network.target
[Service]
User=$User
Group=$Group
SyslogIdentifier=root
Environment=ZHOME=$ZOOKEEPER_HOME
PIDFile=${ZOOKEEPER_HOME}/data/zookeeper_server.pid
ExecStart=$JAVA_HOME/bin/java \
  -Dzookeeper.log.dir=\${ZHOME}/logs/zookeeper.log \
  -Dzookeeper.root.logger=INFO,ROLLINGFILE \
  -cp \${ZHOME}/zookeeper-3.4.9.jar:\${ZHOME}/lib/* \
  -Dlog4j.configuration=file:\${ZHOME}/conf/log4j.properties \
  -Dcom.sun.management.jmxremote \
  -Dcom.sun.management.jmxremote.local.only=false \
  org.apache.zookeeper.server.quorum.QuorumPeerMain \
  \${ZHOME}/conf/zoo.cfg
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
}

#Zookeeper开启自启动
Zookeeper_init_enable(){
    systemctl enable zookeeper.service 2>&1 >/dev/null
    [ $? -eq 0 ] && Echo_Green "Zookeeper开机自启动设置成功" || Echo_Red "Zookeeper开机自启动设置失败" 
}

#Zookeeper关闭自启动
Zookeeper_init_disable(){
   systemctl disable zookeeper.service 2>&1 >/dev/null
   [ $? -eq 0 ] && Echo_Green "Zookeeper关闭开机自启动设置成功" || Echo_Red "Zookeeper关闭开机自启动设置失败"
}

#Redis配置开机自启动
Redis_init_install(){
    source /etc/profile
cat > /lib/systemd/system/redis.service <<EOF
[Unit]
Description=Redis
After=network.target
[Service]
User=$User
Group=$Group
Type=forking
ExecStart=$REDIS_HOME/src/redis-server $REDIS_HOME/config/redis.conf
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s QUIT $MAINPID
PrivateTmp=true
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
}

#Redis开启自启动
Redis_init_enable(){
    systemctl enable redis.service 2>&1 >/dev/null
    [ $? -eq 0 ] && Echo_Green "Redis开机自启动设置成功" || Echo_Red "Redis开机自启动设置失败" 
}

#Redis关闭自启动
Redis_init_disable(){
   systemctl disable redis.service 2>&1 >/dev/null
   [ $? -eq 0 ] && Echo_Green "Redis关闭开机自启动设置成功" || Echo_Red "Redis关闭开机自启动设置失败"
}

Tomcat_init_install(){
    source /etc/profile
    Tomcat_script=`cd $(dirname $0);pwd`/tomcat_init.sh
cat > /lib/systemd/system/Tomcat.service <<EOF
[Unit]
Description=Tomcat
After=network.target
After=zookeeper.service
After=redis.service
After=mysqld.service
After=nginx.service
[Service]
User=$User
Group=$Group
Type=forking
ExecStart=${Tomcat_script} &
TimeoutSec=0
TimeoutStopSec=30
[Install]
WantedBy=multi-user.target
EOF
    #判断rc-local.service是否存在TimeoutStopSec变量
    if [ `grep 'TimeoutStopSec' /lib/systemd/system/rc-local.service|wc -l` -gt 0 ];then
    Echo_Green  "TimeoutStopSec在/lib/systemd/system/rc-local.service中已存在，准备清除."
    #删除已存在的TimeoutStopSec变量
    sed -i  '/TimeoutStopSec/d' /lib/systemd/system/rc-local.service
    fi
    [ `grep 'TimeoutStopSec' /lib/systemd/system/rc-local.service|wc -l` -eq 0 ] && Echo_Green  "旧TimeoutStopSec变量已清除"||Echo_Red "旧TimeoutStopSec变量清空失败."
    source /etc/profile
    echo "TimeoutStopSec=30" >> /lib/systemd/system/rc-local.service
    Echo_Green  "TimeoutStopSec=30变量已添加"

systemctl daemon-reload
}

#Tomcat开启自启动
Tomcat_init_enable(){
    systemctl enable Tomcat.service 2>&1 >/dev/null
    [ $? -eq 0 ] && Echo_Green "Tomcat开机自启动设置成功" || Echo_Red "Tomcat开机自启动设置失败"
}

#Tomcat关闭自启动
Tomcat_init_disable(){
   systemctl disable Tomcat.service 2>&1 >/dev/null
   [ $? -eq 0 ] && Echo_Green "Tomcat关闭开机自启动设置成功" || Echo_Red "Tomcat关闭开机自启动设置失败"
}


usage(){
cat <<ETF
this scirpt service_init(Nginx,Mysql,Zookeeper,Redis)
 USAGE:
    1:检查服务的自启动是否部署
    2:Nginx开启自启动
    3:Nginx关闭自启动
    4:Mysql开启自启动
    5:Mysql关闭自启动
    6:Zookeeper新增自启动服务(如系统中尚未配置)
    7:Zookeeper开启自启动
    8:Zookeeper关闭自启动
    9:Redis新增自启动服务(如系统中尚未配置)
    10:Redis开启自启动
    11:Redis关闭自启动
    12:Tomcat服务设置开机自启动
    13:Tomcat开启自启动
    14:Tomcat关闭自启动
    0:exit
ETF
}
if [ "$1" = "--help" ]; then
    echo "you shuold run $0"
    usage
    exit 0
fi

while true
do
    usage
    read -p "Enter your choice (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 or 0): " Select
    echo $Select
    case $Select in
        "1")
            check_init
            ;;
        "2")
            Nginx_init_enable
	    ;;
        "3")
            Nginx_init_disable
            ;;
        "4")
            Mysql_init_enable
            ;;
        "5")
            Mysql_init_disable
            ;;
        "6")
            Zookeeper_init_install
            ;;
        "7")
            Zookeeper_init_enable
            ;;
        "8")
            Zookeeper_init_disable
            ;;
        "9")
            Redis_init_install
            ;;
        "10")
            Redis_init_enable
            ;;
        "11")
            Redis_init_disable
            ;;
        "12")
            Tomcat_init_install             
            ;;
        "13")
            Tomcat_init_enable
            ;;
        "14")
            Tomcat_init_disable
            ;;
        "0")
            exit 0
            ;;
          *)
            usage
            ;;
    esac
done
