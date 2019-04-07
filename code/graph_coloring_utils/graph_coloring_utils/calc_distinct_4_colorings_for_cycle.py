import math


def recursive_step(n):
    sum = 0
    for i in range(n):
        a = math.pow(3, n-i-1) * math.pow(-1, i)
        sum += a
    return sum


def calc_distinct_4_colorings_for_cycle(n):
    if (n == 1) or (n == 2):
        return 1
    sum = 0
    for i in range(n-2):
        sum += recursive_step(i + 1)
    return int(sum + (1 - math.pow(-1, n-1))/2)
