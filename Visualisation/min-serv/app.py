#!/usr/bin/env python3
""" Development Test Server

A hacked together Flask server used to test the web front-end for the underlying
database. To run it, simply:
```
export FLASK_APP=app.py
flask run
```
"""

__author__ = "Thomas E. Hansen"
__status__ = "Development"


import json
from warnings import warn

from flask import Flask, request, render_template, abort
from flaskext.mysql import MySQL
import networkx as nx
import networkx.algorithms as nxalg


###############
# FLASK SETUP #
###############

app = Flask(__name__)

# database conf
app.config['MYSQL_DATABASE_HOST'] = 'teh6.host.cs.st-andrews.ac.uk'
app.config['MYSQL_DATABASE_USER'] = 'teh6'
app.config['MYSQL_DATABASE_PASSWORD'] = 'GwF53QLc8mQ.g5'
app.config['MYSQL_DATABASE_DB'] = 'teh6_2019_summer_project'

mariadb = MySQL(app)
db_conn = mariadb.connect()
mariadb.init_app(app)


####################
# GLOBAL VARIABLES #
####################

# graph for assisting with highlighting and other potential analysis
# uses NetworkX for now, if we ever experience slowdown, look at graph-tool
dg = nx.DiGraph()

# school id to name
school_dict_id_name = {}
# school name to id
school_dict_name_id = {}
# distinct possible credit values
all_credit_vals = []


###################
# DI-GRAPH THINGS #
###################

def add_nodes_to_graph(nodes):
    """
    Creates a new directed graph (di-graph) stored in the global variable `dg`
    and populates it with nodes labelled by the module code.

    :param nodes: A tuple of 1-tuples, each containing a module code. The weird
                  type is due to the way `flaskext.mysql` returns results.
    :return:
    """
    # might want to make this cleverer, but for now, rebuild the graph each time
    # the database is queried
    global dg
    dg = nx.DiGraph()
    for node in nodes:
        dg.add_node(node[0])        # `node[0]` because each node is a 1-tuple


def add_links_to_graph(links):
    """
    Adds edges to the global `dg` di-graph using the tuple returned from the
    `fetch_requisites` function. This tuple consists of 3-tuples of the form
    (source, target, type) where type is one of "Pre", "Co", or "Anti". Since
    networkx supports adding any keyword-attribute to an edge, the requisite
    type is stored as the `req_type` attribute of the edge.

    :param links: A tuple of links returned by the `fetch_requisites` function.
    :return:
    """
    global dg
    for src, tgt, req_type in links:
        dg.add_edge(src, tgt, req_type=req_type)


def find_paths_to_node(node):
    """
    Use the global `dg` di-graph to find all the modules/nodes reachable via the
    requisites from the given node, at least staying at the same level or going
    down one, as well as all the edges involved in any of these traversals.

    :param node: The node to start at.
    :return: (reachable_nodes: set, edges_involved: set)
    """
    # FixMe: This function could potentially be changed/improved to resemble the
    # FixMe: one used in `static/js/column-vis.js`, the `returnNodes` method.
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


#########################
# JSON HELPER FUNCTIONS #
#########################

def nodes_to_json(nodes):
    """
    This function is used to prepare data for sending to the website.
    Converts the given nodes to a string representing a JSON-array of JSON-
    objects containing the attributes `"id"` and `"group"`. The latter is an
    attribute that was only needed for the force-directed drafts. If these are
    removed/discarded, it can, and should, safely be removed.

    :param nodes: A tuple of 1-tuples containing the module codes.
    :return: A string representing a JSON-array of JSON-objects.
    """
    node_array = []
    for node in nodes:
        node_array.append(
            '{"id": "%s", "group": %s}' % (node[0], get_group(node[0])))
    return str(node_array)


