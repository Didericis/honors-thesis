import uuid
import random
import json

all_vertices = {}
num_cycles = 0


class CycleSpawner:
    is_spawnable = True

    def spawn_random_cycle(self, ancestry=[]):
        raise NotImplementedError()


class Edge(CycleSpawner):
    def __init__(self, v1, v2, id=None):
        self.id = id or str(uuid.uuid1())
        self.v1 = v1
        self.v2 = v2
        self.is_spawnable = True

    def spawn_random_cycle(self, ancestry):
        if not self.is_spawnable:
            raise Exception('Edge {} is not spawnable!'.format(self))

        self.is_spawnable = False
        random_cycle = Cycle.random(edge=self, ancestry=ancestry)
        random_cycle.spawn_random_interior()
        return random_cycle

    def __str__(self):
        return self.id


class Vertex(CycleSpawner):
    def __init__(self, id=None):
        self.id = id or str(uuid.uuid1())
        all_vertices[str(self)] = self

    def spawn_random_cycle(self, ancestry):
        random_cycle = Cycle.random(ancestry=ancestry)
        random_cycle.spawn_random_interior()
        return random_cycle

    def __str__(self):
        return self.id


class Cycle:
    @staticmethod
    def random_nested_graph():
        cycle = Cycle(3)
        cycle.spawn_random_interior()
        return cycle

    @staticmethod
    def random(**kwargs):
        return Cycle(random.randint(3, 10), **kwargs)

    def __init__(self, length, ancestry=[], edge=None, vertex=None):
        if (length < 3):
            raise Exception("Cycle cannot have length less than 3!")
        if (edge and vertex):
            raise Exception("Cycle cannot start from both vertex and edge!")
        global num_cycles

        self.id = str(uuid.uuid1())
        self.ancestry = ancestry
        self.interior = []
        self.edges = []
        self.vertices = []

        if vertex:
            self.vertices = [vertex]
        if edge:
            self.vertices = [edge.v1, edge.v2]
            self.edges = [edge]

        while (len(self.vertices) < length):
            vertex = Vertex()

            if len(self.vertices) == 0:
                self.vertices.append(vertex)
                continue

            first_vertex = self.vertices[0]
            last_vertex = self.vertices[-1]
            self.vertices.append(vertex)

            if last_vertex:
                edge = Edge(v1=last_vertex, v2=vertex)
                self.edges.append(edge)

            if len(self.vertices) == length:
                edge = Edge(v1=last_vertex, v2=first_vertex)
                self.edges.append(edge)

        num_cycles += 1

    @property
    def random_spawnable(self):
        spawnable_edges = list(filter(lambda e: e.is_spawnable, self.edges))
        random_spawnables = spawnable_edges + self.vertices
        return random.choice(random_spawnables)

    def spawn_random_connected(self):
        return self.random_spawnable.spawn_random_cycle(ancestry=self.ancestry)

    def spawn_random_interior(self):
        if len(self.ancestry) > 3:
            return

        ancestry = self.ancestry + [self]
        self.interior.append(Cycle.random(ancestry=ancestry))

        while len(self.interior) < 8:
            random_interior = random.choice(self.interior)
            random_cycle = random_interior.spawn_random_connected()
            self.interior.append(random_cycle)

    def to_dict(self):
        return {
            "vertices": list(map(str, self.vertices)),
            "edges": list(map(str, self.edges)),
            "interior": list(map(lambda c: c.to_dict(), self.interior))
        }

    def __str__(self):
        return self.id


cycle = Cycle.random_nested_graph()
with open('random_nested_graph.json', 'w') as outfile:
    json.dump(cycle.to_dict(), outfile, indent=4)
