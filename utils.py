from typing import Tuple
from bayes_network import BayesNetwork
ROUND_DIGITS = 5

def CPTVertex(p) -> dict[str, float]:
    """
    Calculates the Conditional Probability Table (CPT) for a vertex.

    Parameters:
    p (float): The probability value for the 'low' state.

    Returns:
    dict[str, float]: A dictionary representing the CPT with 
    'low', 'medium', and 'high' states and their corresponding probabilities.
    """
    return {'low' : round(p, ROUND_DIGITS) , 'medium' : round(min(1, p * 2), ROUND_DIGITS), 'high' : round(min(1, p * 3), ROUND_DIGITS)}

def CPTEdge(qi, leakage) -> dict[Tuple[bool, bool], float]:
    """
    Computes the Conditional Probability Table (CPT) for an edge in a Bayesian network.

    Parameters:
    - qi (float): The probability of the edge being blocked given excatly one of its parents is true.
    - leakage (float): The probability of the edge being blocked when both its parents are false.

    Returns:
    - cpt (dict[Tuple[bool, bool], float]): The CPT for the edge,
      represented as a dictionary of tuples (parent values) to probabilities.
    """
    return {(False, False): leakage,
            (True, False): round(1 - qi,ROUND_DIGITS),
            (False, True): round(1 - qi, ROUND_DIGITS),
            (True, True): round(1 - qi ** 2, ROUND_DIGITS)}

def InitBN(initFilePath: str) -> BayesNetwork:
    """
    Initializes a Bayes Network based on the information provided in the given file.

    Args:
        initFilePath (str): The path to the file containing the initialization information.

    Returns:
        BayesNetwork: The initialized Bayes Network.

    Raises:
        FileNotFoundError: If the specified file does not exist.

    """
    with open(initFilePath, 'r') as f:
        # find all lines starting with '#' and cut them off on ';'
        lines = list(line.split(';')[0].split('#')[1].strip().split(' ')
                     for line in f.readlines() if line.startswith("#"))  # seperate the line to a list of words/tokens.
        lines = list(list(filter(lambda e: e!='', line)) for line in lines) # filter empty words/tokens

    leakage = list(float(line[1]) for line in lines if line[0].lower() == 'l')[0] # extract y max value from file
    season = [{"low" : [float(line[1])],
              "medium": [float(line[2])],
              "high": [float(line[3])]} for line in lines if line[0].lower() == 's'][0] # extract season values from file

    nodesCPT, fragEdgesCPT = {}, {}
    for line in lines:
        action = line[0]
        if action == 'V':
            nodesCPT[(int(line[1]), int(line[2]))] = CPTVertex(float(line[3]))
        if action == 'F':
            fragEdgesCPT[((int(line[1]), int(line[2])),
                          (int(line[3]), int(line[4])))] = CPTEdge(1 - float(line[5]), leakage)
    print("season: ", season)
    print("nodesCPT: ", nodesCPT)
    print("fragEdgesCPT: ", fragEdgesCPT)

    return BayesNetwork(season, fragEdgesCPT, nodesCPT)
