# --- README ---
#
# a 'coloring' is an array of color values, where each index represents a
# vertex, and the value at that index represents the coloring of that vertex
#
# we represent our colorings arrays as strings with '.' delimiters so we can
# use colorings as dictionary keys
#
# a color swap is any coloring that can be obtained by setting the color
# of all vertices that have color A in the root coloring to color B, and all
# vertices that have color B in the root coloring to color C
#
# a set of distinct colorings D is a set of colorings where no element in D
# can be obtained via any number of color swaps of any other element in D

COLORS = ['1', '2', '3', '4']
COLORSWAPS = [
    ['1', '2'],
    ['1', '3'],
    ['1', '4'],
    ['2', '3'],
    ['2', '4'],
    ['3', '4']
]


# this is a recursive function to get all of the possible colorings of for the
# all of the vertices up to the ith vertex in a cycle of length n given the
# previous i vertices have the coloring specificed
def find_4_colorings_recursion(coloring, n, i):
    new_colorings = []
    for color in COLORS:
        # next color cannot be same color as last color
        if (len(coloring)) and (color == coloring[len(coloring) - 1]):
            continue
        # color that completes the cycle cannot be same color as first color
        # (in addition to condition above)
        elif (len(coloring)) and (n < (i + 1)) and color == coloring[0]:
            continue
        # add this color to our coloring
        new_colorings = new_colorings + [coloring + [color]]

    # if we have just found the last vertex in our cycle, exit
    if n < (i + 1):
        return new_colorings
    else:
        _all_colorings = []
        # for all of our new colorings up to the ith vertex, find all of
        # the colorings up to the (i + 1)th vertex
        for new_coloring in new_colorings:
            _new_colorings = find_4_colorings_recursion(new_coloring, n, i + 1)
            _all_colorings = _all_colorings + _new_colorings
        return _all_colorings


# this will return all the possible colorings for a cycle of length n
def find_4_colorings_for_cycle(n):
    return list(map(
            lambda coloring: '.'.join(
                list(map(lambda color: str(color), coloring))
            ),
            find_4_colorings_recursion([], n, 1)
            ))


# this will swap color A with color B for a particular coloring
def colorswap(coloring, colorA, colorB):
    coloring = coloring.replace(colorA, '#')
    coloring = coloring.replace(colorB, colorA)
    return coloring.replace('#', colorB)


# this will create all of the possible swaps for a given coloring that can
# be obtained by 1 swap
def find_swaps(coloring):
    new_swaps = set()
    for swap in COLORSWAPS:
        color_swapped = colorswap(coloring, swap[0], swap[1])
        new_swaps.add(color_swapped)
    return new_swaps


# this will create all possible color swaps for a given root coloring that are
# possible after an arbitrary number of swaps
def find_all_swaps(root_coloring):
    prev_swaps = set()
    next_swaps = find_swaps(root_coloring)
    while prev_swaps.union(next_swaps) != prev_swaps:
        prev_swaps = next_swaps
        _next_swaps = next_swaps.copy()
        for swap in next_swaps:
            _next_swaps.update(find_swaps(swap))
        next_swaps = _next_swaps
    return prev_swaps


# this will return all of the distinct valid 4 colorings of a cycle of length n
def find_distinct_4_colorings_for_cycle(n):
    colorings = find_4_colorings_for_cycle(n)
    valid_colorings = []
    coloring_dict = {}

    for coloring in colorings:
        coloring_dict[coloring] = True

    for coloring in colorings:
        if coloring_dict[coloring]:
            valid_colorings = valid_colorings + [coloring]
            coloring_dict[coloring] = 'ROOT'
            swaps = find_all_swaps(coloring)
            for swap in swaps:
                if not coloring_dict[swap] == 'ROOT':
                    coloring_dict[swap] = False

    return valid_colorings
