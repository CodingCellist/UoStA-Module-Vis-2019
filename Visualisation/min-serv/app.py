from flask import Flask, request, render_template, abort
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

# school id to name
school_dict_id_name = {}
# school name to id
school_dict_name_id = {}
# distinct possible credit values
all_credit_vals = []


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


def fetch_modules(cursor, school_ids=None, semesters=None, credit_vals=None):
    module_query = 'SELECT DISTINCT `ModuleCode` FROM `complete_modules`'
    first = True
    # handle school ids
    if not school_ids:
        pass
    else:
        if first:
            module_query += ' WHERE '
            first = False
        module_query += '('     # bracket the condition
        module_query += '`SchoolName` IN '
        module_query += '('     # open the selection
        # get the unique school names for each id
        schools_names = \
            list(set(map(lambda s_id: school_dict_id_name[s_id], school_ids)))
        module_query += str(schools_names)[1:-1]     # str(list) w/o []s
        module_query += ')'     # close the selection
        module_query += ')'     # bracket the condition
        print('\tfetch_modules:', module_query)
    # handle semesters
    if not semesters:
        pass
    else:
        if first:
            module_query += ' WHERE '
            first = False
        else:
            module_query += ' AND '
        module_query += '('     # bracket the condition
        module_query += '`semester_number` IN '
        module_query += '('     # open the selection
        module_query += str(semesters)[1:-1]        # str(list) w/o []s
        module_query += ')'     # close the selection
        module_query += ')'     # bracket the condition
    # handle credit values
    if not credit_vals:
        pass
    else:
        if first:
            module_query += ' WHERE '
            first = False
        else:
            module_query += ' AND '
        module_query += '('     # bracket the condition
        module_query += '`ModuleSCOTCATCredits` IN '
        module_query += '('     # open the selection
        module_query += str(credit_vals)[1:-1]      # str(list) w/o []s
        module_query += ')'     # close the selection
        module_query += ')'     # bracket the condition
    # close the query
    module_query += ';'
    # fetch the nodes
    cursor.execute(module_query)
    raw_nodes = cursor.fetchall()
    # return None as the module query if no filters were applied
    if first:
        return raw_nodes, None
    # otherwise, return the filtering query
    return raw_nodes, module_query


def fetch_requisites(cursor, module_query=None):
    requisite_query = \
        'SELECT `source_module`, `TargetModule`, `type` ' \
        'FROM `complete_requisites`'
    if not module_query:
        pass
    else:
        module_query = module_query[:-1]    # cut the `;` from the module query
        requisite_query += ' WHERE '
        requisite_query += '('              # bracket the 1st condition
        requisite_query += '`source_module` IN '
        requisite_query += '('              # bracket the sub-selection
        requisite_query += module_query     # the query used to filter modules
        requisite_query += ')'              # bracket the sub-selection
        requisite_query += ')'              # bracket the 1st condition
        requisite_query += ' AND '
        requisite_query += '('              # bracket the 2nd condition
        requisite_query += '`TargetModule` IN '
        requisite_query += '('              # bracket the sub-selection
        requisite_query += module_query     # the query used to filter modules
        requisite_query += ')'              # bracket the sub-selection
        requisite_query += ')'              # bracket the 2nd condition
    # close the query
    requisite_query += ';'
    # fetch the requisites
    cursor.execute(requisite_query)
    raw_links = cursor.fetchall()
    return raw_links


def query_db(school_ids=None, semesters=None, credit_vals=None):
    cursor = db_conn.cursor()
    # fetch the modules
    # cursor.execute('SELECT `code` FROM `module`;')
    # raw_nodes = cursor.fetchall()
    raw_nodes, module_query = fetch_modules(cursor,
                                            school_ids=school_ids,
                                            semesters=semesters,
                                            credit_vals=credit_vals
                                            )
    # fetch the requisites
    # cursor.execute(
    #     'SELECT source_module, TargetModule, `type`' \
    #     'FROM complete_requisites;')
    # raw_links = cursor.fetchall()
    raw_links = fetch_requisites(cursor,
                                 module_query=module_query)
    # update the di-graph
    add_nodes_to_graph(raw_nodes)
    add_links_to_graph(raw_links)
    # turn the data into JSON-parseable strings
    nodes = str(nodes_to_json(raw_nodes)).replace("'", "")
    links = str(links_to_json(raw_links)).replace("'", "")
    return nodes, links


