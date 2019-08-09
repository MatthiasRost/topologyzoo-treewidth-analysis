# MIT License
#
# Copyright (c) 2019 Matthias Rost
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

import networkx as nx
import glob
import os
import pkg_resources

from . import util, datamodel

import numpy.random

global_logger = util.get_logger(__name__, make_file=False, propagate=True)

DATA_PATH = pkg_resources.resource_filename("topologyzoo_treewidth_analysis", "data/")

def get_networkx_topology_zoo_graphs():
    network_files = glob.glob(DATA_PATH  + "/topologyZoo/*.gml")
    consider_disconnected = True

    result = {} #will be a map of graph name to networkx graph

    for net_file in network_files:
        # Extract name of network from file path
        path, filename = os.path.split(net_file)
        network_name = os.path.splitext(filename)[0]

        graph = None
        try:
            global_logger.info("reading file {}".format(net_file))
            try:
                graph = nx.read_gml(net_file, label="id")
            except Exception as ex:
                if "duplicated" in str(ex) and "multigraph 1" in str(ex):
                    global_logger.warning("Multigraph detected; fixing the problem...")
                    with open(net_file, "r") as f:
                        graph_source = f.read()
                    graph_source = graph_source.replace("graph [", "graph [\n  multigraph 1")
                    graph = nx.parse_gml(graph_source, label="id")
                    global_logger.warning("\ttried to fix the multigraph issue")

            if graph is not None:
                undir_nx_graph = graph.to_undirected()
                undir_graph = datamodel.get_undirected_graph_from_networkx_graph(undir_nx_graph, network_name)
                global_logger.info("Successfully read graph {}".format(net_file))
                result[network_name] = undir_graph
            else:
                raise RuntimeError("Unsuccessful in reading graph {}".format(net_file))

        except Exception as ex:
            import traceback
            global_logger.error("reading file {} was NOT sucessful! \n\n\n".format(net_file))
            global_logger.error("{}\n\n\n".format(str(ex)))
            traceback.print_exc()

    return result