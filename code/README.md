# Code

This folder contains a bunch of code intended to help with verifying and investigating claims about planar graphs

### graph_coloring_utils

This is a [pip](https://pypi.org/project/pip/) package for a command line utility containing most of the custom code written for investigating claims. Details about installation and usage can be found [here](./graph_coloring_utils)

### boltzman_planar_graphs

This is a program by [Eric Fusy](http://www.lix.polytechnique.fr/Labo/Eric.Fusy/) to generate a uniform random sample of planar graphs in linear time that was downloaded from his website. Paper can be found [here](http://www.lix.polytechnique.fr/Labo/Eric.Fusy/Articles/Fusy08_planar_graphs.pdf).

### random_planar_graph_generator

This is a rough attempt at a random planar graph generator that works by generating random cycles within different random cycles. It wasn't tested and work on it stopped after finding the random planar graph generator by Eric Fusy.
