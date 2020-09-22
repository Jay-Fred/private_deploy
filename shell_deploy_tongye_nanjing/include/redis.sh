Redis_install(){

    while true
    do
        read -p "输入服务启动的普通用户:" User
        if [ ! $User ]; then
            echo "请输入正确的用户"
        else
             echo $User
             break
        fi

    done

    while true
    do
        read -p "输入服务启动的普通用户组:" Group
        if [ ! $Group ]; then
            echo "请输入正确的组"
        else
             echo $Group
             break
        fi

    done


    redis_dir="${software_dir}/redis"
    [ ! -d /var/run/redis ] && mkdir -p /var/run/redis
    chown -R $User:$Group /var/run/redis
    Echo_Green "$DATE    [INFO]    Start install Redis!" >> install.log
    [ -f ${redis_dir}/redis.tar.gz ] || Echo_Red "$DATE    [ERROR]    检查Redis安装包不存在" >> install.log

while true
    do
        read -p "请输入要将Redis安装在哪个路径（eg：如/usr/local/software）:" Redis_dir
        if [ ! $Redis_dir ]; then
            echo "请输入正确的路径"
        else
             echo $Redis_dir
             break
        fi

    done

#判断并添加REDIS_HOME
#判断/etc/profile中是否存在REDIS_HOME变量，如果存在就删掉这个REDIS_HOME
    if [ `grep 'REDIS_HOME' /etc/profile|wc -l` -gt 0 ];then
        Echo_Green  "$DATE    [INFO]    REDIS_HOME在/etc/profile中已存在，准备清除. 清除的变量如下：" >> install.log
        grep 'REDIS_HOME' /etc/profile >> install.log
        #删除REDIS_HOME变量
        sed -i  '/REDIS_HOME/d' /etc/profile
    fi
    [ `grep 'REDIS_HOME' /etc/profile|wc -l` -eq 0 ] && Echo_Green  "$DATE    [INFO]    旧REDIS_HOME变量已清除" >> install.log ||Echo_Red "$DATE    [ERROR]    旧REDIS_HOME变量清空失败."
    source /etc/profile
    cat >> /etc/profile <<EOF
export REDIS_HOME=${Redis_dir}/redis
export PATH=$PATH:${Redis_dir}/redis/src
EOF
    source /etc/profile
    [ ! -d $Redis_dir ] && mkdir -p ${Redis_dir}
    tar -zxvf ${redis_dir}/redis.tar.gz 2>&1 >/dev/null -C ${Redis_dir}
    [ -f ${Redis_dir}/redis/config/redis.conf ] &&  sed -i  "s#/usr/local/software#"${Redis_dir}"#g" ${Redis_dir}/redis/config/redis.conf

    Redis_pwd="HzN8m%cr!Vve"
    Echo_Green "$DATE    [INFO]    Redis修改的密码为：$Redis_pwd" >> install.log
    [ -f ${Redis_dir}/redis/config/redis.conf ] && sed -i "s/lhdnapa12#/"$Redis_pwd"/g" ${Redis_dir}/redis/config/redis.conf
    
#赋权
    chown -R $User:$Group ${Redis_dir}/redis
#切换用户启动
    su - $User -c "${Redis_dir}/redis/src/redis-server ${Redis_dir}/redis/config/redis.conf"
    redis_port=`netstat -nltup|grep 6379|wc -l`
    if [ $redis_port -eq 2 ]; then
        Echo_Green "$DATE    [INFO]    Redis启动成功" >> install.log
    else
        Echo_Red "$DATE    [ERROR]   Redis启动失败!" >> install.log
        exit 1
    fi
}
