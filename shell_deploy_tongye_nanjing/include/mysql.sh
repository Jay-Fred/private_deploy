mysql_package="$software_dir/mysql/Package"
DATE=`date "+%Y-%m-%d %H:%M:%S"`
#备份原yum源，配置本地yum源
Base(){
    echo "安装依赖"
    mkdir -p /etc/yum.repos.d/yum_bak
    [ -d /etc/yum.repos.d/yum_bak ] && mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/yum_bak || Echo_Red "$DATE    [ERROR]    Yum源备份失败" >> install.log
    cat > /etc/yum.repos.d/Mysql_Redis.repo <<EOF
[Mysql_Redis]
name=Mysql_Redis
baseurl=file://${mysql_package}/
gpgcheck=0
enabled=1
EOF
    yum clean all
    yum makecache
}

Mysql_install(){
    Echo_Green "开始创建Mysql用户，初始密码为:mysql"
    groupadd mysql
    useradd -g mysql mysql
    echo 'mysql' |passwd --stdin mysql
    Echo_Green "$DATE    [INFO]    install mysql start...." >> install.log
    yum -y install mysql-community-server
    systemctl start mysqld
    systemctl enable mysqld
    systemctl daemon-reload
    while true
    do
        read -p "输入Mysql的安装路径为:(eg:/usr/local/mysql):" mysql_basedir
        if [ ! $mysql_basedir ]; then
            echo "请输入正确的目录"
        else
             echo $mysql_basedir
             break
        fi

    done 
    [ ! -d ${mysql_basedir}/mysql ] && mkdir -p ${mysql_basedir}/mysql
    [ ! -d ${mysql_basedir}/mysql/log ] && mkdir -p ${mysql_basedir}/mysql/log/
    [ ! -d ${mysql_basedir}/mysql/data ] && mkdir -p  ${mysql_basedir}/mysql/data
    mv /etc/my.cnf /etc/my.cnf_bak
    cp $software_dir/mysql/my.cnf /etc/my.cnf
    sed -i "s#/usr/local#$mysql_basedir#g" /etc/my.cnf
    cp -r /var/lib/mysql/* ${mysql_basedir}/mysql/data
    [ $? -eq 0 ] && Echo_Green "$DATE    [INFO]    Mysql配置文件变量替换完毕!" >> install.log || Echo_Red "$DATE    [ERROR]    Mysql变量替换失败！>> install.log"
    touch $mysql_basedir/mysql/log/mysql-slow.log
    touch $mysql_basedir/mysql/log/mysql.err
    chown -R mysql:mysql ${mysql_basedir}/mysql
    systemctl daemon-reload
    systemctl restart mysqld
    [ -L /var/lib/mysql/mysql.sock ] && rm -rf  /var/lib/mysql/mysql.sock
    ln -s ${mysql_basedir}/mysql/log/mysql.sock /var/lib/mysql/mysql.sock
#赋权
    chown -R mysql:mysql ${mysql_basedir}/mysql
    chown -R mysql:mysql /etc/my.cnf
    chown -R mysql:mysql /var/lib/mysql/mysql.sock
    chown -R mysql:mysql /usr/share/mysql
    chown -R mysql:mysql /var/run/mysqld
}

Mysql_User(){
    port_3306=`netstat -nltup|grep 3306|wc -l`
    [ $port_3306 -eq 1 ] && Echo_Green "$DATE    [INFO]    Mysql启动成功" >> install.log || Echo_Red "$DATE    [ERROR]    Mysql启动失败，请查看！"
    tem_root=`cat /var/log/mysqld.log |grep 'root@localhost'|cut -d ':' -f 4`
#备注 mysql5.7默认密码策略要求密码必须是大小写字母数字特殊字母的组合，至少8位
    root_pwd="HzN8m%cr!Vve"   


    mysql -uroot --connect-expired-password  -p`echo ${tem_root}` <<EOF 
ALTER USER 'root'@'localhost' IDENTIFIED BY "${root_pwd}";
grant all privileges on *.* to "root"@'%' identified by "${root_pwd}";
flush privileges;
EOF
    [ $? -eq 0 ] && Echo_Green "$DATE    [INFO]    Mysql_Root_passwd修改为:${root_pwd}">> install.log || Echo_Red "$DATE    [ERROR]    Mysql_Root_passwd修改失败" >> install.log
}

#恢复yum源
Restore_yum(){
    cp -r /etc/yum.repos.d/yum_bak/* /etc/yum.repos.d/
}

#配置mysql主从
Mysql_Master_Slave(){
    echo ""
    Echo_Yellow "开始配置Mysql主从同步..."
    Echo_Green "关闭防火墙"
    systemctl stop firewalld

while true
    do
        read -p "输入Mysql主节点ip:" Mysql_Master_ip
        if [ ! $Mysql_Master_ip ]; then
            echo "请输入正确的ip"
        else
             echo $Mysql_Master_ip
             break
        fi

    done

while true
    do
        read -p "输入Mysql从节点ip:" Mysql_Slave_ip
        if [ ! $Mysql_Slave_ip ]; then
            echo "请输入正确的ip"
        else
             echo $Mysql_Slave_ip
             break
        fi

    done

while true
    do
        read -p "输入本机ip的最后一个字段(eg:192.168.1.200，则输入200):" num_id
        if [ ! $num_id ]; then
            echo "请输入正确的值"
        else
             echo $num_id
             break
        fi

    done

#开启binlog日志
    #判断my.cnf配置文件是否存在log_bin|server_id变量,如果存在就删掉..
    if [ `grep 'log_bin' /etc/my.cnf|wc -l` -gt 0 ];then
    Echo_Green  "log_bin在/etc/my.cnf中已存在，准备清除..."
    #删除log_bin变量
    sed -i  '/log_bin/d' /etc/my.cnf
    fi
    if [ `grep 'server_id' /etc/my.cnf|wc -l` -gt 0 ];then
    Echo_Green  "server_id在/etc/my.cnf中已存在，准备清除..."
    #删除server_id变量
    sed -i  '/server_id/d' /etc/my.cnf
    fi
cat >> /etc/my.cnf <<EOF
log_bin=mysql-bin
server_id=${num_id}
EOF

#删除auto.cnf文件,两台机器此文件值不能一致，删除重启会新生成新的文件...
    [ -f ${mysql_basedir}/mysql/data/auto.cnf ] && rm -rf ${mysql_basedir}/mysql/data/auto.cnf
#重启mysql
    systemctl restart mysqld
#区分主从节点
    while true
    do
        read -p "此台机器是master主节点还是slave从节点..(eg:master|slave):" mode
        if [ ! $mode ]; then
            echo "请输入正确的值"
        else
             echo $mode
             break
        fi

    done

    if [ $mode = "master" ];then
    Echo_Green "开始配置Master节点..."
#创建主从同步所需用户
mysql -uroot --connect-expired-password  -p`echo ${root_pwd}` <<EOF
grant replication slave on *.* to "repl"@"${Mysql_Slave_ip}" identified by "HzN8m%cr!Vve";
flush privileges;
EOF
#打印master同步信息
    echo ""
    Echo_Green "打印maste同步信息-----File|Position字段须记住,从机配置需要填写这两个字段的参数."
    mysql -uroot --connect-expired-password  -p`echo ${root_pwd}` -e 'show master status\G' |grep -w -E 'File|Position'

    elif [ $mode = "slave" ];then
    Echo_Green "开始配置Slave节点..."

while true
    do
    read -p "请输入主节点上输出的Master信息;File(eg:mysql-bin.000001):" File
        if [ ! $File ]; then
            echo "请输入正确的值"
        else
             echo $File
             break
        fi

    done

while true
    do
    read -p "请输入主节点上输出的Slave信息;Position(eg:906):" Position

        if [ ! $Position ]; then
            echo "请输入正确的值"
        else
             echo $Position
             break
        fi

    done

#配置从库
    mysql -uroot --connect-expired-password  -p`echo ${root_pwd}` <<EOF
change master to master_host="${Mysql_Master_ip}",master_user='repl',master_password='HzN8m%cr!Vve',master_log_file="${File}",master_log_pos=${Position};
start slave;
EOF
    Echo_Green "打印Slave同步信息"
    Echo_Yellow "Slave_IO_Running,Slave_SQL_Running 都为Yes的时候表示配置成功.."
    mysql -uroot --connect-expired-password  -p`echo ${root_pwd}` -e 'show slave status\G' |grep -w -E 'Slave_IO_Running|Slave_SQL_Running'
    fi
}




move_mysql_startscript(){
cat > ${mysql_basedir}/mysql/mysqld.sh  <<EOF
#!/bin/bash
. /etc/init.d/functions
. /etc/profile
[ \$# -ne 1 ] && {
echo "USAGE:{start|stop|restart}"
exit 1
}
start(){
if [ -e /var/run/mysqld/mysqld.pid ]
then
  echo "MySQL is running."
else
  /usr/sbin/mysqld --daemonize  --pid-file=/var/run/mysqld/mysqld.pid
  action  "MySQL is starting" /bin/true
  exit 0
fi
}

stop(){
if [ -e /var/run/mysqld/mysqld.pid ]
then
  /usr/bin/mysqladmin -uroot -p'`echo ${root_pwd}`' -S ${mysql_basedir}/mysql/log/mysql.sock shutdown
  action "MySQL is stoping" /bin/true
else
  action "MySQL is stoping" /bin/false
  exit 1
fi
}

restart(){
  stop
  sleep 5
  start
}
if [ "\$1" == "start" ]
then
  start
elif [ "\$1" == "stop" ]
then
  stop
elif [ "\$1" == "restart" ]
then
  restart
else
  echo "USAGE:{start|stop|restart}"
fi
EOF
chmod 777 ${mysql_basedir}/mysql/mysqld.sh
chown -R mysql:mysql ${mysql_basedir}/mysql

}
