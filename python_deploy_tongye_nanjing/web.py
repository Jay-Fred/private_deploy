from flask import Flask, request, jsonify
from graphviz import Digraph,Graph
import json,time,datetime

app = Flask(__name__)
today_time = lambda:time.strftime('%Y-%m-%d_%H_%M_%S')

################################## / 请求路径生成流程图 ##################################
@app.route('/', methods=['POST'])
def get_data1():
    g = Digraph('G', format="pdf")
    g.attr(compound='true')
    data =  json.loads(request.get_data().decode('UTF-8'))
    print(data)
    area_list = []
    for x in data.keys():
        area_list.append(x)

    def draw():
        try:
            g.edge(nmm + "\n" + nnn, "interbank-client\n" + o, color="blue", ltail="clusterF")
        except Exception:
            pass
        try:
            g.edge("interbank-client\n" + o, tt + "\n" + kk, color="blue", lhead="clusterC")
        except Exception:
            pass
        try:
            g.edge("interbank-client\n" + o, mmm + "\n" + mnn, color="blue")
        except Exception:
            pass
        try:
            g.edge("interbank-client\n" + o, rmm + "\n" + rnn, color="blue", lhead="clusterI")
        except Exception:
            pass
        try:
            g.edge("interbank-client\n" + o, mm + "\n" + nn, color="blue", lhead="clusterG")
        except Exception:
            pass

    if "DMZ区" in area_list:
        with g.subgraph(name="clusterA") as bb:
            bb.attr(label="DMZ区", bgcolor="#F0F8FF", fontname="Microsoft YaHei", fontcolor="red", style="rounded",
                    gradientangle="500")
            with bb.subgraph(name="clusterB") as p, bb.subgraph(name="clusterC") as p:
                for rr, ee in data["DMZ区"].items():
                    p.attr(label="", bgcolor="#DCDCDC", fontname="Microsoft YaHei", fontcolor="red", style="dotted",
                           gradientangle="200")
                    for zz in ee:
                        p.attr(label="", bgcolor="#CCCC99", style="rounded", gradientangle="500")
                        p.attr("node", shape="box", style="filled", gradientangle="90")
                        p.node(zz + "\n" + rr)
                for kk, jj in data["代理服务器"].items():
                    p.attr(label="", bgcolor="#DCDCDC", fontname="Microsoft YaHei", fontcolor="red", style="dotted",
                           gradientangle="200")
                    for tt in jj:
                        p.attr(label="代理服务器", bgcolor="#CDC9C9", style="dotted", gradientangle="200")
                        p.attr("node", shape="box", style="filled", gradientangle="90")
                        p.node(tt + "\n" + kk)

        with g.subgraph(name="clusterD") as b:
            b.attr(label="内网区", bgcolor="#FFEFD5", fontname="Microsoft YaHei", fontcolor="red", style="rounded",
                   gradientangle="500")
            with b.subgraph(name="clusterE") as t, b.subgraph(name="clusterF") as yy, b.subgraph(
                    name="clusterG") as d, b.subgraph(name="clusterH") as e, b.subgraph(name="clusterI") as f:
                t.attr(label="Tomcat", color="white", bgcolor="#CCCC99", style="rounded", gradientangle="500")
                t.attr("node", shape="box", style="filled", gradientangle="90")
                yy.attr(label="Nginx", style="rounded", bgcolor="#FFFFE0", gradientangle="500")
                yy.attr("node", shape="box", style="filled", gradientangle="90")
                d.attr(label="Zookeeper", bgcolor="#FFF0F5", style="rounded", gradientangle="500")
                d.attr("node", shape="box", style="filled", gradientangle="90")
                e.attr(label="Mysql", style="rounded", bgcolor="#B0E0E6", gradientangle="500")
                e.attr("node", shape="box", style="filled", gradientangle="90")
                f.attr(label="Redis", style="rounded", bgcolor="#FFFFE0", gradientangle="500")
                f.attr("node", shape="box", style="filled", gradientangle="90")
                dicts = {};
                mysql = {};
                redis = {};
                nginx = {}
                for o, p in data["内网区"].items():
                    for pp in p:
                        if "zookeeper" in pp:
                            dicts[o] = pp
                        if "mysql" in pp:
                            mysql[o] = pp
                        if "redis" in pp:
                            redis[o] = pp
                        if "nginx" in pp:
                            nginx[o] = pp
                        if "interbank-client" in pp:
                            t.node("interbank-client\n" + o)
                        if "interbank-server" in pp:
                            t.node("interbank-server\n" + o)
                for nmm, nnn in nginx.items():
                    if "nginx" in nnn:
                        yy.node(nmm + "\n" + nnn)
                for mm, nn in dicts.items():
                    if "zookeeper" in nn:
                        d.node(mm + "\n" + nn)
                for mmm, mnn in mysql.items():
                    if "mysql" in mnn:
                        e.node(mmm + "\n" + mnn)
                for rmm, rnn in redis.items():
                    if "redis" in rnn:
                        f.node(rmm + "\n" + rnn)
        draw()
    else:
        with g.subgraph(name="clusterD") as b:
            b.attr(label="内网区", bgcolor="#FFEFD5", fontname="Microsoft YaHei", fontcolor="red", style="rounded",
                   gradientangle="500")
            with b.subgraph(name="clusterE") as t, b.subgraph(name="clusterF") as yy, b.subgraph(
                    name="clusterG") as d, b.subgraph(name="clusterH") as e, b.subgraph(name="clusterI") as f:
                t.attr(label="Tomcat", color="white", bgcolor="#CCCC99", style="rounded", gradientangle="500")
                t.attr("node", shape="box", style="filled", gradientangle="90")
                yy.attr(label="Nginx", style="rounded", bgcolor="#FFFFE0", gradientangle="500")
                yy.attr("node", shape="box", style="filled", gradientangle="90")
                d.attr(label="Zookeeper", bgcolor="#FFF0F5", style="rounded", gradientangle="500")
                d.attr("node", shape="box", style="filled", gradientangle="90")
                e.attr(label="Mysql", style="rounded", bgcolor="#B0E0E6", gradientangle="500")
                e.attr("node", shape="box", style="filled", gradientangle="90")
                f.attr(label="Redis", style="rounded", bgcolor="#FFFFE0", gradientangle="500")
                f.attr("node", shape="box", style="filled", gradientangle="90")
                dicts = {};mysql = {};redis = {};nginx = {};tomcat = {}
                for o, p in data["内网区"].items():
                    for pp in p:
                        if "zookeeper" in pp:
                            dicts[o] = pp
                        if "mysql" in pp:
                            mysql[o] = pp
                        if "redis" in pp:
                            redis[o] = pp
                        if "nginx" in pp:
                            nginx[o] = pp
                        if "interbank-client" in pp:
                            t.node("interbank-client\n" + o)
                        if "interbank-server" in pp:
                            t.node("interbank-server\n" + o)
                for nmm, nnn in nginx.items():
                    if "nginx" in nnn:
                        yy.node(nmm + "\n" + nnn)
                for mm, nn in dicts.items():
                    if "zookeeper" in nn:
                        d.node(mm + "\n" + nn)
                for mmm, mnn in mysql.items():
                    if "mysql" in mnn:
                        e.node(mmm + "\n" + mnn)
                for rmm, rnn in redis.items():
                    if "redis" in rnn:
                        f.node(rmm + "\n" + rnn)
        draw()
    g.render(filename="/tmp/liucheng_" + str(today_time()), view=False)
    return data


################################## /test 请求路径生成拓扑图 ##################################
@app.route('/test', methods=['POST'])
def get_data2():
    dot = Graph('G', format="pdf")
    dot.graph_attr['rankdir '] = 'TB'
    dot.attr(compound='true', fixedsize='false')
    data =  json.loads(request.get_data().decode('UTF-8'))
    for key in data.keys():
        with dot.subgraph(name='cluster_' + key) as c:
            for aa, bb in data[key].items():
                c.attr(label=key, bgcolor='#FFEFD5', fontname='Microsoft YaHei', fontcolor='red', style='rounded',gradientangle='270')
                with c.subgraph(name='cluster_' + aa) as d:
                    d.attr(label=aa, color='white', bgcolor='#CCCC99', style='rounded', gradientangle='270',fontname="Microsoft YaHei")
                    d.attr('node', shape='box', style='filled', gradientangle='90')
                    for cc in bb:
                        d.node(cc)
    dot.render(filename="/tmp/tuopu_"+str(today_time()), view=False)
    return data

if __name__ == '__main__':
    app.run(debug=False,threaded=True,host='10.1.90.216', port=9090)
