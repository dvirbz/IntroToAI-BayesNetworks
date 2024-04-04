import configparser
from os import path
import sys
from PyQt5.QtWidgets import QApplication
from utils import InitBN
from app import NetworkGraphApp

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
    print(bayesNetwork.AllSimplePathsEdges())
    print(bayesNetwork.FindNonBlockedPath((0, 1), (1, 0), {'season': 'medium'}))
    # print(bayesNetwork.EnumerationAsk([((0, 1), (1 , 1))], {'season': 'low'}), '\n\n')
    # print(bayesNetwork.EnumerationAskSet([((1, 0), (1 , 1))], {'season': 'low'}), '\n\n')
    # print(bayesNetwork.EnumerationAskSet([((0, 1), (1 , 1)), ((1, 0), (1 , 1)), ((0, 0), (0 , 1))], {'season': 'low'}), '\n\n')
    # print(bayesNetwork.EnumerationAskSet([((1, 0), (1 , 1)), ((0, 0), (1 , 0))], {'season': 'low'}), '\n\n')
    app = QApplication(sys.argv)
    networkGraphApp = NetworkGraphApp(bayesNetwork)
    networkGraphApp.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    Main()
