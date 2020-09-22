#!/bin/bash
MyDumper_install(){
    mydumper_package="$software_dir/mydumper/Package"
    [ ! -d /etc/yum.repos.d/yum_bak ] && mkdir -p /etc/yum.repos.d/yum_bak
    mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/yum_bak/
    DATE=`date "+%Y-%m-%d %H:%M:%S"`
    location=`pwd`
    Echo_Green "$DATE    [INFO]    Start install mydumper!" >> install.log

#添加判断空值
    while true
    do
        read -p "请输入要将Mydumper安装在哪个路径（eg：如/usr/local/software）:" Mydumper_dir
        if [ ! $Mydumper_dir ]; then
            echo "请输入正确的目录"
        else
             echo Mydumper_dir
             break
        fi
    done

    [ ! -d ${Mydumper_dir} ] && mkdir -p ${Mydumper_dir}
    tar -zxvf $software_dir/mydumper/mydumper-0.9.1.tar.gz -C $Mydumper_dir 2>&1 >/dev/null
cat > /etc/yum.repos.d/mydumper.repo <<EOF
[MyDumper]
name=MyDumper
baseurl=file://${mydumper_package}/
gpgcheck=0
enabled=1
EOF
    yum clean all
    yum makecache
    yum install gcc-c++ -y
    yum install -y cmake
    yum install glib2-devel mysql-devel zlib-devel pcre-devel -y
    cd $Mydumper_dir/mydumper-0.9.1 && cmake ./ && make && make install
    if [ $? -eq 0 ]; then
        Echo_Green "$DATE    [INFO]  MyDumper make操作成功" >> ${basedir}install.log 
    else
        Echo_Red "$DATE    [ERROR]  MyDumper make操作失败" >> ${basedir}install.log
        exit 1
    fi
}

