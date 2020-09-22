#!/bin/bash
Gcc_install()
{
    gcc_package="$software_dir/mydumper/Package"
    [ ! -d /etc/yum.repos.d/yum_bak ] && mkdir -p /etc/yum.repos.d/yum_bak
    mv /etc/yum.repos.d/*.repo /etc/yum.repos.d/yum_bak/
 
    cat > /etc/yum.repos.d/Gcc.repo <<EOF
[Gcc]
name=Gcc
baseurl=file://${gcc_package}/
gpgcheck=0
enabled=1
EOF
    yum clean all
    yum makecache
    yum install gcc-c++ -y

}
