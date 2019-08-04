from subprocess import call
import random

points = {}
while len(points) < 500:
    x = random.randrange(1000)
    if not points.get(x):
        points[x] = random.randrange(1000)


with open('test.node', 'w') as f:
    print(f)
    header = "{}  2  0  0\n".format(len(points))
    f.write(header)
    i = 1
    for x, y in points.items():
        f.write("   {}    {}  {}\n".format(i, x, y))
        i+=1
    f.close()

call(['triangle', '-e', 'test.node'])

import make_html
