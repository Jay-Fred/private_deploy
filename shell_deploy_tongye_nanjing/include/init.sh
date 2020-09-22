init_openfiles(){
cat >> /etc/security/limits.conf <<EOF
* soft nofile 65536      # open files  (-n)
* hard nofile 65536
EOF

}


Disable_Selinux()
{
    setenforce 0
    if [ -s /etc/selinux/config ]; then
        sed -i 's/^SELINUX=.*/SELINUX=disabled/g' /etc/selinux/config
    fi
}

Stop_Firewalld()
{
    systemctl stop firewalld
    systemctl disable firewalld.service
}

Get_Dist_Name()
{
    if grep -Eqi "CentOS" /etc/issue || grep -Eq "CentOS" /etc/*-release && grep -qiE 7.4 /etc/*-release; then
        DISTRO='CentOS 7.4'
    else 
        DISTRO='other'
    fi    
}

Print_split()
{
    echo "=================================================" >> ${basedir}install.log
}
Print_Sys_Info()
{
    echo "${DISTRO}"
    uname -a
    MemTotal=`free -m | grep Mem | awk '{print  $2}'`
    echo "Memory is: ${MemTotal} MB "
    df -h
}

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

Echo_Blue()
{
  echo $(Color_Text "$1" "34")
}


create_user_group()
{
  read -p "请输入要创建的组(eg:lhwork)" group_name
  #判断组是否存在
  grep -E -w "^${group_name}" /etc/group > /dev/null
  if [ $? -eq 0 ];then
     Echo_Red "${group_name} 组已存在..."
  else
     Echo_Green "正在创建${group_name}组..."
     groupadd ${group_name}
  fi
  read -p "请输入要创建的用户(eg:lhwork)" user_name
  #判断用户是否存在
  grep -E -w "^${user_name}" /etc/passwd > /dev/null
  if [ $? -eq 0 ];then
     Echo_Red "${user_name} 用户已存在..."
  else
     Echo_Green "正在创建${user_name}用户..."
     useradd -g ${group_name} ${user_name}
  fi
 
  #修改密码
  echo "HzN8m%cr!Vve" | passwd --stdin ${user_name}
  Echo_Green "修改${user_name}密码，新密码为:HzN8m%cr!Vve"
}
