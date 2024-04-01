from __future__ import annotations
import networkx as nx
import copy as cp
from type_aliases import Node, Edge, BNNode

class BayesNetwork:
    """
    Represents a Bayesian network.

    Attributes:
    - season: A dictionary representing the probabilities of different seasons.
    - fragEdgesCPT: A dictionary representing the Conditional Probability Table (CPT) for fragment edges.
    - nodesCPT: A dictionary representing the CPT for nodes.
    - bn: A directed graph representing the Bayesian network.
    - evidence: A dictionary representing the evidence for inference.

    Methods:
    - EnumerationAsk: Performs inference using the enumeration-ask algorithm.
    - EnumerationAll: Performs inference using the enumeration-all algorithm.
    - Probability: Calculates the probability of a variable given evidence.
    - VarCPT: Returns the CPT for a given variable.
    - Parent: Returns the parent nodes of a given node in the Bayesian network.
    - Normalize: Normalizes a dictionary of probabilities.
    """

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
        self._bn.add_edges_from([("season", node) for node in nodes])
        self._bn.add_edges_from([(node, edge) for node in nodes for edge in fragEdges if node in edge])
        self._evidence: dict[Edge | Node, bool | str , str] = {}

    @property
    def bn(self) -> nx.DiGraph:
        """
        Returns the Bayesian network associated with this object.
        
        Returns:
            nx.DiGraph: The Bayesian network.
        """
        return self._bn

    @property
    def season(self) -> dict[str, list[float]]:
        """
        Returns the season dictionary containing probabilities for each season.

        Returns:
            dict[str, list[float]]: A dictionary where the keys
                represent the seasons and the values are lists of probabilities.
        """
        return self._season

    @property
    def fragEdgesCPT(self) -> dict[Edge, float]:
        """
        Returns the conditional probability table (CPT) for the fragmented edges in the Bayes network.

        The CPT is represented as a dictionary where the
            keys are the edges and the values are the corresponding probabilities.

        Returns:
            dict[Edge, float]: The conditional probability table for the fragmented edges.
        """
        return self._fragEdgesCPT

    @property
    def nodesCPT(self) -> dict[Node, float]:
        """
        Returns the conditional probability table (CPT) for each node in the Bayesian network.

        Returns:
            dict[Node, float]: A dictionary mapping each node to its corresponding CPT.
        """
        return self._nodesCPT

    def EnumerationAsk(self, query: BNNode, e: dict[Edge | Node, bool | str , str]) -> dict[str, float]:
        """
        Performs inference using the enumeration-ask algorithm.

        Args:
        - query: The variable to query.
        - e: The evidence for inference.

        Returns:
        A dictionary containing the probabilities of the query variable.
        """
        Q = {}
        query = [tuple(sorted(q)) if isinstance(q, tuple) and q and isinstance(q[0], tuple) else q for q in query][0]
        options = ['low', 'medium', 'high'] if isinstance(query, str) else [True, False]
        if query in e:
            otherOptions = options - e[query]
            return {e[query]: 1.0} | {other: 0.0 for other in otherOptions}
        for q in options:
            e[query] = q
            barrenBN = self.RemoveBarrenNodes(query, e)
            Q[q] = barrenBN.EnumerationAll(list(nx.topological_sort(barrenBN.bn)), e)
        print(Q)
        return self.Normalize(Q)

    def EnumerationAll(self, nodes: list[Node], e: dict[Edge | Node, bool | str , str]) -> float:
        """
        Performs inference using the enumeration-all algorithm.

        Args:
        - nodes: The nodes in the Bayesian network.
        - e: The evidence for inference.

        Returns:
        The probability of the evidence.
        """
        import numpy as np

        if len(nodes) == 0:
            return 1.0
        y = nodes[0]
        if isinstance(y, tuple) and y and isinstance(y[0], tuple): y = tuple(sorted(y))
        options = ['low', 'medium', 'high'] if isinstance(y, str) else [True, False]
        if y in e:
            a = self.Probability(y, e, e[y])
            b = self.EnumerationAll(nodes[1:], e)
            print(y)
            print(a)
            print(b)
            return a * b
        a = [self.Probability(y, e, option) for option in options]
        b = [self.EnumerationAll(nodes[1:], e | {y : option}) for option in options]
        print(y, a, b)
        print(e)
        print('\n')
        return np.inner(a, b)

    def Probability(self, y: BNNode, e: dict[Edge | Node, bool | str , str], option: str | bool) -> float:
        """
        Calculates the probability of a variable given evidence.

        Args:
        - y: The variable to calculate the probability for.
        - e: The evidence for inference.
        - option: The value of the variable.

        Returns:
        The probability of the variable given the evidence.
        """
        if isinstance(y, str): return self.season[option][0]
        if option:
            return self.VarCPT(y)[self.Parent(y, e)]
        return 1 - self.VarCPT(y)[self.Parent(y, e)]

    def VarCPT(self, node: BNNode):
        """
        Returns the Conditional Probability Table (CPT) for the given variable.

        Args:
        - node: The variable to get the CPT for.

        Returns:
        The CPT for the variable.
        """
        if isinstance(node, str): return self.season
        if isinstance(node, tuple) and node and isinstance(node[0], int): return self._nodesCPT[node]
        return self._fragEdgesCPT[node]

    def Parent(self, node: BNNode, e: dict[Edge | Node, bool | str , str]):
        """
        Returns the parent nodes of the given node in the Bayesian network.

        Args:
        - node: The node to get the parent nodes for.
        - e: The evidence for inference.

        Returns:
        The parent nodes of the given node.
        """
        if node == "season": return 0
        if isinstance(node, tuple) and node and isinstance(node[0], int): return e['season']
        return (e[node[0]], e[node[1]])

    def Normalize(self, queryDict: dict[str, float]) -> dict[str, float]:
        """
        Normalizes a dictionary of probabilities.

        Args:
        - queryDict: The dictionary of probabilities to normalize.

        Returns:
        The normalized dictionary of probabilities.
        """
        sumQ = sum(queryDict.values())
        return {k: v/sumQ for k, v in queryDict.items()}

    def RemoveBarrenNodes(self, query: list[BNNode], e: dict[Node | Edge | str, bool | str]) -> BayesNetwork:
        """
        Removes barren nodes from the Bayesian network.
        """
        newBN = cp.deepcopy(self)
        for node in list(nx.topological_sort(self.bn)):
            if newBN.bn.in_degree(node) == 0 and node in e and node not in query:
                newBN.bn.remove_node(node)
        for node in list(nx.topological_sort(self.bn))[::-1]:
            if node not in newBN.bn.nodes: continue # if node was already removed, continue
            if newBN.bn.out_degree(node) == 0 and node not in e and node not in query:
                newBN.bn.remove_node(node)

        return newBN
