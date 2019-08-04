"""
API for returning an anlyzing planar graphs
"""

import json
from flask import Flask, Markup, request, jsonify
from flask_cors import CORS

from src.maximally_connected_planar_graph import MaximallyConnectedPlanarGraph

APP = Flask(__name__)
CORS(APP)

# this will return the probabilities associated with a particular user
@APP.route("/planar-graphs", methods=['GET', 'DELETE'])
def delete_all_planar_graphs():
    """ delete all planar graphs """
    if request.method == "DELETE":
        MaximallyConnectedPlanarGraph.delete_all()
        return ('', 204)
    results = MaximallyConnectedPlanarGraph.list_all()
    return json.dumps(results)

@APP.route('/planar-graphs/<seed>', methods=['GET', 'DELETE'])
def planar_graph(seed):
    """ delete planar graphs with specific seed """
    if request.method == 'DELETE':
        MaximallyConnectedPlanarGraph.delete(seed)
        return ('', 204)
    triangle = MaximallyConnectedPlanarGraph(seed)
    slice_origin_id = request.args.get('slice-origin-id', default=None, type=str)
    return Markup(triangle.generate_svg(slice_origin_id=slice_origin_id))


@APP.route('/planar-graphs/<seed>/graph.svg', methods=['GET'])
def planar_graph_svg(seed):
    """ generates an svg for the given graph """
    triangle = MaximallyConnectedPlanarGraph(seed)
    slice_origin_id = request.args.get('slice-origin-id', default=None, type=str)
    return Markup(triangle.generate_svg(slice_origin_id=slice_origin_id))


if __name__ == "__main__":
    APP.run(host='0.0.0.0', debug=True)
