from flask import Flask, request, render_template
from flaskext.mysql import MySQL
import json
import networkx as nx
import networkx.algorithms as nxalg


app = Flask(__name__)

# database conf
app.config['MYSQL_DATABASE_HOST'] = 'teh6.host.cs.st-andrews.ac.uk'
app.config['MYSQL_DATABASE_USER'] = 'teh6'
app.config['MYSQL_DATABASE_PASSWORD'] = 'GwF53QLc8mQ.g5'
app.config['MYSQL_DATABASE_DB'] = 'teh6_2019_summer_project'

mariadb = MySQL(app)
db_conn = mariadb.connect()
mariadb.init_app(app)

# graph for assisting with highlighting and other potential analysis
# uses NetworkX for now, if we ever experience slowdown, look at graph-tool
dg = nx.DiGraph()


def add_nodes_to_graph(nodes):
    # might want to make this cleverer, but for now, rebuild the graph each time
    # the database is queried
    global dg
    dg = nx.DiGraph()
    for node in nodes:
        dg.add_node(node[0])


def add_links_to_graph(links):
    global dg
    for src, tgt, req_type in links:
        dg.add_edge(src, tgt, req_type=req_type)


def find_paths_to_node(node):
    """
    Use the directed graph to find all the modules reachable via the requisites
    from the given node, at least staying at the same level or going down one,
    as well as all the edges involved in any of these traversals.
    :param node: The node to start at.
    :return: reachable_nodes: set, edges_involved: set
    """
    # if the graph has not been initialised, do so
    if len(dg.nodes) == 0 or len(dg.edges) == 0:
        query_db()

    # due to the way I represented requisites, we have to use descendants
    # instead of ancestors (maybe the db should be redone? (yikes!))
    reachable_nodes = set(nxalg.descendants(dg, node))

    # find all the edges which connect any pair of the involved nodes
    edges_involved = set([p for p in dg.edges if
                          (p[0] in reachable_nodes and p[1] in reachable_nodes)]
                         )
    return reachable_nodes, edges_involved


# ATTEMPT AT DOING THINGS MANUALLY UNTIL I FOUND THE RIGHT ALGORITHMS
# def find_paths_to_node(node):
#     """
#     Uses the directed graph to find all the paths leading to the given node
#     :param node:
#     :return: the involved nodes and edges in all the paths
#     """
#     involved_nodes, path_fragments = set(), set()
#     neighbours = list(dg[node])
#     old_in_len = len(involved_nodes)
#     old_pf_len = len(path_fragments)
#     # while neighbours is not empty
#     while not len(neighbours) == 0:
#         neighbour = neighbours.pop()
#         neighbour_helper(neighbours, neighbour, involved_nodes, path_fragments)
#         # if the sets stopped growing, remove all instances of the current node
#         # from the list of nodes to check
#         if old_in_len == len(involved_nodes) and old_pf_len == len(path_fragments):
#             while neighbour in neighbours:
#                 neighbours.remove(neighbour)
#     return involved_nodes, path_fragments
#
#
#     # for each neighbour:
#     #  while we are adding things:
#     #   add the edges from the source node to the current neighbour
#     #   find the neighbours of the current neighbour
#     #   repeat process with the new neighbours
#
#
# def neighbour_helper(neighbours: list, neighbour_node, inv_nodes: set, path_frags: set):
#     while True:
#         old_in_len = len(inv_nodes)
#         old_pf_len = len(path_frags)
#         inv_nodes.add(neighbour_node)
#         for attached in dg[neighbour_node]:
#             path_frags.add(neighbour_node + '--' + attached)
#             neighbours.append(attached)
#         if old_in_len == len(inv_nodes) and old_pf_len == len(path_frags):
#             break


def nodes_to_json(nodes):
    node_array = []
    for node in nodes:
        node_array.append(
            '{"id": "%s", "group": %s}' % (node[0], get_group(node[0])))
    return str(node_array)


def links_to_json(links):
    link_array = []
    if len(links[0]) == 2:
        for src, tgt in links:
            link_array.append('{"source": "%s", "target": "%s", "type": "%s"}'
                              % (src, tgt, dg[src][tgt]['req_type']))
    else:
        for src, tgt, req_type in links:
            link_array.append(
                '{"source": "%s", "target": "%s", "type": "%s"}'
                % (src, tgt, req_type))
    return str(link_array)


def get_group(module_code):
    if 'CS' in module_code:
        return 1
    elif 'BL' in module_code:
        return 2
    else:
        return 3


def query_db():
    # fetch the data
    cursor = db_conn.cursor()
    cursor.execute('SELECT `code` FROM `module`;')
    raw_nodes = cursor.fetchall()
    cursor.execute(
        'SELECT source_module, TargetModule, `type` FROM complete_requisites;')
    raw_links = cursor.fetchall()
    # update the di-graph
    add_nodes_to_graph(raw_nodes)
    add_links_to_graph(raw_links)
    # turn the data into JSON-parseable strings
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


@app.route('/columns/find-paths', methods=['GET'])
def graph_paths():
    """
    Function which returns all the nodes and edges to highlight, based on the
    given node.
    :return:
    """
    node = request.args.get('node')
    involved_nodes, path_parts = find_paths_to_node(node)
    path_parts_list = list(path_parts)
    json_path_parts = links_to_json(path_parts_list)
    json_str = '{"involved_nodes": %s, "involved_links": %s}' \
               % (['"%s"' % node for node in involved_nodes], json_path_parts)
    json_str = json_str.replace("'", "")
    return json.loads(json_str)


if __name__ == '__main__':
    app.run()
