import sys
from PyQt5 import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vedo import Plotter, Cone, printc
from structengpy.app.viz.viz_core.model_basic import BasicViewer

class MainWindow(Qt.QMainWindow):

    def __init__(self, parent=None):
        Qt.QMainWindow.__init__(self, parent, width=800)
        self.frame = Qt.QFrame()
        self.layout = Qt.QGridLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

        path=r"C:\Users\HZJ\Desktop\ghdev\analysis"
        viewer=BasicViewer(path,'assembly',self.vtkWidget)
        self.plt=viewer.plotter
        self.id1 = self.plt.addCallback("mouse", self.onMouseClick)
        self.id2 = self.plt.addCallback("key press",   self.onKeypress)
        viewer.show()               # <--- show the vedo rendering

        # Set-up the rest of the Qt window
        btnBasicViz = Qt.QPushButton("模型")
        btnBasicViz.setToolTip('基本模型')
        btnBasicViz.clicked.connect(self.onClick)

        btnLoadViz = Qt.QPushButton("荷载")
        btnLoadViz.clicked.connect(self.onClick)

        btnDispViz = Qt.QPushButton("位移")
        btnDispViz.clicked.connect(self.onClick)

        btnForceViz = Qt.QPushButton("内力")
        btnForceViz.clicked.connect(self.onClick)

        self.layout.addWidget(self.vtkWidget,0,0,1,4)
        self.layout.addWidget(btnBasicViz,1,0,1,1)
        self.layout.addWidget(btnLoadViz,1,1,1,1)
        self.layout.addWidget(btnDispViz,1,2,1,1)
        self.layout.addWidget(btnForceViz,1,3,1,1)
        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)
        self.show()                     # <--- show the Qt Window

    def onMouseClick(self, evt):
        printc("You have clicked your mouse button. Event info:\n", evt, c='y')

    def onKeypress(self, evt):
        printc("You have pressed key:", evt.keyPressed, c='b')

    @Qt.pyqtSlot()
    def onClick(self):
        printc("..calling onClick")
        self.plt.actors[0].color('red').rotateZ(40)
        self.plt.interactor.Render()

    def onClose(self):
        #Disable the interactor before closing to prevent it
        #from trying to act on already deleted items
        printc("..calling onClose")
        self.vtkWidget.close()

if __name__ == "__main__":
    app = Qt.QApplication(sys.argv)
    window = MainWindow()
    app.aboutToQuit.connect(window.onClose) # <-- connect the onClose event
    app.exec_()