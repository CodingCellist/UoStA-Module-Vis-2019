from flask import Flask, request
from flaskext.mysql import MySQL


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
        node_array.append('{id: "%s", group: %s}' % (node[0], get_group(node[0])))
    return str(node_array)


def links_to_json(links):
    link_array = []
    for src, tgt in links:
        link_array.append('{source: "%s", target: "%s"}' % (src, tgt))
    return str(link_array)


def get_group(module_code):
    if 'CS' in module_code:
        return 1
    elif 'BL' in module_code:
        return 2
    else:
        return 3


@app.route('/links', methods=['GET'])
def links():
    cursor = db_conn.cursor()
    cursor.execute('SELECT `code` FROM `module`;')
    raw_nodes = cursor.fetchall()
    cursor.execute('SELECT source_module, TargetModule FROM complete_requisites;')
    raw_links = cursor.fetchall()
    print(nodes_to_json(raw_nodes))
    print(links_to_json(raw_links))
    return 'WIP'


if __name__ == '__main__':
    app.run()
