# MIT License
#
# Copyright (c) 2016-2019 Matthias Rost, Elias Doehne, Tom Koch, Alexander Elvers
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

from collections import defaultdict
import random
import numpy as np
import networkx as nx

from . import util

global_logger = util.get_logger(__name__, make_file=False, propagate=True)

class UndirectedGraph(object):
    """ Simple representation of an unidrected graph (without any further attributes as weights, costs etc.)
    """
    def __init__(self, name):
        self.name = name
        self.nodes = set()
        self.edges = set()

        self.neighbors = {}
        self.incident_edges = {}

    def add_node(self, node):
        self.nodes.add(node)
        self.neighbors[node] = set()
        self.incident_edges[node] = set()

    def add_edge(self, i, j):
        if i not in self.nodes or j not in self.nodes:
            raise ValueError("Node not in graph!")
        new_edge = frozenset([i, j])
        if new_edge in self.edges:
            global_logger.warning("Duplicate edge {}. Ignoring it!".format(new_edge))
        if len(new_edge) == 1:
            global_logger.warning("Loop edges are not allowed ({},{}). Not adding the edge!".format(i,j))
            return None

        self.neighbors[i].add(j)
        self.neighbors[j].add(i)
        self.incident_edges[i].add(new_edge)
        self.incident_edges[j].add(new_edge)
        self.edges.add(new_edge)
        return new_edge

    def remove_node(self, node):
        if node not in self.nodes:
            raise ValueError("Node not in graph.")

        edges_to_remove = list(self.incident_edges[node])

        for incident_edge in edges_to_remove:
            edge_as_list = list(incident_edge)
            self.remove_edge(edge_as_list[0], edge_as_list[1])

        del self.incident_edges[node]
        del self.neighbors[node]
        self.nodes.remove(node)

    def remove_edge(self, i, j):
        old_edge = frozenset([i, j])
        if i not in self.nodes or j not in self.nodes:
            raise ValueError("Nodes not in graph!")
        if old_edge not in self.edges:
            raise ValueError("Edge not in graph!")

        self.neighbors[i].remove(j)
        self.neighbors[j].remove(i)

        self.incident_edges[i].remove(old_edge)
        self.incident_edges[j].remove(old_edge)

        self.edges.remove(old_edge)

    def get_incident_edges(self, node):
        return self.incident_edges[node]

    def get_neighbors(self, node):
        return self.neighbors[node]

    def get_edge_representation(self):
        return [list(edge) for edge in self.edges]

    def check_connectedness(self):
        if len(self.nodes) == 0:
            return True
        root = next(iter(self.nodes))
        unvisited = set(self.nodes)
        to_process = [root]
        while len(to_process) > 0:
            current_node = to_process.pop(0)
            if not current_node in unvisited:
                continue
            for neighbor in self.neighbors[current_node]:
                if neighbor in unvisited:
                    to_process.append(neighbor)
            unvisited.remove(current_node)
        return len(unvisited) == 0

    def __str__(self):
        return "{} {} with following attributes: \n\t\tNodes{}\n\t\tEdges{}".format(type(self).__name__, self.name,
                                                                                    self.nodes, self.edges)


def get_undirected_graph_from_networkx_graph(nx_graph, name):
    ''' returns an undirected graph from the networkx graph
    '''

    graph = UndirectedGraph(name=name)

    for node in nx_graph.nodes():
        graph.add_node(node)

    for u,v in nx_graph.edges():
        graph.add_edge(u,v)

    return graph