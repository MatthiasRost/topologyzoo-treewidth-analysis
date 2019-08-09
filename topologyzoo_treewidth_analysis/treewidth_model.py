# MIT License
#
# Copyright (c) 2019 Matthias Rost, Elias Doehne
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


import itertools
import os
import numpy as np
import random
import time
from heapq import heappush, heappop
import subprocess
import enum
from collections import namedtuple

from . import datamodel, util

global_logger = util.get_logger(__name__, make_file=False, propagate=True)


""" This module contains data structures and algorithms related to treewidth based approximation approaches """

class TreeDecomposition(datamodel.UndirectedGraph):
    ''' Representation of a tree decomposition.'''

    def __init__(self, name):
        super(TreeDecomposition, self).__init__(name)

        self.node_bag_dict = {}  # map TD nodes to their bags
        self.representative_map = {}  # map graph nodes to representative TD nodes
        self.complete_graph_node_to_tree_node_map = {}

    def add_node(self, node, node_bag=None):
        ''' adds a node to the tree decomposition and stores the bag information; edges must be created externally.

        :param node:
        :param node_bag:
        :return: None
        '''
        if not node_bag:
            raise ValueError("Empty or unspecified node bag: {}".format(node_bag))
        if not isinstance(node_bag, frozenset):
            raise ValueError("Expected node bag as frozenset: {}".format(node_bag))
        super(TreeDecomposition, self).add_node(node)
        self.node_bag_dict[node] = node_bag
        # edges_to_create = set()
        for req_node in node_bag:
            if req_node not in self.representative_map:
                self.representative_map[req_node] = node
            if req_node not in self.complete_graph_node_to_tree_node_map:
                self.complete_graph_node_to_tree_node_map[req_node] = [node]
            else:
                self.complete_graph_node_to_tree_node_map[req_node].append(node)


    def remove_node(self, node):
        del self.node_bag_dict[node]


        for req_node in self.complete_graph_node_to_tree_node_map.keys():
            if node in self.complete_graph_node_to_tree_node_map[req_node]:
                self.complete_graph_node_to_tree_node_map[req_node].remove(node)
            if self.representative_map[req_node] == node:
                self.representative_map[req_node] = self.complete_graph_node_to_tree_node_map[req_node][0]

        super(TreeDecomposition, self).remove_node(node)

    @property
    def width(self):
        return max(len(bag) for bag in self.node_bag_dict.values()) - 1

    def get_bag_intersection(self, t1, t2):
        return self.node_bag_dict[t1] & self.node_bag_dict[t2]

    def get_representative(self, req_node):
        if req_node not in self.representative_map:
            raise ValueError("Cannot find representative for unknown node {}!".format(req_node))
        return self.representative_map[req_node]

    def is_tree_decomposition(self, graph):
        if not self._is_tree():
            print("Not a tree!")
            return False
        if not self._verify_all_nodes_covered(graph):
            print("Not all nodes are covered!")
            return False
        if not self._verify_all_edges_covered(graph):
            print("Not all edges are covered!")
            return False
        if not self._verify_intersection_property():
            print("Intersection Property does not hold!")
            return False
        return True

    def _is_tree(self):
        if not self.nodes:
            return True
        start_node = next(iter(self.nodes))
        visited = set()
        q = {start_node}
        while q:
            t = q.pop()
            visited.add(t)
            if len(self.get_neighbors(t) & visited) > 1:
                return False
            q |= self.get_neighbors(t) - visited

        return visited == set(self.nodes)

    def _verify_all_nodes_covered(self, req):
        return set(self.representative_map.keys()) == set(req.nodes)

    def _verify_all_edges_covered(self, req):
        for (i, j) in req.edges:
            # Check that there is some overlap in the sets of representative nodes:
            found_covering_bag = False
            for node_bag in self.node_bag_dict.values():
                if i in node_bag and j in node_bag:
                    found_covering_bag = True
                    break
            if found_covering_bag:
                break
        return True

    def _verify_intersection_property(self):
        # Check that subtrees induced by each graph node are connected
        for req_node in self.representative_map:
            subtree_nodes = {t for (t, bag) in self.node_bag_dict.items() if req_node in bag}
            start_node = self.get_representative(req_node)
            visited = set()
            q = {start_node}
            while q:
                t = q.pop()
                visited.add(t)
                subtree_neighbors = self.get_neighbors(t) & subtree_nodes
                unvisited_neighbors = (subtree_neighbors - visited)
                q |= unvisited_neighbors
            if not visited == subtree_nodes:
                return False
        return True


