#!/bin/bash
Tomcat_Install()
{
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


    tomcat_dir="${software_dir}"/tomcat
    Echo_Green "$DATE    [INFO]    Start install Tomcat!" >> install.log
    [ -f ${tomcat_dir}/tomcat.tar.gz ] || Echo_Red "$DATE    [ERROR]    检查Tomcat安装包不存在" >> install.log

    while true
    do
        read -p "请输入要将Tomcat安装在哪个路径（eg：如/usr/local/installed）:" Tomcat_dir
        if [ ! $Tomcat_dir ]; then
            echo "请输入正确的路径"
        else
             echo $Tomcat_dir
             break
        fi

    done

    [ ! -d $Tomcat_dir ] && mkdir -p ${Tomcat_dir}
    tar -zxvf ${tomcat_dir}/tomcat.tar.gz 2>&1 >/dev/null -C ${Tomcat_dir}
    if [ `grep 'TOMCAT_HOME' /etc/profile|wc -l` -gt 0 ]; then
        echo "$DATE    [INFO]    TOMCAT_HOME在/etc/profile中已存在,开始清除" >> install.log
        #删除TOMCAT_HOME变量
        sed -i  '/TOMCAT_HOME/d' /etc/profile
        [ `grep 'TOMCAT_HOME' /etc/profile|wc -l` -eq 0 ] && Echo_Green "$DATE    [INFO]    旧TOMAT_HOME变量已清除" >> install.log ||Echo_Red "$DATE    [ERROR]    旧TOMCAT_HOME变>量清空失败."
    fi

    echo "export TOMCAT_HOME=${Tomcat_dir}" >> /etc/profile
    sed -i "s#/usr/local/installed#"${Tomcat_dir}"#g" ${Tomcat_dir}/tomcat-*/bin/catalina.sh
    if [ $? -eq 0 ]; then
        Echo_Green "$DATE    [INFO]  Tomcat安装成功" >> ${basedir}install.log
    else
        Echo_Red "$DATE    [ERROR]  Tomcat安装失败" >> ${basedir}install.log
        exit 1
    fi

#新建程序所需目录
[ ! -d  /usr/local/installed/interbank/ratingReport/ ] && mkdir -p /usr/local/installed/interbank/ratingReport/
[ ! -d  /usr/local/installed/interbank/financeExcel/ ] && mkdir -p /usr/local/installed/interbank/financeExcel/
[ ! -d  /usr/local/installed/interbank/mybondExcel/ ] && mkdir -p /usr/local/installed/interbank/mybondExcel/
[ ! -d  /usr/local/installed/interbank/excel/ ] && mkdir -p /usr/local/installed/interbank/excel/
[ ! -d  /usr/local/installed/interbank/taskFile/ ] && mkdir -p /usr/local/installed/interbank/taskFile/
[ ! -d  /usr/local/installed/interbank/logo/ ] && mkdir -p /usr/local/installed/interbank/logo/
[ ! -d  /usr/local/installed/interbank/batchSaveUserExcel/ ] && mkdir -p /usr/local/installed/interbank/batchSaveUserExcel/
[ ! -d  /usr/local/installed/interbank/ibApiFile/ ] && mkdir -p /usr/local/installed/interbank/ibApiFile/
[ ! -d  /usr/local/installed/ocx/ocx/ ] && mkdir -p /usr/local/installed/ocx/ocx/

chown -R $User:$Group /usr/local/installed/interbank
chown -R $User:$Group /usr/local/installed/ocx

#为安装的Tomcat路径赋权
chown -R $User:$Group ${Tomcat_dir}/tomcat*
}
