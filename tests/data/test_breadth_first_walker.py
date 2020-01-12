# -*- coding: utf-8 -*-
#
# Copyright 2017-2020 Data61, CSIRO
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
import networkx as nx
from stellargraph.data.explorer import SampledBreadthFirstWalk
from stellargraph.core.graph import StellarGraph, StellarDiGraph


def create_test_graph():
    """
    Creates a simple graph for testing the BreadthFirstWalk class. The node ids are string or integers.

    :return: A simple graph with 13 nodes and 24 edges (including self loops for all but two of the nodes) in
    StellarGraph format.
    """
    g = nx.Graph()
    edges = [
        ("0", 1),
        ("0", 2),
        (1, 3),
        (1, 4),
        (3, 6),
        (4, 7),
        (4, 8),
        (2, 5),
        (5, 9),
        (5, 10),
        ("0", "0"),
        (1, 1),
        (3, 3),
        (6, 6),
        (4, 4),
        (7, 7),
        (8, 8),
        (2, 2),
        (5, 5),
        (9, 9),
        (
            "self loner",
            "self loner",
        ),  # node that is not connected with any other nodes but has self loop
    ]

    g.add_edges_from(edges)
    g.add_node(
        "loner"
    )  # node that is not connected to any other nodes and not having a self loop

    g = StellarGraph(g)

    return g


def expected_bfw_size(n_size):
    """
    Calculates the number of nodes generated by a single BFW for a single root node.
    :param n_size: <list> The number of neighbours at each depth level
    :return: The size of the list returned by a single BFW on a single root node
    """
    total = []
    for i, d in enumerate(n_size):
        if i == 0:
            total.append(d)
        else:
            total.append(total[-1] * d)
    return sum(total) + 1  # add the root node


