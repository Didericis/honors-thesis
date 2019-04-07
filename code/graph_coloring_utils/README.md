# Graph Coloring Utils

This is a command line utility for doing graph related calculations

### Requirements

- Git
- Python3 + pip

### Installation

Installation can be done by cloning the repo, navigating to this folder and running pip install on the directory

```
git install https://github.com/didericis/honors-thesis.git
cd honors-thesis/code/graph_coloring_utils
pip install --upgrade .
```

### Usage

```
Usage:
  gcutils distinct_4_colorings <v> [--count | --calc | --compare]

Option
  -h --help               Show help info
  --version               Show version
                          (you will need to have 'syk --test up' running)
  --count                 Count the number of colorings individually
  --calc                  Count the number of colorings using a formula
  --compare               Compare the --count and --calc values
Description:
  distinct_4_colorings    Given a chordless cycle with v vertices, this will
                          return all of the distinct, valid 4 colorings of that
                          cycle
```
