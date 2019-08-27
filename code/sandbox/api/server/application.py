"""
API for returning an anlyzing planar graphs
"""

import json
from flask import Flask, Markup, request # pylint: disable=E0401
from flask_cors import CORS # pylint: disable=E0401

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

@APP.route('/planar-graphs/<seed>', methods=['DELETE'])
def planar_graph(seed):
    """ delete planar graphs with specific seed """
    MaximallyConnectedPlanarGraph.delete(seed)
    return ('', 204)


@APP.route('/planar-graphs/<seed>/graph.svg', methods=['GET'])
def planar_graph_svg(seed):
    """ generates an svg for the given graph """
    num_points = request.args.get('num-points', default=200, type=int)
    triangle = MaximallyConnectedPlanarGraph(seed, num_points=num_points)
    slice_origin_id = request.args.get('slice-origin-id', default=None, type=int)
    reverse_slice = request.args.get('reverse-slice', default=False, type=bool)
    colored_nodes = dict(request.args)
    colored_nodes.pop('slice_origin_id', None)
    return Markup(
        triangle.generate_svg(
            slice_origin_id=slice_origin_id,
            colored_nodes=colored_nodes,
            reverse_slice=reverse_slice
        )
    )


if __name__ == "__main__":
    APP.run(host='0.0.0.0', debug=True)