""" Computing tree decompositions """


class TreeDecompositionComputation(object):
    """
    Use the exact tree decomposition algorithm implementation by Hisao Tamaki and Hiromu Ohtsuka, obtained
    from https://github.com/TCS-Meiji/PACE2017-TrackA, to compute tree decompositions.

    It assumes that the path to the tree decomposition algorithm is stored in the environment variable PACE_TD_ALGORITHM_PATH
    """

    def __init__(self, graph, logger=None, timeout=None):
        self.graph = graph
        self.timeout = timeout
        if logger is None:
            self.logger = util.get_logger(__name__, make_file=False, propagate=True)
        else:
            self.logger = logger

        self.map_nodes_to_numeric_id = None
        self.map_numeric_id_to_nodes = None
        self.DEBUG_MODE = False




    def compute_tree_decomposition(self):
        td_alg_input = self._convert_graph_to_td_input_format()
        result = None
        # There is probably a better way...
        curr_dir = os.getcwd()
        PACE_TD_ALGORITHM_PATH = os.getenv("PACE_TD_ALGORITHM_PATH")
        if PACE_TD_ALGORITHM_PATH is None:
            raise ValueError("PACE_TD_ALGORITHM_PATH environment variable is not set!")
        os.chdir(PACE_TD_ALGORITHM_PATH)
        try:
            self.logger.info("Starting tw-exact on graph {}".format(self.graph.name))
            p = subprocess.Popen("./tw-exact", stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf8')
            stdoutdata, stderrdata = None, None
            try:
                stdoutdata, stderrdata = p.communicate(input=td_alg_input, timeout=self.timeout)
                self.logger.info(".. sending data:\n{}".format(td_alg_input))
            except subprocess.TimeoutExpired:
                self.logger.info("Timeout expired when trying to compute tree decomposition. Killing process and discarding potential result.")
                p.kill()
                p.communicate()
            if not stderrdata:
                self.logger.info(".. receiving tree decomposition:\n{}".format(stdoutdata))
                result = self._convert_result_format_to_tree_decomposition(stdoutdata)
                self.logger.info(".. successfully converted tree decomposition into our own format.")

        except subprocess.CalledProcessError as e:
            self.logger.error("Subprocess Error: {}".format(e))
            self.logger.error("Return code:      {}".format(e.returncode))
        finally:
            os.chdir(curr_dir)
        return result

    def _convert_graph_to_td_input_format(self):
        self.map_nodes_to_numeric_id = {node: str(idx) for (idx, node) in enumerate(sorted(self.graph.nodes), 1)}
        self.map_numeric_id_to_nodes = {v: k for (k, v) in self.map_nodes_to_numeric_id.items()}
        lines = ["p tw {} {}".format(len(self.graph.nodes), len(self.graph.edges))]
        for edge in sorted(self.graph.edges):
            i, j = edge
            lines.append("{} {}".format(
                self.map_nodes_to_numeric_id[i],
                self.map_nodes_to_numeric_id[j],
            ))
        if self.DEBUG_MODE:
            with open("pace_graph.txt", "w") as f:
                f.write("\n".join(lines))
                f.write("{}".format(self.map_nodes_to_numeric_id))
                f.write("{}".format(self.map_numeric_id_to_nodes))
        return "\n".join(lines)

    def _convert_result_format_to_tree_decomposition(self, computation_stdout):
        lines = computation_stdout.split("\n")
        td = TreeDecomposition("{}_TD".format(self.graph.name))
        for line in lines[1:]:
            line = [w.strip() for w in line.split() if w]
            if not line or line[0] == "c":  # ignore empty and comment lines
                continue
            elif line[0] == "b":
                bag_id = self._get_bagid(line[1])
                bag = frozenset([
                    self.map_numeric_id_to_nodes[i] for i in line[2:]
                ])
                td.add_node(bag_id, node_bag=bag)
            else:
                assert len(line) == 2
                i, j = line
                td.add_edge(
                    self._get_bagid(i),
                    self._get_bagid(j),
                )
        return td

    def _get_bagid(self, numeric_id):
        return "bag_{}".format(numeric_id)


def compute_tree_decomposition(graph, timeout=None):
    return TreeDecompositionComputation(graph, logger=global_logger, timeout=timeout).compute_tree_decomposition()