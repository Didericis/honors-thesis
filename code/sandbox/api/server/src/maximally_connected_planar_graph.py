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

# Ducktype for level
# {
#     node_ids: [],
#     cycles: [],
#     paths: []
# }

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
    def generate_triangle(seed, num_points=200):
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
        while len(points) < num_points:
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

    def __init__(self, seed, num_points=None):
        self.files = {
            'node': os.path.join(DATA_DIR, '{}/triangle.1.node'.format(seed)),
            'edge': os.path.join(DATA_DIR, '{}/triangle.1.edge'.format(seed)),
            'ele': os.path.join(DATA_DIR, '{}/triangle.1.ele'.format(seed)),
            'data': os.path.join(DATA_DIR, '{}/data.json'.format(seed))
        }

        self.boundary_nodes = []
        self.nodes = {}
        self.levels = []

        if not os.path.exists(os.path.join(DATA_DIR, seed)):
            MaximallyConnectedPlanarGraph.generate_triangle(seed, num_points)
            self.nodes, self.boundary_nodes, self.levels = self.parse_triangle_files()
            self.save_data_file()
        else:
            # NB: this is bad design. We should be explicitly creating graphs with points,
            #     and loading separately, not overloading initializiation like this,
            #     but it doesn't seem worth fixing
            if num_points:
                print('Ignoring num_points (retrieving existing graph)')
            self.load_data_file()
            # TEMP
            self.nodes, self.boundary_nodes, self.levels = self.parse_triangle_files()
            self.save_data_file()

    def load_data_file(self):
        """
        Loads the data in this class from a serialized json file
        """
        with open(self.files['data'], 'r') as infile:
            data = json.load(infile)
            self.boundary_nodes = data['boundary_nodes']
            self.nodes = {int(k): v for k, v in data['nodes'].items()}
            self.levels = data['levels']
            infile.close()

    def save_data_file(self):
        """
        Serializes the data in this class into a json file
        """
        with open(self.files['data'], 'w') as outfile:
            json.dump({
                'boundary_nodes': self.boundary_nodes,
                'nodes': self.nodes,
                'levels': self.levels,
            }, outfile, indent=4)
            outfile.close()

    def calculate_clockwise_angle_and_distance(self, center_node, spoke_node): # pylint: disable=R0201
        """
        Given a center_node_id and with a related spoke_node_id, this will
        find the angle between the vector formed by edge between the center
        and the spoke and the vector [0, 1]
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

    # reads nodes from a triangle file
    def parse_triangle_files(self):
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
                    nodes[int(content[0])] = {
                        'id': int(content[0]),
                        'coords': [int(content[1]), int(content[2])],
                        'distance': 0 if is_boundary else None,
                        'relations': [],
                        'level_cycles': [], # ids of any level cycles this node is a part of
                        'level_paths': [],  # ids of any level paths this node is a part of
                        'is_root_element': False,
                        'betweener_paths': []
                    }
                    if is_boundary:
                        boundary_nodes.append(int(content[0]))
            node_file.close()

        # parse edge files into node relations
        with open(self.files['edge']) as edge_file:
            header = True
            for line in edge_file:
                if header:
                    header = False
                    continue
                content = list(filter(bool, line.split(' ')))
                if not '#' in content[0]:
                    nodes[int(content[1])]['relations'].append(int(content[2]))
                    nodes[int(content[2])]['relations'].append(int(content[1]))
            edge_file.close()

        # with open(self.files['ele']) as ele_file:
        #     header = True
        #     for line in edge_file:
        #         if header:
        #             header = False
        #             continue
        #         content = list(filter(bool, line.split(' ')))
        #         if not '#' in content[0]:
        #             nodes[int(content[1])]['relations'].append(int(content[2]))
        #             nodes[int(content[2])]['relations'].append(int(content[1]))
        #     edge_file.close()

        # sorts relations clockwise
        for node_id, node in nodes.items():
            nodes[node_id]['relations'] = sorted(node['relations'], key=(
                lambda related_node_id: (
                    self.calculate_clockwise_angle_and_distance(node, nodes.get(related_node_id)) # pylint: disable=W0640
                )
            ))

        levels = self.get_levels(nodes, boundary_nodes)

        for level in levels:
            for node_id in level['node_ids']:
                self.identify_special_nodes(nodes, node_id)

        return nodes, boundary_nodes, levels


    def identify_special_nodes(self, nodes, node_id): # pylint: disable=R0201
        """
        Identifies all of the special nodes in a given level
        """
        node = nodes[node_id]

        start_node_id = None
        end_node_id = None

        for index, related_node_id in enumerate(node['relations']):
            related_node = nodes[related_node_id]
            previous_node_id = node['relations'][(index - 1) % len(node['relations'])]
            previous_node = nodes[previous_node_id]
            if (
                    (previous_node['distance'] == node['distance']) and
                    (related_node['distance'] > node['distance'])
            ):
                start_node_id = related_node_id
            elif (
                    (related_node['distance'] == node['distance']) and
                    (previous_node['distance'] > node['distance'])
            ):
                end_node_id = previous_node_id

            if (start_node_id and end_node_id) and (start_node_id != end_node_id):
                nodes[start_node_id]['betweener_paths'].append(node['distance'])
                nodes[end_node_id]['betweener_paths'].append(node['distance'])
                nodes[node_id]['betweener_paths'].append(node['distance'])


    def identify_level_elements(self, nodes, node_ids_in_level):  # pylint: disable=R0914,R0201,R0915,R0912
        """
        Identifies all of the level cycles and level paths in a given level
        """
        # assume all node ids are NOT in a chordless cycle to begin with
        non_cycle_node_ids = dict(zip(node_ids_in_level, map(lambda i: True, node_ids_in_level)))

        level_cycles = []
        level_paths = []

        # Step 1: Define all edges and declare them as untraversed
        untraversed_edges = {}
        for node_id in node_ids_in_level:
            node = nodes.get(node_id)
            related_node_ids = list(filter(lambda id: id in node_ids_in_level, node['relations']))
            for related_node_id in related_node_ids:
                untraversed_edges["{}-{}".format(related_node_id, node_id)] = True
                untraversed_edges["{}-{}".format(node_id, related_node_id)] = True

        # given a starting path (array of two connected points), this will
        # traverse all connected points in a counter clockwise fashion
        def traverse_edges_for_cycles(path):
            # get next edge counter clockwise
            last_node = nodes.get(path[-1])
            second_to_last_node = nodes.get(path[-2])

            # NB: this relies on relations already having been sorted clockwise
            related_node_ids = list(filter(lambda id: id in node_ids_in_level, last_node['relations'])) # pylint: disable=C0301
            second_to_last_node_index = related_node_ids.index(second_to_last_node['id'])
            index = (second_to_last_node_index + 1) % len(related_node_ids)
            next_node_id = related_node_ids[index]

            # remove from traversed edges
            edge_id = "{}-{}".format(last_node['id'], next_node_id)
            if untraversed_edges.get(edge_id):
                del untraversed_edges[edge_id]

            if next_node_id in path:
                if next_node_id != second_to_last_node['id']:
                    level_cycle = path[path.index(next_node_id):]
                    for node_id in level_cycle:
                        # remove new node from traversed nodes
                        if non_cycle_node_ids.get(node_id):
                            del non_cycle_node_ids[node_id]
                    level_cycles.append(level_cycle)
            else:
                path.append(next_node_id)
                traverse_edges_for_cycles(path)

        def traverse_edges_for_path(path, prev_node_id=None):
            last_node = nodes.get(path[-1])
            if non_cycle_node_ids.get(last_node['id']):
                del non_cycle_node_ids[last_node['id']]
            related_node_ids = list(filter(lambda id: id in node_ids_in_level, last_node['relations'])) # pylint: disable=C0301
            for node_id in related_node_ids:
                if non_cycle_node_ids.get(node_id):
                    del non_cycle_node_ids[node_id]
                if node_id != prev_node_id:
                    path.append(node_id)
                    if node_id in non_cycle_node_ids:
                        traverse_edges_for_path(path, prev_node_id=node_id)
            return path

        # this loop identifies all level cycles
        while untraversed_edges:
            # pick an edge and add to the path, delete from traversed
            current_edge = next(iter(untraversed_edges))
            del untraversed_edges[current_edge]
            starting_path = list(map(int, current_edge.split('-')))
            traverse_edges_for_cycles(path=starting_path)

        # this loop identifies all level paths
        while non_cycle_node_ids:
            current_node_id = next(iter(non_cycle_node_ids))
            level_path = traverse_edges_for_path([current_node_id])
            level_paths.append(level_path)


        # remove duplicate cycles
        non_duplicate_cycles = []
        existing_cycles_as_sets = []
        for level_cycle in level_cycles:
            if set(level_cycle) not in existing_cycles_as_sets:
                non_duplicate_cycles.append(level_cycle)
            existing_cycles_as_sets.append(set(level_cycle))

        # remove duplicate paths
        non_duplicate_paths = []
        existing_paths_as_sets = []
        for level_path in level_paths:
            if set(level_path) not in existing_paths_as_sets:
                non_duplicate_paths.append(level_path)
            existing_paths_as_sets.append(set(level_path))


        # adds ids to nodes for level paths and level cycles
        for cycle_id, level_cycle in enumerate(non_duplicate_cycles):
            for node_id in level_cycle:
                node = nodes.get(node_id)
                if not cycle_id in node['level_cycles']:
                    node['level_cycles'].append(cycle_id)
                    if len(level_cycle) == 3:
                        node['is_root_element'] = True

        for path_id, level_path in enumerate(non_duplicate_paths):
            for node_id in level_path:
                node = nodes.get(node_id)
                if not path_id in node['level_paths']:
                    node['level_paths'].append(path_id)
                    node['is_root_element'] = True

        return non_duplicate_cycles, non_duplicate_paths

    def get_levels(self, nodes, boundary_nodes): # pylint: disable=R0201
        """
        returns an array of levels
        (level == nodes that all share the same minimum distance from the outer region)
        WARNING: mutates the "nodes" parameter and add a "distance" parameter to
        each node based on the distance from the boundary
        """
        # current distance = collection of all node ids with same minimum distance
        # from the outermost boundary
        levels = []

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

            level_cycles, level_paths = self.identify_level_elements(nodes, nodes_with_same_distance) # pylint: disable=C0301
            levels.append({
                'node_ids': nodes_with_same_distance,
                'cycles': level_cycles,
                'paths': level_paths
            })
            distance += 1
            nodes_with_same_distance = next_nodes_with_same_distance

        return levels

    # get a "slice" of nodes
    def get_slice(self, node_id, nodes_in_slice, is_origin=False, is_reverse=False):
        """
        Generate a "slice" of nodes given a starting node
        """
        if is_reverse:
            return self.get_reverse_slice(node_id, nodes_in_slice)
        return self.get_level_element_slice(node_id, nodes_in_slice, is_origin=is_origin)

    def get_level_element_slice(self, node_id, nodes_in_slice, is_origin=False):
        """
        Generate a "slice" of nodes given a starting node id, which we then use
        to find the first level element containing that node. We then move outward
        from each node in the level element to generate the slice
        """
        node = self.nodes[node_id]
        if node['distance'] == 0:
            nodes_in_slice[node_id] = []

        origin_node_ids = [node_id]
        if is_origin and node['level_cycles']:
            level_cycle_id = node['level_cycles'][0]
            origin_node_ids = self.levels[node['distance']]['cycles'][level_cycle_id]
        elif is_origin and node['level_paths']:
            level_path_id = node['level_paths'][0]
            origin_node_ids = self.levels[node['distance']]['paths'][level_path_id]

        for origin_node_id in origin_node_ids:
            for related_node_id in self.nodes[origin_node_id]['relations']:
                if self.nodes[related_node_id]['distance'] < self.nodes[origin_node_id]['distance']:
                    related_node_ids = nodes_in_slice.get(origin_node_id, [])
                    related_node_ids.append(related_node_id)
                    nodes_in_slice[origin_node_id] = related_node_ids
                    nodes_in_slice = self.get_slice(related_node_id, nodes_in_slice)
        return nodes_in_slice

    def get_reverse_slice(self, node_id, nodes_in_slice):
        """
        Generate a reverse "slice" of nodes given a starting node. We will move
        inward from a starting outer node in order to generate the slice.
        """
        node = self.nodes[node_id]

        for related_node_id in node['relations']:
            if self.nodes[related_node_id]['distance'] > node['distance']:
                if not nodes_in_slice.get(node_id):
                    nodes_in_slice[node_id] = [related_node_id]
                else:
                    nodes_in_slice[node_id].append(related_node_id)
                if not nodes_in_slice.get(related_node_id):
                    nodes_in_slice[related_node_id] = []
                self.get_reverse_slice(related_node_id, nodes_in_slice)
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
        else:
            betweener_path = set(self.nodes[node_id_1]['betweener_paths']).intersection(set(self.nodes[node_id_2]['betweener_paths'])) # pylint: disable=C0301
            if betweener_path:
                if (list(betweener_path)[0] % 2) == 1:
                    color = 'purple'
                else:
                    color = 'blue'
        if (node_id_1 in nodes_in_slice) and (node_id_2 in nodes_in_slice):
            color = '#42b983'

        if (
                (self.nodes[node_id_1].get('color', None) in ['yellow', 'green']) and
                (self.nodes[node_id_2].get('color', None) in ['yellow', 'green'])
        ):
            color = 'lightgreen'
        if (
                (self.nodes[node_id_1].get('color', None) in ['red', 'blue']) and
                (self.nodes[node_id_2].get('color', None) in ['red', 'blue'])
        ):
            color = 'purple'
        return (
            "    <line x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" style=\"stroke:{}; stroke-width: 1;\"/>\n" # pylint: disable=C0301
            .format(coords1[0], coords1[1], coords2[0], coords2[1], color)
        )

    def generate_svg(
            self, nodes=None, slice_origin_id=None, reverse_slice=False, colored_nodes=None
    ): # pylint: disable=R0914
        """
        Generate svg based on nodes
        """
        _nodes = nodes if nodes else self.nodes

        nodes_in_slice = self.get_slice(slice_origin_id, {}, is_origin=True, is_reverse=reverse_slice) if slice_origin_id else {} # pylint: disable=C0301
        html = "<svg xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\"1500px\" height=\"1000px\">\n" # pylint: disable=C0301
        html += "  <g>\n"

        drawn_edges = {}

        for node_id, node in _nodes.items():

            # if node_id % 2 == 0:
            if colored_nodes and (str(node_id) in colored_nodes):
                self.nodes[node_id]['color'] = colored_nodes.get(str(node_id), None)
                fill = self.nodes[node_id]['color']
            # elif node_id in nodes_in_slice:
            #     fill = '#42b983'
            # elif node['is_root_element']:
            #     fill = 'orange'
            # elif node.get('is_center'):
            #     fill = 'red'
            else:
                fill = 'white'

            for related_node_id in node['relations']:
                edge1 = "{}-{}".format(node_id, related_node_id)
                edge2 = "{}-{}".format(related_node_id, node_id)
                if not drawn_edges.get(edge1):
                    html += self.generate_line(node_id, related_node_id, nodes_in_slice)
                    drawn_edges[edge1] = True
                    drawn_edges[edge2] = True

            level_cycles = ','.join(map(str, node['level_cycles']))
            level_paths = ','.join(map(str, node['level_paths']))

            html += (
                "    <rect class=\"node\" id=\"{}\" x=\"{}\" y=\"{}\" height=\"8\" width=\"10\" style=\"stroke: {}; fill: {};\"/>\n" # pylint: disable=C0301
                .format(node['id'], node['coords'][0]-6, node['coords'][1]-3, 'black', fill)
            )
            html += (
                "    <text class=\"node\" id=\"{}\" level_cycles=\"{}\" level_paths=\"{}\" x=\"{}\" y=\"{}\" style=\"fill: {}; font-size: 8px;\">{}</text>\n" # pylint: disable=C0301
                .format(node['id'], level_cycles, level_paths, node['coords'][0]-5, node['coords'][1]+4, 'black', node['distance']) # pylint: disable=C0301
            )
        html += "  </g>\n"
        html += "</svg>"
        return html
