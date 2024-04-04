from __future__ import annotations
import copy as cp
import networkx as nx
from type_aliases import Node, Edge, BNNode

ROUND_DIGITS = 5

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

    def __init__(self, season: dict[str, list[float]], fragEdgesCPT: dict[Edge, float], nodesCPT: dict[Node, float], x: int, y: int):
        self._season = season
        self._fragEdgesCPT = fragEdgesCPT
        self._nodesCPT = nodesCPT
        self._bn: nx.DiGraph = nx.DiGraph()
        self._grid: nx.Graph = nx.grid_2d_graph(x + 1, y + 1)
        nodes = list(nodesCPT.keys())
        fragEdges = list(fragEdgesCPT.keys())
        self._bn.add_nodes_from({"season"})
        self._bn.add_nodes_from(fragEdges)
        self._bn.add_nodes_from(nodes)
        self._bn.add_edges_from([("season", node) for node in nodes])
        self._bn.add_edges_from([(node, edge) for node in nodes for edge in fragEdges if node in edge])
        self._evidence: dict[BNNode, bool | str] = {}

    @property
    def bn(self) -> nx.DiGraph:
        """
        Returns the Bayesian network associated with this object.
        
        Returns:
            nx.DiGraph: The Bayesian network.
        """
        return self._bn

    @property
    def grid(self) -> nx.Graph:
        """
        Returns the Full Grid associated with this object.
        
        Returns:
            nx.Graph: The Grid.
        """
        return self._grid
    
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

    @property
    def evidence(self) -> dict[BNNode, bool | str]:
        """
        Returns the evidence dictionary containing the observed values for each node in the Bayesian network.

        Returns:
            dict[BNNode, bool | str]: The evidence dictionary where the keys are the nodes in the network and the values
            are the observed values for each node.
        """
        return self._evidence

    def ClearEvidence(self) -> None:
        """
        Clears all the evidence in the Bayesian network.

        This method sets the evidence dictionary to an empty dictionary,
        effectively removing all the evidence that has been previously set.
        """
        self._evidence = {}

    def HierarchicalLayout(self, width=2, vertGap=0.3) -> dict[BNNode, tuple[float, float]]:
        """
        Calculates the positions of nodes in a hierarchical layout for a Bayesian network.

        Parameters:
        - width (float): The horizontal spacing between nodes in the second layer. Default is 2.
        - vertGap (float): The vertical spacing between layers. Default is 0.3.

        Returns:
        - pos (dict): A dictionary containing the positions of nodes in the layout.
            The keys are node names and the values are (x, y) coordinates.
        """

        pos = {}
        pos['season'] = (0, 0)  # Place root at the top

        # Calculate horizontal positions for the second layer
        secondLayerNodes = list(self.bn.successors('season'))
        for i, node in enumerate(secondLayerNodes):
            pos[node] = (-width/2 + i * (width / (len(secondLayerNodes) - 1)), -vertGap)

        # Calculate positions for the third layer based on their connections
        # for node in secondLayerNodes:
        #     successors = list(self.bn.successors(node))
        #     for i, succ in enumerate(successors):
        i = 0
        for node in self.bn.nodes:
            if node in ['season'] + secondLayerNodes: continue
            pos[node] = (-width/2 + i * (width / (len(self.bn.nodes) - len(secondLayerNodes) - 2)), -2 * vertGap)
            i += 1

        return pos
    def AllSimplePathsEdges(self) -> list[list[Edge]]:
        """
        Finds all simple paths between all nodes in the Bayes Network.

        Returns:
            list[list[Edge]]: A list of lists of nodes representing the paths between all nodes.

        """
        allPathsNodes = sum([self.AllSimplePathsStartToEndEdges(start, end) for start in self.grid.nodes for end in self.grid.nodes if start != end], [])
        return allPathsNodes
    
    def AllSimplePathsStartToEndEdges(self, start: Node, end: Node) -> list[list[Edge]]:
        """
        Finds all simple paths between two nodes in the Bayes Network.

        Args:
            start (Node): The starting node of the path.
            end (Node): The ending node of the path.

        Returns:
            list[list[Node]]: A list of lists of nodes representing the paths from start to end.

        """
        allPathsNodes = list(nx.all_simple_paths(self.grid, start, end))
        allPathEdges = [[(allPathsNodes[i][j], allPathsNodes[i][j + 1]) for j in range(len(allPathsNodes[i]) - 1)] for i in range(len(allPathsNodes))]
        return allPathEdges

    def FindNonBlockedPath(self, start: Node, end: Node, e: dict[BNNode, bool | str]) -> list[Node]:
        """
        Finds a non-blocked path between two nodes in the Bayes Network.

        Args:
            start (Node): The starting node of the path.
            end (Node): The ending node of the path.
            e (dict[BNNode, bool | str]): Evidence dictionary containing the values of nodes.

        Returns:
            list[Node]: A list of nodes representing the non-blocked path from start to end.

        """
        # allPathsNodes = list(nx.all_simple_paths(self.grid, start, end))
        # allPathEdges = [[(allPathsNodes[i][j], allPathsNodes[i][j + 1]) for j in range(len(allPathsNodes[i]) - 1)] for i in range(len(allPathsNodes))]
        allPathEdges = self.AllSimplePathsStartToEndEdges(start, end)
        print(f'{allPathEdges=}')
        highProb = (0, [])
        for path in allPathEdges:
            currPathProb = (self.EnumerationAskSet(path, e | {}), path)
            print(f'{currPathProb=}')
            highProb = max(highProb, currPathProb)
        return highProb

    def EnumerationAskSet(self, querySet: list[BNNode], e: dict[BNNode, bool | str]) -> float:
        """
        Performs enumeration-based inference for all queries in the Bayesian network.

        Args:
            e (dict): Evidence dictionary containing observed values for nodes or edges in the network.

        Returns:
            dict: A dictionary containing the probabilities of all queries in the network.
                  The keys are the queries (nodes or edges) and the values are dictionaries
                  representing the probability distribution for each query.
        """
        if len(querySet) == 0: return 1.0
        p = self.EnumerationAsk([querySet[0]], e | {})
        pFalse = p[False]
        # print(f'{querySet=}, {e=}, {p=}, {pFalse=}', '\n')
        return round(pFalse * self.EnumerationAskSet(querySet[1:], e | {querySet[0]: False}), ROUND_DIGITS)

    def EnumerationAskAll(self, e: dict[BNNode, bool | str]) -> dict[BNNode, dict[bool | str , float]]:
        """
        Performs enumeration-based inference for all queries in the Bayesian network.

        Args:
            e (dict): Evidence dictionary containing observed values for nodes or edges in the network.

        Returns:
            dict: A dictionary containing the probabilities of all queries in the network.
                  The keys are the queries (nodes or edges) and the values are dictionaries
                  representing the probability distribution for each query.
        """
        queries = list(nx.topological_sort(self.bn))
        probabilityDict = {q: cp.deepcopy(self).EnumerationAsk([q], cp.copy(e)) for q in queries}
        return probabilityDict

    def EnumerationAsk(self, query: BNNode, e: dict[BNNode, str | bool]) -> dict[str, float]:
        """
        Performs inference using the enumeration-ask algorithm.

        Args:
        - query: The variable to query.
        - e: The evidence for inference.

        Returns:
        A dictionary containing the probabilities of the query variable.
        """
        # from utils import PlotBN
        queryDict = {}
        # PlotBN(self)
        query = [tuple(sorted(q)) if isinstance(q, tuple) and q and isinstance(q[0], tuple) else q for q in query][0]
        if query not in self.bn.nodes: return {True: 0.0, False: 1.0}
        options = ['low', 'medium', 'high'] if isinstance(query, str) else [True, False]
        if query in e:
            otherOptions = options[::]
            otherOptions.remove(e[query])
            return {e[query]: 1.0} | {other: 0.0 for other in otherOptions}
        for q in options:
            e[query] = q
            barrenBN = self.RemoveBarrenNodes(query, e | {})
            # PlotBN(barrenBN)
            nodes = list(nx.topological_sort(barrenBN.bn))
            # print(f'{query=}, {nodes=}, {e=}', '\n\n')
            queryDict[q] = barrenBN.EnumerationAll(nodes, e | {})
        return self.Normalize(queryDict)

    def EnumerationAll(self, nodes: list[Node], e: dict[BNNode, bool | str]) -> float:
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
            p = self.Probability(y, e, e[y])
            r = self.EnumerationAll(nodes[1:], e)
            return p * r
        p = [self.Probability(y, e, option) for option in options]
        r = [self.EnumerationAll(nodes[1:], e | {y : option}) for option in options]
        return np.inner(p, r)

    def Probability(self, y: BNNode, e: dict[BNNode, bool | str], option: str | bool) -> float:
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

    def Parent(self, node: BNNode, e: dict[BNNode, bool | str]):
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
        # print(f'{queryDict=}, {sumQ=}', '\n\n')
        if sumQ == 0: return queryDict
        return {k: round(v/sumQ, ROUND_DIGITS) for k, v in queryDict.items()}

    def RemoveBarrenNodes(self, query: list[BNNode], e: dict[Node | Edge | str, bool | str]) -> BayesNetwork:
        """
        Removes barren nodes from the Bayesian network.
        """
        if not isinstance(query, list): query = [query] # convert query to list if it is not
        newBN = cp.deepcopy(self)
        nodes = list(nx.topological_sort(self.bn))
        # print(f'{query=}, {nodes=}, {e=}')
        for node in nodes:
            if newBN.bn.in_degree(node) == 0 and node in e and node not in query:
                # print(f'{node=}, {newBN.bn.in_degree(node)=}')
                newBN.bn.remove_node(node)
        for node in nodes[::-1]:
            if node not in newBN.bn.nodes: continue # if node was already removed, continue
            if newBN.bn.out_degree(node) == 0 and node not in e and node not in query:
                # print(f'{node=}, {newBN.bn.out_degree(node)=}')
                newBN.bn.remove_node(node)
        return newBN
