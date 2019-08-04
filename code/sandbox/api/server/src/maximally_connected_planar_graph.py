"""
Class for defining and manipulating triangle files
"""

from subprocess import call
import random
import os
import json
import shutil
import math

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/')


class MaximallyConnectedPlanarGraph():
    """
    Class for defining and manipulating triangle files
    """
    @staticmethod
    def delete_all():
        """
        Delete all stored planar graphs
        """
        if os.path.exists(DATA_DIR):
            shutil.rmtree(DATA_DIR)

    @staticmethod
    def delete(seed):
        """
        Deletes the stored planar graph corresponding to the given seed value
        """
        shutil.rmtree(os.path.join(DATA_DIR, seed))

    @staticmethod
    def list_all():
        """
        List all stored planar graphs by their seed
        """
        if os.path.exists(DATA_DIR):
            return os.listdir(DATA_DIR)
        return []

    @staticmethod
    def generate_triangle(seed):
        """
        Generates a random maximally planar graph for a given seed value
        using the "triangle" library (output stored in triagle format)
        """
        points = {
            0: 750,
            750: 0,
            1500: 751
        }
        random.seed(seed)
        while len(points) < 200:
            y_coord = (random.randrange(500) or 1) + 200
            x_coord = random.randrange(round(y_coord*4/3)) + round((500 - y_coord)*(3/4)) + 400
            if (not points.get(x_coord)) and (x_coord != 750):
                points[x_coord] = y_coord

        os.makedirs(os.path.join(DATA_DIR, seed), exist_ok=True)
        filepath = os.path.join(DATA_DIR, '{}/triangle.node'.format(seed))

        # creates the input nodes used by triangle to create delauney graph
        with open(filepath, 'w') as node_file:
            header = "{}  2  0  0\n".format(len(points))
            node_file.write(header)
            i = 1
            for x_coord, y_coord in points.items():
                node_file.write("   {}    {}  {}\n".format(i, x_coord, y_coord))
                i += 1
            node_file.close()

        call(['triangle', '-e', filepath])

    def __init__(self, seed):
        self.files = {
            'node': os.path.join(DATA_DIR, '{}/triangle.1.node'.format(seed)),
            'edge': os.path.join(DATA_DIR, '{}/triangle.1.edge'.format(seed)),
            'data': os.path.join(DATA_DIR, '{}/data.json'.format(seed))
        }

        self.boundary_nodes = []
        self.nodes = {}
        self.nodes_by_level = []

        if not os.path.exists(os.path.join(DATA_DIR, seed)):
            MaximallyConnectedPlanarGraph.generate_triangle(seed)
            self.nodes, self.boundary_nodes, self.nodes_by_level = self.parse_triangle_file()
            self.save_data_file()
        else:
            self.load_data_file()

    def load_data_file(self):
        """
        Loads the data in this class from a serialized json file
        """
        with open(self.files['data'], 'r') as infile:
            data = json.load(infile)
            self.boundary_nodes = data['boundary_nodes']
            self.nodes = data['nodes']
            self.nodes_by_level = data['nodes_by_level']
            infile.close()

    def save_data_file(self):
        """
        Serializes the data in this class into a json file
        """
        with open(self.files['data'], 'w') as outfile:
            json.dump({
                'boundary_nodes': self.boundary_nodes,
                'nodes': self.nodes,
                'nodes_by_level': self.nodes_by_level,
            }, outfile, indent=4)
            outfile.close()

    def calculate_clockwise_angle_and_distance(self, center_node, spoke_node): # pylint: disable=R0201
        """
        Given a center_node_id and with a related spoke_node_id, this will
        find the angle
        """
        if not spoke_node['id'] in center_node['relations']:
            raise Exception('spoke_node_id must be related to center node')

        refvec = [0, 1]
        point = spoke_node['coords']
        origin = center_node['coords']

        # Vector between point and the origin: v = p - o
        vector = [point[0] - origin[0], point[1] - origin[1]]
        # Length of vector: ||v||
        lenvector = math.hypot(vector[0], vector[1])
        # If length is zero there is no angle
        if lenvector == 0:
            return -math.pi, 0

        # Normalize vector: v/||v||
        normalized = [vector[0]/lenvector, vector[1]/lenvector]
        dotprod = normalized[0]*refvec[0] + normalized[1]*refvec[1]     # x1*x2 + y1*y2
        diffprod = refvec[1]*normalized[0] - refvec[0]*normalized[1]     # x1*y2 - y1*x2
        angle = math.atan2(diffprod, dotprod)

        # Negative angles represent counter-clockwise angles so we need to subtract them
        # from 2*pi (360 degrees)
        if angle < 0:
            return 2 * math.pi + angle, lenvector

        # I return first the angle because that's the primary sorting criterium
        # but if two vectors have the same angle then the shorter distance should come first.
        # (lenvector should never really be needed, however, since that would mean edges overlap)
        return angle, lenvector

    def get_closest_counter_clockwise(self, center_node, spoke_node): # pylint: disable=R0201
        """
        Given a center_node and with a related spoke_node, this will
        find the first node related to center_node in the clockwise direction
        """
        spoke_index = center_node['relations'].index(spoke_node['id'])
        index = (spoke_index + 1) % len(center_node['relations'])
        return (center_node['relations'][index], '??')

    def identify_level_elements(self, level):
        node_ids_in_level = self.nodes_by_level[level]
        traversed = {
            # 'node_id_1': { 'node_id_2': True, 'node_id_3': True }
            # 'node_id_2': { 'node_id_1': True }
            # 'node_id_3': { 'node_id_2': True }
        }


        first_node_id = node_ids_in_level[0]
        first_node = self.nodes.get(first_node_id)
        current_path = [first_node_id]

        if first_node['relations']:
            related_node_id = first_node['relations'][0]
            related_node = self.nodes.get(related_node_id)
            current_path.append(related_node_id)

        next_node_id = self.get_closest_counter_clockwise(related_node, first_node)
        next_node = self.nodes.get(next_node_id)
        if next_node['relations']:
            related_node_id = first_node['relations'][0]
            if related_node_id in current_path:
                print('EXCEPT')
            else:
                current_path.append(related_node_id)
                related_node = self.nodes.get(related_node_id)

    # reads nodes from a triangle file
    def parse_triangle_file(self):
        """
        returns dictonary of nodes and array of boundary node ids based on the
        contents of the node file
        """
        nodes = {}
        boundary_nodes = []

        # parse node file into nodes
        with open(self.files['node']) as node_file:
            header = True
            for line in node_file:
                if header:
                    header = False
                    continue
                content = list(filter(lambda a: bool(a), line.split(' '))) # pylint: disable=W0108
                if not '#' in content[0]:
                    is_boundary = content[3] == '1\n'
                    nodes[content[0]] = {
                        'id': content[0],
                        'coords': [int(content[1]), int(content[2])],
                        'distance': 0 if is_boundary else None,
                        'relations': [],
                        'is_inner': False,
                        'is_isolated': False
                    }
                    if is_boundary:
                        boundary_nodes.append(content[0])
            node_file.close()

        # parse edge files into node relations
        with open(self.files['edge']) as edge_file:
            header = True
            for line in edge_file:
                if header:
                    header = False
                    continue
                content = list(filter(lambda a: bool(a), line.split(' '))) # pylint: disable=W0108
                if not '#' in content[0]:
                    nodes[content[1]]['relations'].append(content[2])
                    nodes[content[2]]['relations'].append(content[1])
            edge_file.close()

        # sorts relations clockwise
        for node_id, node in nodes.items():
            nodes[node_id]['relations'] = sorted(node['relations'], key=(
                lambda related_node_id: (
                    self.calculate_clockwise_angle_and_distance(node, nodes.get(related_node_id)) # pylint: disable=W0640
                )
            ))

        nodes_by_level = self.add_distance_to_nodes(nodes, boundary_nodes)

        return nodes, boundary_nodes, nodes_by_level

    def add_distance_to_nodes(self, nodes, boundary_nodes): # pylint: disable=R0201
        """
        add a "distance" parameter to each node based on the distance from the boundary
        WARNING: mutates the "nodes" parameter
        """
        # current distance = collection of all node ids with same minimum distance
        # from the outermost boundary
        nodes_by_level = []

        nodes_with_same_distance = boundary_nodes
        distance = 0
        # keep the process going until we have gone through all the possible distances
        while nodes_with_same_distance:
            next_nodes_with_same_distance = []
            for node_id in nodes_with_same_distance:
                nodes[node_id]['distance'] = distance # this is only needed for 1st step
                # relations = all nodes connected to the node in question by a single edge
                for related_node_id in nodes[node_id]['relations']:
                    # if we have not labeled this node yet, that means it must
                    # have a distance 1 greater than the nodes we're iterating over
                    if nodes[related_node_id].get('distance') is None:
                        nodes[related_node_id]['distance'] = distance + 1
                        next_nodes_with_same_distance.append(related_node_id)

            nodes_by_level.append(nodes_with_same_distance)
            distance += 1
            nodes_with_same_distance = next_nodes_with_same_distance

        return nodes_by_level

    # get a "slice" of nodes
    def get_slice(self, node_id, nodes_in_slice):
        """
        Generate a "slice" of nodes given a starting node
        """
        if self.nodes[node_id]['distance'] == 0:
            nodes_in_slice[node_id] = []
        for related_node_id in self.nodes[node_id]['relations']:
            if self.nodes[related_node_id]['distance'] < self.nodes[node_id]['distance']:
                related_node_ids = nodes_in_slice.get(node_id, [])
                related_node_ids.append(related_node_id)
                nodes_in_slice[node_id] = related_node_ids
                nodes_in_slice = self.get_slice(related_node_id, nodes_in_slice)
        return nodes_in_slice


    def generate_line(self, node_id_1, node_id_2, nodes_in_slice):
        """
        Returns an SVG line element for two nodes that form an edge
        """
        coords1 = self.nodes[node_id_1]['coords']
        coords2 = self.nodes[node_id_2]['coords']
        color = '#222'
        if self.nodes[node_id_1]['distance'] == self.nodes[node_id_2]['distance']:
            color = 'white'
        if (node_id_1 in nodes_in_slice) and (node_id_2 in nodes_in_slice):
            color = '#42b983'
        return (
            "    <line x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" style=\"stroke:{}; stroke-width: 1;\"/>\n" # pylint: disable=C0301
            .format(coords1[0], coords1[1], coords2[0], coords2[1], color)
        )

    def generate_svg(self, nodes=None, slice_origin_id=None):
        """
        Generate svg based on nodes
        """
        _nodes = nodes if nodes else self.nodes

        nodes_in_slice = self.get_slice(slice_origin_id, {}) if slice_origin_id else {}
        html = "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\"1500px\" height=\"1000px\">\n" # pylint: disable=C0301
        html += "  <g>\n"

        drawn_edges = {}

        for node, data in _nodes.items():
            for related_node_id in data['relations']:
                edge1 = "{}-{}".format(node, related_node_id)
                edge2 = "{}-{}".format(related_node_id, node)
                if not drawn_edges.get(edge1):
                    html += self.generate_line(node, related_node_id, nodes_in_slice)
                    drawn_edges[edge1] = True
                    drawn_edges[edge2] = True

            if data.get('is_closest'):
                fill = 'yellow'
            elif data.get('is_center'):
                fill = 'red'
            elif data.get('is_selected'):
                fill = 'purple'
            elif data['is_isolated']:
                fill = 'blue'
            elif node in nodes_in_slice:
                fill = '#42b983'
            elif data['is_inner']:
                fill = '#e96900'
            else:
                fill = 'white'
            html += (
                "    <rect class=\"node\" id=\"{}\" x=\"{}\" y=\"{}\" height=\"8\" width=\"10\" style=\"stroke: {}; fill: {};\"/>\n" # pylint: disable=C0301
                .format(data['id'], data['coords'][0]-6, data['coords'][1]-3, 'black', fill)
            )
            html += (
                "    <text class=\"node\" id=\"{}\" angle=\"{}\" x=\"{}\" y=\"{}\" style=\"fill: {}; font-size: 8px;\">{}</text>\n" # pylint: disable=C0301
                .format(data['id'], data.get('angle', '?'), data['coords'][0]-5, data['coords'][1]+4, 'black', data['distance']) # pylint: disable=C0301
            )
        html += "  </g>\n"
        html += "</svg>"
        return html
