from enum import Enum
from typing import Tuple
import networkx as nx
from type_aliases import Node, Edge

class BayesNetwork:
    
    def __init__(self, season: dict[str, list[float]], fragEdgesCPT: dict[Edge, float], nodesCPT: dict[Node, float]):
        self._season = season
        self._fragEdgesCPT = fragEdgesCPT
        self._nodesCPT = nodesCPT
        self._bn: nx.DiGraph = nx.DiGraph()
        nodes = list(nodesCPT.keys())
        fragEdges = list(fragEdgesCPT.keys())
        self._bn.add_nodes_from({"season"})
        self._bn.add_nodes_from(fragEdges)
        self._bn.add_nodes_from(nodes)
        self._bn.add_edges_from([("season", node) for node in nodes] + \
            [(node, edge) for node in nodes for edge in fragEdges if node in edge])
        self._eveidence: dict[Edge | Node, bool | str , str] = {}

    def EnumerationAsk(self, query: Node | Edge | str, e: dict[Edge | Node, bool | str , str]) -> dict[str, float]:
        """
        The enumeration-ask algorithm for inference in Bayesian networks.
        """
        Q = {}
        options = ['low', 'medium', 'high'] if isinstance(query, str) else [True, False]
        for q in options:
            e[query] = q
            Q[q] = self.EnumerationAll(list(nx.topological_sort(self._bn)), e)
        return self.Normalize(Q)

    def EnumerationAll(self, nodes: list[Node], e: dict[Edge | Node, bool | str , str]) -> float:
        """
        The enumeration-all algorithm for inference in Bayesian networks.
        """
        # edge | bool (parent node)
        # node | string = 'low' med or high (parent season)
        if len(nodes) == 0:
            return 1.0
        y = nodes[0]
        options = ['low', 'medium', 'high'] if isinstance(y, str) else [True, False]
        if y in e:
            return self.Probability(y, e, e[y]) * self.EnumerationAll(nodes[1:], e)
        return sum(self.Probability(y, e, option) *
                   self.EnumerationAll(nodes[1:], e.update({y : option})) for option in options)

    def Probability(self, y: Node | Edge | str, e: dict[Edge | Node, bool | str , str], option: str | bool) -> float:
        if isinstance(y, str): return self._season[option]
        if option:
            return self.VarCPT(y)[y][self.Parent(y, e)]
        return 1 - self.VarCPT(y)[y][self.Parent(y, e)]

    def VarCPT(self, var: Node | Edge | str):
        """
        Returns the Conditional Probability Table (CPT) for the given variable.
        """
        if isinstance(var, str): return self._season
        if isinstance(var, Node): return self._nodesCPT
        if isinstance(var, Edge): return self._fragEdgesCPT
        return None

    def Parent(self, node: Node | Edge | str, e: dict[Edge | Node, bool | str , str]):
        """
        Returns the parent nodes of the given node in the Bayesian network.
        """
        if node == "season": return 0
        if isinstance(node, Node): return e["season"]
        if isinstance(node, Edge): return tuple(e[node[0]], e[node[1]])
        return None

    def Normalize(self, queryDict: dict[str, float]) -> dict[str, float]:
        """
        Normalize the given dictionary of probabilities.
        """
        sumQ = sum(queryDict.values())
        return {k: v/sumQ for k, v in queryDict.items()}