def check_school_ids(school_ids):
    if not school_ids:
        return True
    for school_id in school_ids:
        if school_id not in school_dict_name_id.values():
            return False
    return True


def check_semesters(semesters):
    if not semesters:
        return True
    sem_range = range(1, 5)
    for semester in semesters:
        if semester not in sem_range:
            return False
    return True


def check_credit_vals(credit_vals):
    if not credit_vals:
        return True
    valid_credit_range = range(0, 121)
    for credit_val in credit_vals:
        if credit_val not in valid_credit_range:
            return False
    return True


def network_template(template_name: str):
    nodes, links = query_db()
    network = '{"nodes": %s, "links": %s}' % (nodes, links)
    json_network = json.loads(network)
    return render_template(template_name, network=json_network)


@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    # load things _FIRST!_
    json_school_dict = get_school_dict()
    get_distinct_credit_vals()
    # handle request args if there are any
    if len(request.args) > 0:
        # get the request arguments and turn them to ints as they should be
        school_ids = list(map(int, request.args.getlist("schoolIds[]")))
        semesters = list(map(int, request.args.getlist("semesters[]")))
        credit_vals = list(map(int, request.args.getlist("creditVals[]")))
        # sanity check since we don't have prepared statements
        all_ok = True
        all_ok &= check_school_ids(school_ids)
        all_ok &= check_semesters(semesters)
        all_ok &= check_credit_vals(credit_vals)
        # if all is not okay, abort with status 400 (bad request)
        if not all_ok:
            abort(400)
        nodes, links = query_db(school_ids=school_ids,
                                semesters=semesters,
                                credit_vals=credit_vals)
    else:
        # if there are no request args, query the db without filtering
        nodes, links = query_db()
    # format things to json
    network = '{"nodes": %s, "links": %s}' % (nodes, links)
    json_network = json.loads(network)
    return render_template("index.html",
                           network=json_network,
                           school_dict=json_school_dict,
                           credit_vals=all_credit_vals)
    # return network_template("index.html")


@app.route('/admin.html', methods=['GET'])
def db_admin():
    return render_template("admin.html")


@app.route('/fd-graph', methods=['GET'])
def fd_graph():
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


#################################
# ROUTES FOR SUPPLYING RAW DATA #
#################################


@app.route('/data', methods=['GET'])
def data():
    nodes, links = query_db()
    network = '{"nodes": %s, "links": %s}' % (nodes, links)
    # print(network)
    return json.loads(network)


@app.route('/data/school-ids', methods=['GET'])
def get_school_dict():
    cursor = db_conn.cursor()
    # fetch the schools if we haven't already done so
    global school_dict_name_id
    if len(school_dict_name_id) == 0:
        cursor.execute(
            'SELECT * FROM `school`;'
        )
        id_school_tuples = cursor.fetchall()
        # cursor.fetchall returns a tuple of tuples, not a list
        id_school_tuple_list = [(int_id, name) for (int_id, name) in id_school_tuples]
        # mapping int_id --> name
        global school_dict_id_name
        school_dict_id_name = dict(id_school_tuple_list)
        # mapping name --> int_id
        school_id_tuples = [(name, int_id) for (int_id, name) in
                            id_school_tuple_list]
        school_dict_name_id = dict(school_id_tuples)
    return json.loads(json.dumps(school_dict_name_id))


@app.route('/data/credit-vals', methods=['GET'])
def get_distinct_credit_vals():
    cursor = db_conn.cursor()
    # fetch the distinct credit values if we haven't already done so
    global all_credit_vals
    if len(all_credit_vals) == 0:
        cursor.execute(
            'SELECT DISTINCT `credit_worth` FROM `module`;'
        )
        all_credit_vals = cursor.fetchall()
        all_credit_vals = [t[0] for t in all_credit_vals]
        all_credit_vals.sort()
    return json.loads('{"allCreditVals": %s}' % all_credit_vals)


if __name__ == '__main__':
    app.run()
