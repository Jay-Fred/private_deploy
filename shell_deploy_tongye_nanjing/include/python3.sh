#!/bin/bash
python3_install()
{
    python_package="$software_dir/python3/python3_software"
    [ ! -d /etc/yum.repos.d/yum_bak ] && mkdir -p /etc/yum.repos.d/yum_bak
    mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/yum_bak/
 
    cat > /etc/yum.repos.d/python3.repo <<EOF
[python3]
name=python3
baseurl=file://${python_package}/
gpgcheck=0
enabled=1
EOF
    yum clean all
    yum makecache
    Echo_Green "开始安装python3依赖.." >> install.log
    Echo_Green "开始安装python3依赖.."
    yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gdbm-devel db4-devel libpcap-devel xz-devel gcc-c++
    [ $? -eq 0 ] && Echo_Green "Python3 依赖安装成功.." >> install.log || Echo_Red "Python3 依赖安装失败..." >> install.log
    while true
    do
        read -p "输入python3的解压路径(eg:/usr/local):" python_dir
        if [ ! $python_dir ]; then
            echo "请输入正确的路径"
        else
             echo $python_dir
             break
        fi

    done

    [ ! -d ${python_dir} ] && mkdir -p ${python_dir}
    echo ""
    echo ""
    Echo_Green "开始安装Python3.." 
    Echo_Green "开始安装python3.." >> install.log
    cd $software_dir/python3/Python-3.6.0 && ./configure --prefix=${python_dir}/python3
    cd $software_dir/python3/Python-3.6.0 && make && make install 
    ln -s ${python_dir}/python3/bin/python3 /usr/bin/python3
   
    echo "" 
    echo ""
    ${python_dir}/python3/bin/pip3 install $software_dir/python3/numpy-1.16.2-cp36-cp36m-manylinux1_x86_64.whl
    ${python_dir}/python3/bin/pip3 install $software_dir/python3/scipy-1.2.1-cp36-cp36m-manylinux1_x86_64.whl
    
    Echo_Green "安装Python3完成.."
    Echo_Green "安装python3完成.." >> install.log

}
