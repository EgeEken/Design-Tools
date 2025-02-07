import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Canvas import *
import resources
import time

class MainWindow(QMainWindow):

    def __init__(self, parent = None ):
        QMainWindow.__init__(self, parent )
        #print( "init mainwindow")
        self.resize(1000, 800)

        self.container = QWidget()
        self.layout = QVBoxLayout()

        self.canvas = Canvas(self)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.textEdit = QTextEdit("", self)
        self.textEdit.setReadOnly(True)
        self.textEdit.setMaximumHeight(150)

        self.layout.addWidget(self.canvas, 1)
        self.layout.addWidget(self.textEdit)

        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        bar = self.menuBar()
        fileMenu = bar.addMenu("File")
        actQuit = fileMenu.addAction(QIcon(":/icons/quit.png"), "&Quit", self.quit, QKeySequence("Esc"))
        actNew = fileMenu.addAction(QIcon(":/icons/new3.png"), "&New", self.new, QKeySequence("Ctrl+N"))
        actSave = fileMenu.addAction(QIcon(":/icons/save.png"), "&Save", self.save, QKeySequence("Ctrl+S"))

        fileToolBar = QToolBar("File")
        self.addToolBar( fileToolBar )
        fileToolBar.addAction( actQuit )
        fileToolBar.addAction( actNew )
        fileToolBar.addAction( actSave )

        colorMenu = bar.addMenu("Color")
        actPen = colorMenu.addAction(QIcon(":/icons/pen.png"), "&Pen color", self.pen_color, QKeySequence("Ctrl+P"))
        actBrush = colorMenu.addAction(QIcon(":/icons/brush.png"), "&Brush color", self.brush_color, QKeySequence("Ctrl+B"))

        colorToolBar = QToolBar("Color")
        self.addToolBar( colorToolBar )
        colorToolBar.addAction( actPen )
        colorToolBar.addAction( actBrush )

        shapeMenu = bar.addMenu("Shape")
        actRectangle = shapeMenu.addAction(QIcon(":/icons/rectangle.png"), "&Rectangle", self.rectangle)
        actEllipse = shapeMenu.addAction(QIcon(":/icons/ellipse.png"), "&Ellipse", self.ellipse)
        actFree = shapeMenu.addAction(QIcon(":/icons/free.png"), "&Free drawing", self.free_drawing)
        actEraser = shapeMenu.addAction(QIcon(":/icons/eraser.png"), "&Eraser", self.eraser)
        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setRange(0, 50)
        self.slider.setValue(10)
        self.slider.valueChanged[int].connect(self.slider_changed)
        self.slider.show()

        shapeToolBar = QToolBar("Shape")
        self.addToolBar( shapeToolBar )
        shapeToolBar.addAction( actRectangle )
        shapeToolBar.addAction( actEllipse )
        shapeToolBar.addAction( actFree )
        shapeToolBar.addAction( actEraser )
        shapeToolBar.addWidget( self.slider )

        modeMenu = bar.addMenu("Mode")
        actMove = modeMenu.addAction(QIcon(":/icons/move.png"), "&Move", self.move)
        actDraw = modeMenu.addAction(QIcon(":/icons/draw.png"), "&Draw", self.draw)
        actSelect = modeMenu.addAction(QIcon(":/icons/select.png"), "&Select", self.select)
        actLasso = modeMenu.addAction(QIcon(":/icons/lasso.png"), "&Lasso", self.lasso_select)

        modeToolBar = QToolBar("Navigation")
        self.addToolBar( modeToolBar )
        modeToolBar.addAction( actMove )
        modeToolBar.addAction( actDraw )
        modeToolBar.addAction( actSelect )
        modeToolBar.addAction( actLasso )

        editMenu = bar.addMenu("Edit")
        actCopy = editMenu.addAction(QIcon(":/icons/copy.png"), "&Copy", self.copy_selected, QKeySequence("Ctrl+C"))
        actCut = editMenu.addAction(QIcon(":/icons/cut.png"), "&Cut", self.cut_selected, QKeySequence("Ctrl+X"))
        actPaste = editMenu.addAction(QIcon(":/icons/paste.png"), "&Paste", self.paste_selected, QKeySequence("Ctrl+V"))

        editToolBar = QToolBar("Edit")
        self.addToolBar( editToolBar )
        editToolBar.addAction( actCopy )
        editToolBar.addAction( actCut )
        editToolBar.addAction( actPaste )



    ##############
    def pen_color(self):
        self.log_action("choose pen color")
        pencolor = QColorDialog.getColor()
        if pencolor.isValid():
            self.canvas.set_pencolor(pencolor)

    def brush_color(self):
        self.log_action("choose brush color")
        brushcolor = QColorDialog.getColor()
        if brushcolor.isValid():
            self.canvas.set_brushcolor(brushcolor)
        
    def rectangle(self):
        self.canvas.shape = "Rectangle"
        if self.canvas.mode != "Draw":
            self.draw()
        self.log_action("Shape mode: rectangle")

    def ellipse(self):
        self.canvas.shape = "Ellipse"
        if self.canvas.mode != "Draw":
            self.draw()
        self.log_action("Shape Mode: ellipse")

    def free_drawing(self):
        self.canvas.shape = "Free"
        if self.canvas.mode != "Draw":
            self.draw()
        self.log_action("Shape mode: free drawing")

    def eraser(self):
        self.canvas.shape = "Eraser"
        if self.canvas.mode != "Draw":
            self.draw()
        self.log_action("Shape mode: eraser")

    def slider_changed(self, value):
        self.canvas.set_brushsize(value)
        if self.canvas.mode != "Draw":
            self.draw()


    def move(self):
        self.log_action("Mode: move")
        self.canvas.mode = "Move"
        self.canvas.pos1 = None
        self.canvas.pos2 = None
        self.canvas.pos3 = None
        self.canvas.movepos = None

    def draw(self):
        self.log_action("Mode: draw")
        self.canvas.mode = "Draw"
        self.canvas.selected_objects = []
        self.canvas.pos1 = None
        self.canvas.pos2 = None
        self.canvas.pos3 = None
        self.canvas.movepos = None

    def select(self):
        self.log_action("Mode: select")
        self.canvas.mode = "Select"
        self.canvas.pos1 = None
        self.canvas.pos2 = None
        self.canvas.pos3 = None
        self.canvas.movepos = None

    
    def lasso_select(self):
        self.log_action("Mode: lasso select")
        self.canvas.mode = "Lasso"
        self.canvas.pos1 = None
        self.canvas.pos2 = None
        self.canvas.pos3 = None
        self.canvas.movepos = None
        
    
    def new(self):
        self.log_action("New")
        self.canvas.reset()
        self.textEdit.setPlainText("")

    def save(self):
        timestr = time.strftime("_%Y-%m-%d_%H-%M-%S", time.localtime()) 
        self.log_action("Saved as canvas" + timestr + ".png and log" + timestr + ".txt")
        self.canvas.grab().save("canvas" + timestr + ".png")
        content = self.textEdit.toPlainText()
        with open("log" + timestr + ".txt", "w") as f:
            f.write(content)

    def quit(self):
        self.log_action("Quit")
        self.close()

    def copy_selected(self):
        self.log_action("Copy selected")
        self.canvas.copy_selected()
        self.canvas.pos1 = None
        self.canvas.pos2 = None
        self.canvas.pos3 = None
        self.canvas.movepos = None

    def cut_selected(self):
        self.log_action("Cut selected")
        self.canvas.cut_selected()
        self.canvas.pos1 = None
        self.canvas.pos2 = None
        self.canvas.pos3 = None
        self.canvas.movepos = None

    def paste_selected(self):
        self.log_action("Paste selected")
        self.canvas.paste_selected()
        self.canvas.pos1 = None
        self.canvas.pos2 = None
        self.canvas.pos3 = None
        self.canvas.movepos = None
    

    def log_action(self, logged):
        timestr = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime()) 
        content = self.textEdit.toPlainText()
        content = content[2:]
        self.textEdit.setPlainText(" >" + timestr + " | " + logged + "\n" + content)

if __name__=="__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()
    app.exec_()
