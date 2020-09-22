#Nginx
Nginx_install(){

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


if [ ! -d /html ];then
  mkdir /html
  chown -R ${User}:${Group} /html
fi
    nginx_package="${software_dir}/nginx/Package"
    echo "开始安装Nginx"
    rpm -ivh ${nginx_package}/*.rpm
    [ $? -eq 0 ] && Echo_Green "$DATE    [INFO]    Nginx安装完成" >> install.log || Echo_Red "$DATE    [ERROR]    Nginx安装失败" >> install.log
    [ -f /etc/nginx/conf.d/default.conf ] && mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf_bak
    cp ${nginx_package}/80.interbank.conf /etc/nginx/conf.d/
#替换Nginx启动用户nginx为指定启动用户
    sed -i '/user  nginx;/d' /etc/nginx/nginx.conf
    sed -i "s#/var/run/nginx.pid;#/etc/nginx/nginx.pid;#g" /etc/nginx/nginx.conf
#替换interbank实际ip地址及端口

#Nginx版本号隐藏
    Echo_Green "关闭Nginx版本号展示..."
    sed -i 's#gzip  on;#gzip  on;\n    server_tokens  off;#g' /etc/nginx/nginx.conf
while true
    do
        read -p "输入interbank-client服务部署的ip地址.(eg:192.168.1.100):" interbank_client_ip
        if [ ! $interbank_client_ip ]; then
            echo "请输入正确的ip地址"
        else
             echo $interbank_client_ip
             break
        fi

    done

while true
    do
        read -p "输入interbank-client服务部署的port端口.(eg:8888):" interbank_client_port
        if [ ! $interbank_client_port ]; then
            echo "请输入正确的端口号"
        else
             echo $interbank_client_port
             break
        fi

    done

    sed -i "s/127.0.0.1:8888/${interbank_client_ip}:${interbank_client_port}/g" /etc/nginx/conf.d/80.interbank.conf
    /usr/sbin/nginx 
    echo "开始替换nginx systemctl配置文件"
cat > /lib/systemd/system/nginx.service <<EOF
[Unit]
Description=nginx - high performance web server
Documentation=http://nginx.org/en/docs/
After=network-online.target remote-fs.target nss-lookup.target
Wants=network-online.target

[Service]
User=$User
Group=$Group
Type=forking
PIDFile=/etc/nginx/nginx.pid
ExecStart=/usr/sbin/nginx -c /etc/nginx/nginx.conf
ExecReload=/bin/kill -s HUP $MAINPID
ExecStop=/bin/kill -s TERM $MAINPID

[Install]
WantedBy=multi-user.target
EOF
    systemctl daemon-reload   
    echo "开始为Nginx相关文件赋权"
    chown $User:$Group /etc/logrotate.d/nginx
    chown -R $User:$Group /etc/nginx
    chown $User:$Group /etc/sysconfig/nginx
    chown $User:$Group /etc/sysconfig/nginx-debug
    chown -R $User:$Group /usr/lib64/nginx
    chown -R $User:$Group /usr/libexec/initscripts/legacy-actions/nginx
    chown -R $User:$Group /usr/share/nginx
    chown -R $User:$Group /var/cache/nginx
    chown -R $User:$Group /var/log/nginx

    chown root:root /usr/sbin/nginx
    chmod 755 /usr/sbin/nginx
    setcap cap_net_bind_service=+eip /usr/sbin/nginx 
    echo "Nginx重启"
    /usr/sbin/nginx -s stop
    su - $User -c '/usr/sbin/nginx'
    systemctl enable nginx.service
}