class TestBreadthFirstWalk(object):
    def test_parameter_checking(self):
        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["0", 1]
        n = 1
        n_size = [1]

        with pytest.raises(ValueError):
            # nodes should be a list of node ids even for a single node
            bfw.run(nodes=None, n=n, n_size=n_size)
        with pytest.raises(ValueError):
            bfw.run(nodes=0, n=n, n_size=n_size)

        # n has to be positive integer
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=-1, n_size=n_size)
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=10.1, n_size=n_size)
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=0, n_size=n_size)

        # n_size has to be list of positive integers
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=n, n_size=0)
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=n, n_size=[-5])
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=-1, n_size=[2.4])
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=n, n_size=(1, 2))
        # seed must be positive integer or 0
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=n, n_size=n_size, seed=-1235)
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=n, n_size=n_size, seed=10.987665)
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=n, n_size=n_size, seed=-982.4746)
        with pytest.raises(ValueError):
            bfw.run(nodes=nodes, n=n, n_size=n_size, seed="don't be random")

        # If no neighbours are sampled, then just the start node should be returned, e.g.:
        # subgraph = bfw.run(nodes=["0"], n=1, n_size=[])
        # assert len(subgraph) == 1
        # assert len(subgraph[0]) == 1
        # assert subgraph[0][0] == "0"
        # However, by consensus this is an error:
        with pytest.raises(ValueError):
            bfw.run(nodes=["0"], n=1, n_size=[])

        # If no root nodes are given, an empty list is returned which is not an error but I thought this method
        # is the best for checking this behaviour.
        nodes = []
        subgraph = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraph) == 0

    def test_walk_generation_single_root_node_loner(self):
        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["loner"]
        n = 1
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        assert len(subgraphs[0]) == 1  # all elements should the same node
        assert subgraphs[0][0] == "loner"

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        assert len(subgraphs[0]) == expected_bfw_size(n_size)  # "loner" plus None
        assert subgraphs[0][0] == "loner"
        assert subgraphs[0][1] is None

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        # "loner" plus 2 * None + 2 * 2 * None
        assert len(subgraphs[0]) == expected_bfw_size(n_size)
        assert subgraphs[0][0] == "loner"
        assert subgraphs[0][1] is None
        assert subgraphs[0][2] is None
        assert subgraphs[0][6] is None

        n_size = [3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        # "loner" plus 3 * None + 3 * 2 * None
        assert len(subgraphs[0]) == expected_bfw_size(n_size)
        assert subgraphs[0][0] == "loner"

        n = 3
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        for subgraph in subgraphs:
            assert len(subgraph) == 1  # root node only
            assert subgraph[0] == "loner"

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        for subgraph in subgraphs:
            # "loner" plus None
            assert len(subgraph) == expected_bfw_size(n_size)
            assert subgraph[0] == "loner"

        n = 99
        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        for subgraph in subgraphs:
            # "loner" plus 2 * None + 2 * 2 * None
            assert len(subgraph) == expected_bfw_size(n_size)
            assert subgraph[0] == "loner"

        n = 17
        n_size = [3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        for subgraph in subgraphs:
            # "loner" plus 3 * None + 3 * 2 * None
            assert len(subgraph) == expected_bfw_size(n_size)
            assert subgraph[0] == "loner"

    def test_directed_walk_generation_single_root_node(self):

        g = nx.DiGraph()
        edges = [
            ("root", 2),
            ("root", 1),
            ("root", "0"),
            (2, "c2.1"),
            (2, "c2.2"),
            (1, "c1.1"),
        ]
        g.add_edges_from(edges)
        g = StellarDiGraph(g)

        def _check_directed_walk(walk, n_size):
            if len(n_size) > 1 and n_size[0] > 0 and n_size[1] > 0:
                for child_pos in range(n_size[0]):
                    child = walk[child_pos + 1]
                    grandchildren_start = 1 + n_size[0] + child_pos * n_size[1]
                    grandchildren_end = grandchildren_start + n_size[1]
                    grandchildren = walk[grandchildren_start:grandchildren_end]
                    if child == "root":  # node with three children
                        for grandchild in grandchildren:
                            assert grandchild in [0, 1, 2]
                    elif child == "0":  # node without children
                        for grandchild in grandchildren:
                            assert grandchild == "root"
                    elif child == 1:  # node with single child
                        for grandchild in grandchildren:
                            assert grandchild in ["c1.1", "root"]
                    elif child == 2:  # node with two children
                        for grandchild in grandchildren:
                            assert grandchild in ["c2.1", "c2.2", "root"]
                    else:
                        assert 1 == 0

        bfw = SampledBreadthFirstWalk(g)

        nodes = ["root"]
        n = 1
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        assert len(subgraphs[0]) == 1  # all elements should be the same node
        assert subgraphs[0][0] == "root"

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        assert len(subgraphs[0]) == expected_bfw_size(n_size)  # "root" plus child
        assert subgraphs[0][0] == "root"

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        # "root" plus 2 * child + 2 * 2 * grandchild or None
        assert len(subgraphs[0]) == expected_bfw_size(n_size)
        assert subgraphs[0][0] == "root"
        assert subgraphs[0][1] is not None
        assert subgraphs[0][2] is not None
        _check_directed_walk(subgraphs[0], n_size)

        n_size = [3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        # "root" plus 3 * child + 3 * 2 * grandchild or None
        assert len(subgraphs[0]) == expected_bfw_size(n_size)
        assert subgraphs[0][0] == "root"
        _check_directed_walk(subgraphs[0], n_size)

        n = 3
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        for subgraph in subgraphs:
            assert len(subgraph) == 1  # root node only
            assert subgraph[0] == "root"

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        for subgraph in subgraphs:
            # "root" plus child
            assert len(subgraph) == expected_bfw_size(n_size)
            assert subgraph[0] == "root"

        n = 99
        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        for subgraph in subgraphs:
            # "root" plus 2 * child + 2 * 2 * grandchild or None
            assert len(subgraph) == expected_bfw_size(n_size)
            assert subgraph[0] == "root"
            _check_directed_walk(subgraph, n_size)

        n = 17
        n_size = [3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n
        for subgraph in subgraphs:
            # "root" plus 3 * child + 3 * 2 * grandchild or None
            assert len(subgraph) == expected_bfw_size(n_size)
            assert subgraph[0] == "root"

    def test_walk_generation_single_root_node_self_loner(self):
        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["self loner"]
        n = 1

        n_size = [0]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should be same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should be same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should be same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should be same node
        assert nodes[0] in set(subgraphs[0])

        n = 3
        n_size = [0]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should be same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should be same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should be same node
        assert nodes[0] in set(subgraphs[0])

        n_size = [3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)
        assert len(set(subgraphs[0])) == 1  # all elements should the same node
        assert nodes[0] in set(subgraphs[0])

    def test_walk_generation_single_root_node(self):

        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["0"]
        n = 1
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == expected_bfw_size(n_size=n_size)

        # subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        # assert len(subgraphs[0]) == 2

        n_size = [2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [1, 1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [2, 2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [2, 3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

        n_size = [2, 3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs[0]) == len(nodes) * n * expected_bfw_size(n_size=n_size)

    def test_walk_generation_many_root_nodes(self):

        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["0", 2]
        n = 1
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for i, subgraph in enumerate(subgraphs):
            assert len(subgraph) == 1
            assert subgraph[0] == nodes[i]  # should equal the root node

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [1, 1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3, 3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2, 3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2, 3, 2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

    def test_walk_generation_number_of_walks_per_root_nodes(self):

        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = [1]
        n = 2
        n_size = [0]

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for i, subgraph in enumerate(subgraphs):
            assert len(subgraph) == expected_bfw_size(n_size=n_size)
            assert subgraph[0] == nodes[0]  # should equal the root node

        n_size = [1]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == len(nodes) * n
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        #############################################################
        nodes = [1, 5]
        n_size = [1]
        n = 2

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [2]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        #############################################################
        nodes = [1, 5]
        n_size = [2, 2]
        n = 3

        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [3, 3]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

        n_size = [4, 4]
        subgraphs = bfw.run(nodes=nodes, n=n, n_size=n_size)
        assert len(subgraphs) == n * len(nodes)
        for subgraph in subgraphs:
            assert len(subgraph) == expected_bfw_size(n_size=n_size)

    def test_fixed_random_seed(self):

        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        w0 = bfw.run(nodes=[1], n=1, n_size=[7], seed=42)
        w1 = bfw.run(nodes=[1], n=1, n_size=[7], seed=1010)

        assert len(w0) == len(w1)
        assert w0 != w1

        w0 = bfw.run(nodes=[1], n=1, n_size=[7], seed=42)
        w1 = bfw.run(nodes=[1], n=1, n_size=[7], seed=42)

        assert len(w0) == len(w1)
        assert w0 == w1

        w0 = bfw.run(nodes=[1], n=5, n_size=[12], seed=101)
        w1 = bfw.run(nodes=[1], n=5, n_size=[12], seed=101)

        assert len(w0) == len(w1)
        assert w0 == w1

        w0 = bfw.run(nodes=[9, "self loner"], n=1, n_size=[12], seed=101)
        w1 = bfw.run(nodes=[9, "self loner"], n=1, n_size=[12], seed=101)

        assert len(w0) == len(w1)
        assert w0 == w1

        w0 = bfw.run(nodes=[1, "self loner", 4], n=5, n_size=[12], seed=101)
        w1 = bfw.run(nodes=[1, "self loner", 4], n=5, n_size=[12], seed=101)

        assert len(w0) == len(w1)
        assert w0 == w1

    def test_benchmark_bfs_walk(self, benchmark):
        g = create_test_graph()
        bfw = SampledBreadthFirstWalk(g)

        nodes = ["0"]
        n = 5
        n_size = [5, 5]

        benchmark(lambda: bfw.run(nodes=nodes, n=n, n_size=n_size))
