import configparser
from os import path
from utils import InitBN, PlotBN

def Main():
    """Main function of the project
    Args:
        argc (int): System Arguments Count
        argv (list[str]): System Arguments
    """
    config = configparser.ConfigParser()
    config.read('config.ini')
    filePath = config['settings'].get('bayes_network_config_path', './tests/test0.txt')
    assert path.exists(filePath), "Path to grid configuration file does not exist!"

    bayesNetwork = InitBN(filePath)
    PlotBN(bayesNetwork)
    print(bayesNetwork.EnumerationAsk([((1, 1), (1, 0))], {}))

    print('done')

if __name__ == "__main__":
    Main()
