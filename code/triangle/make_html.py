nodes = {}
edges = []
current_distance = []

with open('test.1.node') as f:
    header = True
    for line in f:
        if header:
            header = False
            continue
        content = list(filter(lambda a: bool(a), line.split(' ')))
        if not '#' in content[0]:
            is_boundary = content[3] == '1\n'
            nodes[content[0]] = {
                'coords': [int(content[1]), int(content[2])],
                'is_boundary': is_boundary,
                'distance': 0 if is_boundary else None,
                'relations': []
            }
            if is_boundary:
                current_distance.append(content[0])
    f.close()

with open('test.1.edge') as f:
    header = True
    for line in f:
        if header:
            header = False
            continue
        content = list(filter(lambda a: bool(a), line.split(' ')))
        if not '#' in content[0]:
            edges.append([content[1], content[2]])
            nodes[content[1]]['relations'].append(content[2])
            nodes[content[2]]['relations'].append(content[1])
    f.close()


all = {}
distance = 0
while len(current_distance):
    next_distance = []
    for n in current_distance:
        nodes[n]['distance'] = distance
        for related_n in nodes[n]['relations']:
            if nodes[related_n].get('distance') == None:
                nodes[related_n]['distance'] = distance + 1
                next_distance.append(related_n)
    print('DISTANCE: ', distance)
    distance += 1
    current_distance = next_distance

first_isolated = None
for node, data in nodes.items():
    prev_distance = nodes[data['relations'][0]]['distance']
    data['is_isolated'] = True
    data['is_inner'] = True
    for n in data['relations']:
        data['is_isolated'] = data['is_isolated'] and (prev_distance == nodes[n]['distance'])
        data['is_inner'] = data['is_inner'] and (data['distance'] >= nodes[n]['distance'])
        prev_distance = nodes[n]['distance']
    if not first_isolated and data['is_isolated']:
        first_isolated = node

# # remove false positives for is_inner
# for node, data in nodes.items():
#     for n in data['relations']:
#         data['is_inner'] = data['is_inner'] and ((data['distance'] > nodes[n]['distance']) or (nodes[n]['is_inner']))


special_edges = {}

def get_special_edges(node):
    for related in nodes[node]['relations']:
        if nodes[related]['distance'] < nodes[node]['distance']:
            edges = special_edges.get(node, [])
            edges.append(related)
            special_edges[node] = edges
            get_special_edges(related)

if first_isolated:
    get_special_edges(first_isolated)
else:
    print('NO ISOLATED')




html = """
<html>
    <head>
        <script language="javascript" type="text/javascript">
            var i = 1;
            var x = 0;
            var y = 0;
            window.onkeydown = function(e) {
                var el = document.getElementsByTagName("g")[0];
                if (e.code === 'KeyI') {
                    i += .25;
                } else if (e.code === 'KeyO') {
                    i -= .25;
                } else if (e.code === 'ArrowRight') {
                    x -= 20;
                } else if (e.code === 'ArrowLeft') {
                    x += 20;
                } else if (e.code === 'ArrowDown') {
                    y -= 20;
                } else if (e.code === 'ArrowUp') {
                    y += 20;
                }
                el.setAttribute('transform', `scale(${i}) translate(${x} ${y})`);
            }
        </script>
    </head>
    <body>
"""

html += "        <svg  xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" width=\"100vw\" height=\"100vh\">\n"
html += "            <g>\n"
for edge in edges:
    coords1 = nodes[edge[0]]['coords']
    coords2 = nodes[edge[1]]['coords']
    color = 'lightgray'
    if nodes[edge[0]]['distance'] == nodes[edge[1]]['distance']:
        color = 'black'
    dir1 = special_edges.get(edge[0], [])
    dir2 = special_edges.get(edge[1], [])
    if (edge[1] in dir1) or (edge[0] in dir2):
        color = 'red'
    html += (
        "                <line x1=\"{}\" y1=\"{}\" x2=\"{}\" y2=\"{}\" style=\"stroke:{}; stroke-width: 1;\"/>\n"
        .format(coords1[0], coords1[1], coords2[0], coords2[1], color)
    )

for node, data in nodes.items():
    coordinates = data['coords']
    stroke = 'green' if data['is_boundary'] else 'black'
    if data['is_boundary']:
        fill = 'green'
    elif data['is_isolated']:
        fill = 'red'
    elif data['is_inner']:
        fill = 'yellow'
    else:
        fill = 'white'
    text_color = 'white' if data['is_boundary'] else 'black'
    html += (
        "                <rect x=\"{}\" y=\"{}\" height=\"8\" width=\"10\" style=\"stroke: {}; fill: {};\"/>\n"
        .format(coordinates[0]-6, coordinates[1]-3, stroke, fill)
    )
    html += (
        "                <text x=\"{}\" y=\"{}\" style=\"fill: {}; font-size: 8px;\">{}</text>\n"
        .format(coordinates[0]-5, coordinates[1]+4, text_color, data['distance'])
    )


html += "            </g>\n"
html += "    </svg>"
html += """
    </body>
</html>
"""

with open('map.html', 'w') as f:
    f.write(html)
    f.close()
