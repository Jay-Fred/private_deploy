import requests
import json
from env import *

################################## url1 生成流程图 ##################################
################################## url1 生成拓扑图 ##################################
url1 = 'http://10.1.90.216:9090'
url2 = 'http://10.1.90.216:9090/test'
payload = {}
DMZ区 = {}
代理服务器 = {}

for i in proxy_ip:
    代理服务器[proxy_ip] = ["proxy_ip"]
for i in proxy_ip:
    DMZ区[proxy_ip] = [""]
payload["内网区"] = app_list
payload["DMZ区"] = DMZ区
payload["代理服务器"] = 代理服务器
json_data = json.dumps(payload).encode('UTF-8')
proxy = {"http": proxy_ip+":"+proxy_port}
response1 = requests.post(url=url1, data=json_data, proxies=proxy)
time.sleep(5)
response2 = requests.post(url=url2, data=json_data, proxies=proxy)

print(response1.text)
print(response2.text)
