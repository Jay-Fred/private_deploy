DATE=`date "+%Y-%m-%d %H:%M:%S"`
location=`pwd`
basedir=`echo $location|awk -F "/" '{for(i=1;i<=NF;i++){printf $i"/"}}'`
software_dir="${basedir}software"

clear
echo "+------------------------------------------------------------------------+"
echo "|                           Written by lhxy                              |"
echo "+------------------------------------------------------------------------+"
echo "|        A tool to auto-compile & install lhxy system     on Centos7.4   |"
echo "+------------------------------------------------------------------------+"
echo "|           For more information please visit https://www.lhseer.com     |"
echo "+------------------------------------------------------------------------+"

# Check if user is root
if [ $(id -u) != "0" ]; then
    echo "Error: You must be root to run this script, please use root to install "
    exit 1
fi

. include/init.sh
. include/mysql.sh
. include/redis.sh
. include/tomcat.sh
. include/zookeeper.sh
. include/nginx.sh
. include/supervise.sh
. include/gc.sh
. include/mydumper.sh
. include/tomcat.sh
. include/python3.sh
Check_Env()
{
    Get_Dist_Name
    if [ "${DISTRO}" = "CentOS 7.4" ]; then
        Echo_Green "Linux release is ok|CentOS 7.4"    
    elif [ "${DISTRO}" = "CentOS 7.6" ]; then
        Echo_Green "Linux release is ok|CentOS 7.6"
    elif [ "${DISTRO}" = "Red Hat 7.4" ]; then
        Echo_Green "Linux release is ok|Red Hat 7.4"
    elif [ "${DISTRO}" = "Red Hat 7.6" ]; then
        Echo_Green "Linux release is ok|Red Hat 7.6"
    else
        Echo_Red "Unable to get Linux distribution name, or do NOT support the current distribution."
        exit 1
    fi
    Print_Sys_Info
}


usage(){
cat <<ETF
this scirpt install mysql,zookeeper,redis,tomcat
 USAGE:
    1:check environmental
    2:install mysql
    3:install jdk1.8
    4:install zookeeper
    5:install redis
    6:install tomcat
    7:install nginx
    8:install supervise
    9:install mydumper
    10:install python3
    11.init openfiles(不要重复执行，执行一次即可)
    0:exit
ETF
}

mysql_mode(){
cat <<ETF
 USAGE:
    1:mysql单机模式
    2:mysql主从模式
    0:exit
ETF
}

zookeeper_mode(){
cat <<ETF
 USAGE:
    1:zookeeper单机模式
    2:zookeeper集群模式
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
    read -p "Enter your choice (1, 2, 3, 4, 5, 6, 7, 8,9,10,11 or 0): " Select
    echo $Select
    case $Select in
        "1")
            Print_split
            create_user_group
            Check_Env
            Disable_Selinux
            Stop_Firewalld
            ;;
        "2")
            mysql_mode
            read -p "Enter your choice (1, 2 or 0): " select_mysql_mode
            echo $select_mysql_mode
            case $select_mysql_mode in
            "1")
            Print_split     
            Base
            Mysql_install
            Mysql_User
            move_mysql_startscript 
            ;;
            "2")
            Print_split
            Base
            Mysql_install
            Mysql_User
            Mysql_Master_Slave
            move_mysql_startscript
            ;;
            "0")
            exit 0
            ;; 
            *)
            mysql_mode
            ;;
            esac
            ;;
        "3")
            Print_split
            JDK_install
            ;;
        "4")
            zookeeper_mode
            read -p "Enter your choice (1, 2 or 0): " select_zookeeper_mode
            echo $select_zookeeper_mode
            case $select_zookeeper_mode in
            "1")
            Print_split
            Zookeeper_install
            ;;
            "2")
            Print_split
            Zookeeper_install
            Zookeeper_cluster
            ;;
            "0")
            exit 0
            ;;
            *)
            zookeeper_mode
            ;;
            esac
            ;;
        "5")
            Print_split
            Redis_install
            ;;
        "6")
            Print_split
            Tomcat_Install 
            ;;
        "7")
            Print_split
            Nginx_install
            ;;
        "8")
            Print_split
            Gcc_install
            Supervise_install
            ;;
        "9")
            Print_split
            MyDumper_install
            ;;
        "10")
            Print_split
            python3_install
            ;;
        "11")
            Print_split
            init_openfiles
            ;;

        "0")
            exit 0
            ;;
          *)
            usage
            ;;
    esac
    

done
