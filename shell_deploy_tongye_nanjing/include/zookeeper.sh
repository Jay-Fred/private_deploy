#JDK
JDK_install(){
    jdk_dir="${software_dir}/jdk"
    Echo_Green "$DATE    [INFO]    Start install JDK!" >> install.log
    [ -f $jdk_dir/java.tar.gz ] || Echo_Red "$DATE    [ERROR]    检查JDK目录是否存在" >> install.log
#tar -zxvf ../software/java.tar.gz -C ../software 2>&1 >/dev/null || echo "$DATE    [ERROR]    检查JDK目录是否存在" >> install.log
    while true
    do
        read -p "请输入要将JDK安装在哪个路径（eg：如/usr/local/software）:" JDK_dir
        if [ ! $JDK_dir ]; then
            echo "请输入正确的路径"
        else
             echo $JDK_dir
             break
        fi

    done

    [ ! -d $JDK_dir ] && mkdir -p ${JDK_dir}
    tar -zxvf $jdk_dir/java.tar.gz -C $JDK_dir 2>&1 >/dev/null
    [ -d ${JDK_dir}/java ] && Echo_Green "$DATE    [INFO]    安装JDK完成" >> install.log
    #判断/etc/profile中是否存在JAVA_HOME变量，如果存在就删掉这个JAVA_HOME
    if [ `grep 'JAVA_HOME' /etc/profile|wc -l` -gt 0 ];then
    Echo_Green  "$DATE    [INFO]    JAVA_HOME在/etc/profile中已存在，准备清除. 清除的变量如下：" >> install.log
    grep 'JAVA_HOME' /etc/profile >> install.log
    #删除JAVA_HOME变量
    sed -i  '/JAVA_HOME/d' /etc/profile
    fi
    [ `grep 'JAVA_HOME' /etc/profile|wc -l` -eq 0 ] && Echo_Green  "$DATE    [INFO]    旧JAVA_HOME变量已清除" >> install.log ||Echo_Red "$DATE    [ERROR]    旧JAVA_HOME变量清空失败."
    #判断/etc/profile中是否存在CLASSPATH变量，如果存在就删掉这个CLASSPATH
    if [ `grep 'CLASSPATH' /etc/profile|wc -l` -gt 0 ];then
    Echo_Green  "$DATE    [INFO]    CLASSPATH在/etc/profile中已存在，准备清除. 清除的变量如下：" >> install.log
    grep 'CLASSPATH' /etc/profile >> install.log
    #删除CLASSPATH变量
    sed -i  '/CLASSPATH/d' /etc/profile
    fi
    [ `grep 'CLASSPATH' /etc/profile|wc -l` -eq 0 ] && Echo_Green  "$DATE    [INFO]    旧CLASSPATH变量已清除" >> install.log ||Echo_Red "$DATE    [ERROR]    旧CLASSPATH变量清空失败."
source /etc/profile
cat >> /etc/profile <<EOF
export JAVA_HOME=${JDK_dir}/java
export PATH=${JDK_dir}/java/bin:$PATH 
export CLASSPATH=.:${JDK_dir}/java/lib/dt.jar:${JDK_dir}/java/lib/tools.jar 
EOF
    source /etc/profile
}

#Zookeeper
Zookeeper_install(){
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

   

    zookeeper_dir="${software_dir}/zookeeper"
    Echo_Green "$DATE    [INFO]    Start install Zookeeper！" >> install.log
    [ -f ${zookeeper_dir}/zookeeper.tar.gz ] || Echo_Red "$DATE    [ERROR]    检查Zookeeper目录是否存在" >> install.log
#&& tar -zxvf ../software/zookeeper.tar.gz -C ../software 2>&1 >/dev/null || echo "$DATE    [ERROR]    检查Zookeeper目录是否存在

    while true
    do
        read -p "请输入要将Zookeeper安装在哪个路径（eg：如/usr/local/software）:" Zookeeper_dir
        if [ ! $Zookeeper_dir ]; then
            echo "请输入正确的路径"
        else
             echo $Zookeeper_dir
             break
        fi

    done

    [ ! -d $Zookeeper_dir ] && mkdir -p ${Zookeeper_dir}
    tar -zxvf ${zookeeper_dir}/zookeeper.tar.gz -C ${Zookeeper_dir} $2>&1 >/dev/null
    [ -f ${Zookeeper_dir}/zookeeper/conf/zoo.cfg ] && sed -i  "s#/usr/local/software/zookeeper-3.4.9#"${Zookeeper_dir}"/zookeeper#g" ${Zookeeper_dir}/zookeeper/conf/zoo.cfg
    [ $? -eq 0 ] && Echo_Green "$DATE    [INFO]    Zookeepe安装成功" >> install.log || Echo_Red "$DATE    [ERROR]    Zookeepe安装失败" >> install.log
    #判断/etc/profile中是否存在ZOOKEEPER_HOME变量，如果存在就删掉这个ZOOKEEPER_HOME
    if [ `grep 'ZOOKEEPER_HOME' /etc/profile|wc -l` -gt 0 ];then
    Echo_Green  "$DATE    [INFO]    ZOOKEEPER_HOME在/etc/profile中已存在，准备清除. 清除的变量如下：" >> install.log
    grep 'ZOOKEEPER_HOME' /etc/profile >> install.log
    #删除ZOOKEEPER_HOME变量
    sed -i  '/ZOOKEEPER_HOME/d' /etc/profile
    fi
    [ `grep 'ZOOKEEPER_HOME' /etc/profile|wc -l` -eq 0 ] && Echo_Green  "$DATE    [INFO]    旧ZOOKEEPER_HOME变量已清除" >> install.log ||Echo_Red "$DATE    [ERROR]    旧ZOOKEEPER_HOME变量清空失败."
source /etc/profile
cat >> /etc/profile <<EOF
export ZOOKEEPER_HOME=${Zookeeper_dir}/zookeeper
export PATH=$PATH:${Zookeeper_dir}/zookeeper/bin
EOF
    source /etc/profile
    chown -R $User:$Group ${Zookeeper_dir}
    su - $User -c "${Zookeeper_dir}/zookeeper/bin/zkServer.sh  start"
    zookeeper_port=`netstat -nltup|grep 2181|wc -l`
    if [ ${zookeeper_port} -eq 1 ]; then
        Echo_Green "$DATE    [INFO]    Zookeeper启动成功！" >> install.log 
    else
        Echo_Red "$DATE    [ERROR]    Zookeeper启动失败！" >> install.log
        exit 1
    fi

}

