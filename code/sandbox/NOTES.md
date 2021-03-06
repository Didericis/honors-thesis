## Conjecture

Any graph with only triangular faces that can be embedded in R^n such that no two faces intersect has a chromatic number of n+2.

## Planar graphs

Consider any arbitrary embedding of a graph in the plane that is maximally planar. Embedding is G

- CLAIM: The outermost cycle of G will be a 3 cycle
- DEF: The induced subgraph of G made up of vertices a minimum distance of n away from a vertex in the outermost cycle is level n, or L_n
- CLAIM: The inner dual of L_n will always be a tree
- CLAIM: Any level can be composed of "level elements", which must be one of 2 types:
  - chordless cycle (cycle level element)
  - path (each disjoint induced subgraph of the level made up of all vertices/edges in the level minus any edges in chordless cycles or vertices that only have edges in chordless cycles)
- CLAIM: each level element shares at most 2 vertices with another level element
- CLAIM: If a level cycle has more than 3 vertices, when that cycle is mapped onto G, that cycle must surround at least one vertex in G

- Pruning Procedure:
  - Remove all vertices of G that sit inside of a 3 cycle in a level other than the outermost level
    - CLAIM: They're a part of a smaller maximally planar graph, and we can apply proof recursively to show they can be colored

- Slicing Procedure:
  - For each level element in L_n, excluding level cycles made up of more than 3 vertices, add level element to slice:
    - add all vertices in L_{n-1} that form an edge with the current slice, except those vertices that are in other slices, into the current slice
    - add all vertices in L_{n-1} in another slice that form an edge with a vertex in level L_{n-1} and with level L_{n} in the current slice into the current slice
    - repeat procedure for L_{n-2}, L_{n-3}, etc, and stop when L_{x} has only one vertex
  - Repeat for each level element in L_{n+1}, L_{n+2}, L_{n+3}, etc

- CLAIM: the lowest level of the slice either has no cycle or a 3 cycle (true by definition)
- CLAIM: if a level of a slice forms a cycle, then all lower levels besides the lowest level must form a cycle
  - lowest level could be any level element

- CLAIM: two level slices can have at most 2 vertices in common that are on the same level
  - if 2 vertices in common on the same level, those common vertices must be on the uppermost level of one slice and the lowermost level of the other slice

- [OBSERVATION 1](observation_1.png):
  - Cannot always alternate two colors around a level cycle with only 1 exception
- [OBSERVATION 2](observation_2.png):
  - Going counter clockwise with first sequence and only moving up a level on the last edge on a node with multiple edges between levels does results in conflicts when going up via same pattern with second sequence


### TODO:

- [x] Add ability to specify nodes when creating new graphs
- [x] Add ability to print graph info to site
- [ ] Add ability to list and select level elements
- [ ] Add ability to fold level elements and save intermediary svg steps