def links_to_json(links):
    """
    This function is used to prepare data for sending to the website.
    Converts the given links to a string representing a JSON-array of JSON-
    objects containing the attributes `"source"`, `"target"`, and `"type"`.

    :param links: A tuple of 3-tuples containing the module codes denoting the
                  source and target modules, as well as whether the requisite
                  is a "Pre", "Co", or "Anti" requisite.
    :return: A string representing a JSON-array of JSON-objects.
    """
    link_array = []
    if len(links[0]) == 2:
        # for use with the di-graph edges
        for src, tgt in links:
            link_array.append('{"source": "%s", "target": "%s", "type": "%s"}'
                              % (src, tgt, dg[src][tgt]['req_type']))
    else:
        # for use with the database query results
        for src, tgt, req_type in links:
            link_array.append(
                '{"source": "%s", "target": "%s", "type": "%s"}'
                % (src, tgt, req_type))
    return str(link_array)


def get_group(module_code):
    """
    FixMe: Deprecated. Unless the force-directed graphs are being used, this
    FixMe: function should be removed.
    Returns an arbitrary integer used by the force-directed graph drafts.

    :param module_code: The code of a module.
    :return: An integer grouping that module. This integer is completely
             unrelated to anything in this project; 100% arbitrary.
    """
    warn("Only used for the force-directed graphs. Can likely be removed.",
         DeprecationWarning)
    if 'CS' in module_code:
        return 1
    elif 'BL' in module_code:
        return 2
    else:
        return 3


def fetch_modules(cursor, school_ids=None, semesters=None, credit_vals=None):
    """
    Constructs, executes, and fetches the results of  the SQL-query used to get
    the relevant modules.

    :param cursor: The mysql cursor used to execute and fetch the results of the
                   query.
    :param school_ids: A list of school ids to filter the modules by.
    :param semesters: A list of semester numbers to filter the modules by.
    :param credit_vals: A list of exact credit worths to filter the modules by.
    :return: A 2-tuple of the form: (query_results: tuple, sql_query: str).
             The query results are a tuple consisting of 1-tuples, each
             containing a module code. This is due to the way flaskext.mysql
             handles query-result fetching. If any filters were applied, the
             SQL-query is returned as well to be able to filter the requisites.
             Otherwise, the SQL-query is `None`.
    """
    module_query = 'SELECT DISTINCT `ModuleCode` FROM `complete_modules`'
    first = True
    # handle school ids
    if not school_ids:
        pass
    else:
        if first:
            # if this is the first filter, add the `WHERE` SQL keyword,
            # indicating the start of conditions
            module_query += ' WHERE '
            first = False
        module_query += '('     # bracket the condition
        module_query += '`SchoolName` IN '  # filter by the school names
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
            # if this is the first filter, add the `WHERE` SQL keyword,
            # indicating the start of conditions
            module_query += ' WHERE '
            first = False
        else:
            module_query += ' AND '
        module_query += '('     # bracket the condition
        module_query += '`semester_number` IN '     # filter by semester number
        module_query += '('     # open the selection
        module_query += str(semesters)[1:-1]        # str(list) w/o []s
        module_query += ')'     # close the selection
        module_query += ')'     # bracket the condition
    # handle credit values
    if not credit_vals:
        pass
    else:
        if first:
            # if this is the first filter, add the `WHERE` SQL keyword,
            # indicating the start of conditions
            module_query += ' WHERE '
            first = False
        else:
            module_query += ' AND '
        module_query += '('     # bracket the condition
        module_query += '`ModuleSCOTCATCredits` IN '    # filter by credit worth
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
    """
    Constructs, executes, and fetches the results of  the SQL-query used to get
    the relevant requisites. The `module_query` is used for a sub-query which
    dictates how to filter the requisites.

    :param cursor: The mysql cursor used to execute and fetch the results of the
                   query.
    :param module_query: The SQL-query used to fetch the relevant modules.
                         Returned from the `fetch_modules` function.
    :return: A tuple of 3-tuples containing the module codes of the source and
             target of a requisite, as well as its type (i.e. "Pre", "Co", or
             "Anti"). This format is due to the way flaskext.mysql handles
             query-result fetching.
    """
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
    """
    Fetches the modules (nodes) and requisites (links) from the MariaDB database
    and returns them in a JSON-parsable format.

    :param school_ids: A list of the school ids to filter by.
    :param semesters: A list of the semester numbers to filter by.
    :param credit_vals: A list of the exact credit worths to filter by.
    :return: A 2-tuple (pair) of strings. The first string represents a JSON-
             array of JSON-objects of modules/nodes. The second string
             represents a JSON-array of JSON-objects of requisites/links.
    """
    cursor = db_conn.cursor()
    # fetch the modules
    raw_nodes, module_query = fetch_modules(cursor,
                                            school_ids=school_ids,
                                            semesters=semesters,
                                            credit_vals=credit_vals
                                            )
    # fetch the requisites
    raw_links = fetch_requisites(cursor,
                                 module_query=module_query
                                 )
    # update the di-graph
    add_nodes_to_graph(raw_nodes)
    add_links_to_graph(raw_links)
    # turn the data into JSON-parseable strings, removing `'`s that python's
    # `str` function puts in
    nodes = str(nodes_to_json(raw_nodes)).replace("'", "")
    links = str(links_to_json(raw_links)).replace("'", "")
    return nodes, links