#Zookeeper修改为集群模式
Zookeeper_cluster(){
    echo ""
    echo "关闭防火墙!"
    systemctl stop firewalld
    Echo_Green "请输入三台Zookeeper的ip地址......."

    while true
    do
        read -p "第1台Zookeeper的Ip地址(eg:192.168.10.1):" Zookeeper_1_ip
        if [ ! $Zookeeper_1_ip ]; then
            echo "请输入正确的Ip"
        else
             echo $Zookeeper_1_ip
             break
        fi

    done

    while true
    do
        read -p "第2台Zookeeper的Ip地址(eg:192.168.10.2):" Zookeeper_2_ip
        if [ ! $Zookeeper_2_ip ]; then
            echo "请输入正确的Ip"
        else
             echo $Zookeeper_2_ip
             break
        fi

    done

    while true
    do
        read -p "第3台Zookeeper的Ip地址(eg:192.168.10.3):" Zookeeper_3_ip
        if [ ! $Zookeeper_3_ip ]; then
            echo "请输入正确的Ip"
        else
             echo $Zookeeper_3_ip
             break
        fi

    done

    while true
    do
        read -p "请输入本机是第几台Zookeeper(eg:第一台填写1,第二台填写2,第三台填写3)" Node_num
        if [ ! $Node_num ]; then
            echo "请输入正确的值"
        else
             echo $Node_num
             break
        fi

    done

#定义配置文件地址
    source /etc/profile
    Zookeeper_config="$ZOOKEEPER_HOME/conf/zoo.cfg"
    #判断zoo.cfg配置文件是否存在server.1|server.2|server.3变量,如果存在就删掉..
    if [ `grep 'server.1' ${Zookeeper_config}|wc -l` -gt 0 ];then
    Echo_Green  "server.1在${Zookeeper_config}中已存在，准备清除..."
    #删除server.1变量
    sed -i  '/server.1/d' ${Zookeeper_config}
    fi
    if [ `grep 'server.2' ${Zookeeper_config}|wc -l` -gt 0 ];then
    Echo_Green  "server.2在${Zookeeper_config}中已存在，准备清除..."
    #删除server.2变量
    sed -i  '/server.2/d' ${Zookeeper_config}
    fi
    if [ `grep 'server.3' ${Zookeeper_config}|wc -l` -gt 0 ];then
    Echo_Green  "server.3在${Zookeeper_config}中已存在，准备清除..."
    #删除server.3变量
    sed -i  '/server.3/d' ${Zookeeper_config}
    fi
cat >> ${Zookeeper_config} <<EOF
server.1=${Zookeeper_1_ip}:2888:3888
server.2=${Zookeeper_2_ip}:2888:3888
server.3=${Zookeeper_3_ip}:2888:3888
EOF

#获取zookeeper环境中dataDir配置的路径
    datadir="${Zookeeper_dir}/zookeeper/data"
#新增myid文件
cat > ${datadir}/myid <<EOF
${Node_num}
EOF

#赋权
    chown -R $User:$Group ${Zookeeper_config}
    chown -R $User:$Group ${datadir}/myid
#重启zookeeper服务
    source /etc/profile
    su - $User -c "${Zookeeper_dir}/zookeeper/bin/zkServer.sh restart"
    sleep 5
    Echo_Green "三台Zookeeper全部启动完毕后，执行${Zookeeper_dir}/zookeeper/bin/zkServer.sh status 查看集群状态"
    Echo_Green "打印Zookeeper的状态信息：Mode:leader为主节点|Mode:follower为从节点"
}

