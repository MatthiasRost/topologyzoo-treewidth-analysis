# MIT License
#
# Copyright (c) 2016-2018 Matthias Rost, Elias Doehne, Tom Koch, Alexander Elvers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import os
import sys
import click

from . import util
from . import topology_zoo_reader
from . import treewidth_model

try:
    import cPickle as pickle
except ImportError:
    import pickle


@click.group()
def cli():
    pass

import logging


def initialize_root_logger(filename, print_level=logging.INFO, file_level=logging.DEBUG, allow_override=False):
    if not allow_override and filename is not None and os.path.exists(filename):
        raise ValueError("Attempted to overwrite existing log file:  {}".format(filename))
    print("Initializing root logger: {}".format(filename))
    fmt = '%(levelname)-10s %(asctime)s %(lineno)4d:%(name)-32s\t %(message)s'
    logging.basicConfig(filename=filename,
                        filemode='w',
                        level=file_level,
                        format=fmt)

    root_logger = logging.getLogger()

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(print_level)
    root_logger.addHandler(stdout_handler)
    root_logger.info("Initialized Root Logger")
    return root_logger

@cli.command()
def compute_topologyzoo_treewidths():
    """Computes the treewidth of all contained topology zoo graphs. Stores the output in the output/ folder and the log in log/."""
    util.ExperimentPathHandler.initialize(check_emptiness_log=False, check_emptiness_output=False)
    log_file = os.path.join(util.ExperimentPathHandler.LOG_DIR, "compute_topologyzoo_treewidths.log")
    logger = initialize_root_logger(log_file, allow_override=True)
    graph_dictionary = topology_zoo_reader.get_networkx_topology_zoo_graphs()
    tw_dictionary = {}
    for graph_name, graph in graph_dictionary.items():
        td = treewidth_model.compute_tree_decomposition(graph)
        if td.is_tree_decomposition(graph):
            logger.info("Returned tree decomposition of width {} for graph {} is valid!".format(td.width, graph_name))
        else:
            raise ValueError("Returned tree decomposition is NOT valid!")
        tw_dictionary[graph_name] = td.width

    output_file = os.path.join(util.ExperimentPathHandler.OUTPUT_DIR,"topologyzoo_treewidths.txt")

    logger.info("Writing resuling treewidths to {}".format(output_file))
    with open(output_file, "w") as f:
        f.write("#{:20s}\t{:>10s}\t{:>10s}\t{:>10s}\n".format("graph_name", "nodes", "edges", "treewidth"))
        for graph_name in sorted(list(graph_dictionary.keys())):
            graph = graph_dictionary[graph_name]
            number_nodes = len(graph.nodes)
            number_edges = len(graph.edges)
            treewidth = tw_dictionary[graph_name]
            f.write("{:21s}\t{:10d}\t{:10d}\t{:10d}\n".format(graph_name, number_nodes, number_edges, treewidth))

    logger.info("\tdone.")


if __name__ == '__main__':
    cli()
