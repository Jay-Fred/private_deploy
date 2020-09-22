#!/bin/bash
#安装supervise

Supervise_install()
{ 
    supervise_dir="${software_dir}/supervise"
    Echo_Green "$DATE    [INFO]    install supervise start...." >> install.log
    [ -f ${supervise_dir}/admin.tar.gz ] || Echo_Red "$DATE    [ERROR]    检查supervise安装包不存在" >> install.log
    while true
    do
        read -p "请输入要将Supervise安装在哪个路径（eg：如/usr/local/software）:" Supervise_dir
        if [ ! $Supervise_dir ]; then
            echo "请输入正确的路径"
        else
             echo $Supervise_dir
             break
        fi

    done

    [ ! -d $Supervise_dir ] && mkdir -p ${Supervise_dir}
    tar -zxvf ${supervise_dir}/admin.tar.gz 2>&1 >/dev/null -C ${Supervise_dir}
    cd ${Supervise_dir}/admin/daemontools-0.76 && package/install
    if [ $? -eq 0 ]; then
        Echo_Green "$DATE    [INFO]    supervise安装成功" >> ${basedir}install.log
    else
        Echo_Red "$DATE    [ERROR]    supervise安装失败" >> ${basedir}install.log
    fi
}