#######################
# FILTER SANITISATION #
#######################

# The three functions below are an attempt at preventing SQL-injections by
# manipulating the GET-request.
# FixMe: They should be replaced with prepared statements. Unfortunately
# FixMe: however, flaskext.mysql's cursor does not support prepared statements.

def check_school_ids(school_ids):
    """
    Checks that all of the ids in `school_ids` are valid, i.e. that the ids
    occur in the database.

    :param school_ids: A list of ids to check.
    :return: `True` if nothing was given, or if all the ids were valid. `False`
             otherwise.
    """
    if not school_ids:
        return True
    for school_id in school_ids:
        if school_id not in school_dict_name_id.values():
            return False
    return True


def check_semesters(semesters):
    """
    Checks that all of the semester numbers in `semesters` are valid, i.e. that
    they are in the range [1..4] (i.e. semester 1, 2, summer, and whole-year).

    :param semesters: A list of semester numbers to check.
    :return: `True` if nothing was given, or if all the semester numbers were
             valid. `False` otherwise.
    """
    if not semesters:
        return True
    sem_range = range(1, 5)
    for semester in semesters:
        if semester not in sem_range:
            return False
    return True


def check_credit_vals(credit_vals):
    """
    Checks that all of the credit values in `credit_vals` are valid, i.e. that
    they are in the range [0..120].

    :param credit_vals: A list of credit values to check.
    :return: `True` if nothing was given, or if all the credit values were
             valid. `False` otherwise.
    """
    if not credit_vals:
        return True
    valid_credit_range = range(0, 121)
    for credit_val in credit_vals:
        if credit_val not in valid_credit_range:
            return False
    return True


####################################
# ROUTES FOR GUI/WEBSITE ENDPOINTS #
####################################

def network_draft(template_name: str):
    """
    Helper function which queries the database without any filters and renders
    the result using the given template. Used for the drafts initially made.

    :param template_name: The name of the template to use.
    :return: `render_template(template_name, network=json_network)` where
             `json_network` is a string describing a JSON-object containing
             `"nodes"` and `"links"` whose values are the JSON-arrays returned
             by the `query_db` function.
    """
    # FixMe: this function could potentially be deleted if/when the drafts are
    # FixMe: no longer needed
    nodes, links = query_db()
    network = '{"nodes": %s, "links": %s}' % (nodes, links)
    json_network = json.loads(network)
    return render_template(template_name, network=json_network)


