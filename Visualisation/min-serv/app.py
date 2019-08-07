from flask import Flask, request, render_template
from flaskext.mysql import MySQL
import json


app = Flask(__name__)

# database conf
app.config['MYSQL_DATABASE_HOST'] = 'teh6.host.cs.st-andrews.ac.uk'
app.config['MYSQL_DATABASE_USER'] = 'teh6'
app.config['MYSQL_DATABASE_PASSWORD'] = 'GwF53QLc8mQ.g5'
app.config['MYSQL_DATABASE_DB'] = 'teh6_2019_summer_project'

mariadb = MySQL(app)
db_conn = mariadb.connect()
mariadb.init_app(app)


def nodes_to_json(nodes):
    node_array = []
    for node in nodes:
        node_array.append(
            '{"id": "%s", "group": %s}' % (node[0], get_group(node[0])))
    return str(node_array)


def links_to_json(links):
    link_array = []
    for src, tgt, type_ in links:
        link_array.append(
            '{"source": "%s", "target": "%s", "type":"%s"}' % (src, tgt, type_))
    return str(link_array)


def get_group(module_code):
    if 'CS' in module_code:
        return 1
    elif 'BL' in module_code:
        return 2
    else:
        return 3


def query_db():
    cursor = db_conn.cursor()
    cursor.execute('SELECT `code` FROM `module`;')
    raw_nodes = cursor.fetchall()
    cursor.execute(
        'SELECT source_module, TargetModule, `type` FROM complete_requisites;')
    raw_links = cursor.fetchall()
    nodes = str(nodes_to_json(raw_nodes)).replace("'", "")
    links = str(links_to_json(raw_links)).replace("'", "")
    return nodes, links


def network_template(template_name: str):
    nodes, links = query_db()
    network = '{"nodes": %s, "links": %s}' % (nodes, links)
    json_network = json.loads(network)
    return render_template(template_name, network=json_network)


@app.route('/data', methods=['GET'])
def data():
    nodes, links = query_db()
    network = '{"nodes": %s, "links": %s}' % (nodes, links)
    # print(network)
    return json.loads(network)


@app.route('/fd-graph', methods=['GET'])
def fd_graph():
    # nodes, links = query_db()
    # network = '{"nodes": %s, "links": %s}' % (nodes, links)
    # return render_template('fd-graph.html', network=json.loads(network))
    return network_template('fd-graph.html')


@app.route('/columns')
def columns():
    return network_template('columns.html')


@app.route('/fd-colour')
def fd_colour():
    return network_template('fd-graph-colour.html')


if __name__ == '__main__':
    app.run()
