import configparser
from os import path
import sys
from PyQt5.QtWidgets import QApplication
from utils import InitBN, PlotBN
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
    app = QApplication(sys.argv)
    networkGraphApp = NetworkGraphApp(bayesNetwork)
    networkGraphApp.show()
    sys.exit(app.exec_())
    # PlotBN(bayesNetwork)
    # print(bayesNetwork.EnumerationAsk([(1,1)],{"season": "low"}))
    # print(bayesNetwork.EnumerationAskAll({(1,1): True}))
    print('done')

if __name__ == "__main__":
    Main()
