#!/bin/bash

#tomcat部署启动顺序流程：
#1.tomcat-8.0.30-decision-server-8388
#2.tomcat-8.0.30-interbank-server-8788
#3.tomcat-8.0.30-interbank-quartz-8988
#4.tomcat-8.0.30-monitor-server-8188
#5.tomcat-8.0.30-monitor-web-8288
#6.tomcat-8.0.30-interbank-client-8888
#7.tomcat-8.0.30-datatransfer-client-8080

    source /etc/profile
#启动顺序为
    tomcat_service=(tomcat-8.0.30-decision-server-8388 tomcat-8.0.30-interbank-server-8788 tomcat-8.0.30-interbank-quartz-8988 tomcat-8.0.30-monitor-server-8188 tomcat-8.0.30-monitor-web-8288 tomcat-8.0.30-interbank-client-8888 tomcat-8.0.30-datatransfer-client-8080)
    for i in ${tomcat_service[@]};do
    if [ -d /service/$i ];then
      cd /service;nohup supervise /service/$i >/dev/null 2>&1 &
      sleep 60
    fi
done

exit 0