@app.route('/', methods=['GET'])
@app.route('/index.html', methods=['GET'])
def index():
    """
    Processes any request to the `/` route or the `/index.html` route, i.e. the
    home/main page. This includes parsing, verifying, and querying the database
    based on the filters passed in the GET-request's URL, as well as loading and
    initialising the global variables used in other parts of this app.

    :return: `render_template` of `index.html`, with the parts needing filled in
             by jinja2 named appropriately. Returns a HTML status code 400 (bad
             request) if one of the filters given did not pass their check.
    """
    # load global things _FIRST!_
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
        # query the db with the given filters
        nodes, links = query_db(school_ids=school_ids,
                                semesters=semesters,
                                credit_vals=credit_vals)
    else:
        # if there are no request args, query the db without filtering
        nodes, links = query_db()
    # format things to json
    network = '{"nodes": %s, "links": %s}' % (nodes, links)
    json_network = json.loads(network)
    # render the `index.html` page with jinja2 filling in the keyword parts with
    # the given data/objects
    return render_template("index.html",
                           network=json_network,
                           school_dict=json_school_dict,
                           credit_vals=all_credit_vals
                           )


@app.route('/admin.html', methods=['GET'])
def db_admin():
    """
    Renders the `admin.html` template, used for managing the database containing
    modules, schools, requisites, courses, etc.

    :return: `render_template("admin.html")`
    """
    return render_template("admin.html")


@app.route('/fd-graph', methods=['GET'])
def fd_graph():
    """
    Renders the force-directed draft used to get an initial overview of what the
    network was like. Uses the `network_draft` function.

    :return: `network_draft('fd-graph.html')`
    """
    return network_draft('fd-graph.html')


@app.route('/columns')
def columns():
    """
    Renders the column-oriented layout used when getting familiar with D3JS and
    figuring out how to lay out the network in a nicer, more intuitive way. Uses
    the `network_draft` function.

    :return: `network_draft('columns.html')`
    """
    return network_draft('columns.html')


@app.route('/fd-colour')
def fd_colour():
    """
    Renders the force-directed draft used to get an initial overview of what the
    network was like, _with_ the edges coloured to represent pre-, co-, and
    anti-requisites. Uses the `network_draft` function.

    :return: `network_draft('fd-graph-colour.html')`
    """
    return network_draft('fd-graph-colour.html')


#################################
# ROUTES FOR SUPPLYING RAW DATA #
#################################

# These are mostly used for sanity-checking/debugging by me, and not by any part
# of the website

@app.route('/columns/find-paths', methods=['GET'])
def graph_paths():
    """
    Given the id of a node (i.e. a module code) through a `node` argument in the
    GET-request, returns all the nodes and edges to highlight in a JSON-object
    containing the arrays `"involved_nodes"` and `"involved_links"`. This was
    done to have the ancestor finding be done server-side rather than client-
    side.
    The involved nodes are strings of node-ids/module codes and the involved
    links are strings representing a link using the `links_to_json` function.

    :return: A JSON-object containing two arrays: `"involved_nodes"` and
             `"involved_links"`.
    """
    node = request.args.get('node')
    involved_nodes, path_parts = find_paths_to_node(node)
    path_parts_list = list(path_parts)
    json_path_parts = links_to_json(path_parts_list)
    json_str = '{"involved_nodes": %s, "involved_links": %s}' \
               % (['"%s"' % node for node in involved_nodes], json_path_parts)
    json_str = json_str.replace("'", "")
    return json.loads(json_str)


@app.route('/data', methods=['GET'])
def data():
    """
    Returns the JSON-object commonly referred to throughout the routes in this
    app as the `network` keyword argument. It is a JSON-object containing two
    arrays: `"nodes"` and `"links"`.

    :return: A JSON-object containing two arrays: `"nodes"` and `"links"`.
    """
    nodes, links = query_db()
    network = '{"nodes": %s, "links": %s}' % (nodes, links)
    # print(network)
    return json.loads(network)


@app.route('/data/school-ids', methods=['GET'])
def get_school_dict():
    """
    Returns the global variable `school_dict_name_id` as a JSON-object. This
    object is used to be able to map school names to their ids.

    :return: A JSON-object whose properties are the school names, and their
             corresponding values are the numeric id of that school.
    """
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
    """
    Returns the global variable `all_credit_vals` as a JSON-object. This object
    contains an array of all the exact credit values.

    :return: A JSON-object whose property is `"allCreditVals"`, containing an
             array of all the possible exact credit values.
    """
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
