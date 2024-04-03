from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QComboBox, QTextEdit, QPushButton, QLabel, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas,\
    NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
import networkx as nx
from bayes_network import BayesNetwork

class NetworkGraphApp(QMainWindow):
    def __init__(self, bn: BayesNetwork):
        super().__init__()
        self.title = 'Network Graph App'
        self.left = 10
        self.top = 10
        self.width = 1440
        self.height = 810
        self.bn = bn
        self.InitUI()

    def InitUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Initialize matplotlib figure for embedding
        self.figure = plt.figure(figsize=(9, 9))
        self.canvas = FigureCanvas(self.figure)

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)

        # Navigation Toolbar
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout.addWidget(self.toolbar)  # Add the toolbar to the layout


        # Dropdown for selecting the query category (Layer)
        self.dropdown1 = QComboBox(self)
        self.dropdown1.addItem("Select Option")
        for node in self.bn.bn.nodes:
            self.dropdown1.addItem(str(node))
        self.layout.addWidget(self.dropdown1)

        # Dropdown for specific options based on the first dropdown's selection
        self.dropdown2 = QComboBox(self)
        self.dropdown2.addItem("Select Option from Dropdown 1 first")
        self.layout.addWidget(self.dropdown2)

        # Button to process Evidence
        self.evidenceButton = QPushButton('Process Evidence', self)
        self.evidenceButton.clicked.connect(self.ProcessEvidence)
        self.layout.addWidget(self.evidenceButton, 1)

        # Connect the first dropdown's selection change signal to a method
        self.dropdown1.currentIndexChanged.connect(self.UpdateDropdown2)

        # Results display area
        self.resultsDisplay = QTextEdit(self)
        self.resultsDisplay.setPlaceholderText('Results will be shown here...')
        self.resultsDisplay.setReadOnly(True)
        self.layout.addWidget(self.resultsDisplay)

        # Placeholder Button
        self.placeholder1 = QPushButton('placeholder1', self)
        # self.placeholder1.clicked.connect(self.close)
        self.layout.addWidget(self.placeholder1)

        # Placeholder Button
        self.placeholder2 = QPushButton('placeholder2', self)
        # self.placeholder2.clicked.connect(self.close)
        self.layout.addWidget(self.placeholder2)

        # Placeholder Button
        self.ClearEvidence = QPushButton('Clear Evidence', self)
        self.ClearEvidence.clicked.connect(self.bn.ClearEvidence)
        self.layout.addWidget(self.ClearEvidence)

        # Button to process Quit
        self.quitButton = QPushButton('Quit', self)
        self.quitButton.clicked.connect(self.close)
        self.layout.addWidget(self.quitButton)

        # Set the layout on the application's window
        self.mainWidget = QWidget(self)
        # self.mainWidget.setLayout(self.layout)
        self.hLayout = QHBoxLayout(self.mainWidget)

        # Text widget (QLabel) for displaying text information
        self.infoLabel = QLabel("Information goes here")
        self.infoLabel.setWordWrap(True)  # Enable word wrap if needed
        # You can set a fixed width for the label or adjust it according to your needs
        self.infoLabel.setFixedWidth(int(self.width / 2))
        
        self.placeholder1.clicked.connect(lambda: self.infoLabel.setText('\n'.join([f'{k}: {v}' for k, v in self.bn.EnumerationAskAll(self.bn.evidence).items()])))

        # Add the info label and existing vertical layout to the horizontal layout
        self.hLayout.addWidget(self.infoLabel)
        self.hLayout.addLayout(self.layout)  # self.layout is your existing QVBoxLayout

        self.setCentralWidget(self.mainWidget)

        self.PlotGraph()

    def PlotGraph(self):
        # Clear previous figure
        self.figure.clf()
        plt.subplots_adjust(bottom=0.25)  # left, bottom, width, height (range 0 to 1)

        pos = self.bn.HierarchicalLayout()

        # Draw the graph
        nx.draw(self.bn.bn, pos, with_labels=True, ax=self.figure.add_subplot(111), font_size=10, node_size=1500)

        for node in nx.topological_sort(self.bn.bn):
            varCPT = '\n'.join([f"{k}: {v[0] if isinstance(v, list) else v}" for k, v in self.bn.VarCPT(node).items()])
            plt.text(pos[node][0], pos[node][1] - 0.2, s=varCPT,\
                bbox=dict(facecolor='white', alpha=0.5), horizontalalignment='center',)

        # Refresh canvas
        self.canvas.draw()

    def ProcessEvidence(self):
        # Example process: Use selections to generate a result
        node = self.dropdown1.currentText()
        option = self.dropdown2.currentText()

        node = node if isinstance(node, str) and node.lower() == 'season' else eval(node)
        option = option.lower() if isinstance(node, str) and node.lower() == 'season' else eval(option)
        self.bn.evidence[node] = option

        # You would replace this with your actual query processing logic
        if node != "Select Layer" and option != "Select Option":
            self.resultsDisplay.setPlainText(f"Evidence is {self.bn.evidence}")
        else:
            self.resultsDisplay.setPlainText("Please select valid options.")

    def UpdateDropdown2(self):
        # Get the current text (selected item) from the first dropdown
        selectedItem = self.dropdown1.currentText()

        self.dropdown2.clear()
        self.dropdown2.addItem('Select Option')
        if selectedItem.lower() == 'season':
            self.dropdown2.addItems(['Low', 'Medium', 'High'])

        else:
            self.dropdown2.addItems(['True', 'False'])
