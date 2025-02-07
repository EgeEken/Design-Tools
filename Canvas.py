from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import random
import math


class Canvas(QWidget):

    def __init__(self, parent = None):
        super().__init__()
        #print("class Canvas")
        self.setMinimumSize(200, 200)
        self.current_gesture = []  # Initialize lasso gesture points list
        self.parent = parent

        self.painter = QPainter(self)
        self.brushcolor = Qt.red
        self.pencolor = Qt.black
        self.painter.setBrush(self.brushcolor)
        self.painter.setPen(self.pencolor)

        self.brushsize = 10

        self.selected_objects = []
        self.selected_any = False
        self.lasso_object = QPolygon()

        self.drawing = False
        self.mode = "Draw"
        
        self.shape = "Free"
        self.objects = []

        self.pos1 = None
        self.pos2 = None
        self.pos3 = None
        self.movepos = None

        self.copied_objects = []

    def paintEvent(self, event):
        self.painter.begin(self)

        for obj in self.objects:
            if obj in self.selected_objects:
                self.painter.setOpacity(0.5)
                self.painter.setPen(Qt.blue)
                self.painter.setBrush(Qt.white)
                self.painter.drawRect(obj[1].adjusted(-5, -5, 5, 5))
                self.painter.setOpacity(1)
            self.painter.setPen(obj[2])
            self.painter.setBrush(obj[3])
            if obj[0] == "Rect":
                self.painter.drawRect(obj[1])
            elif obj[0] == "Ellipse":
                self.painter.drawEllipse(obj[1])
            elif obj[0] == "Free":
                self.painter.setBrush(obj[2])
                self.painter.drawEllipse(obj[1])
            

        self.painter.setBrush(QBrush(self.brushcolor))
        self.painter.setPen(QPen(self.pencolor))

        if self.mode == "Draw":
            if self.shape == "Rectangle" and self.pos1 and self.pos2:
                self.painter.drawRect(QRect(self.pos1, self.pos2))
                if not self.drawing:
                    self.add_object(("Rect", QRect(self.pos1, self.pos3), self.pencolor, self.brushcolor))
                    self.pos1 = None
                    self.pos2 = None
                    self.pos3 = None
            elif self.shape == "Ellipse" and self.pos1 and self.pos2:
                self.painter.drawEllipse(QRect(self.pos1, self.pos2))
                if not self.drawing:
                    self.add_object(("Ellipse", QRect(self.pos1, self.pos3), self.pencolor, self.brushcolor))
                    self.pos1 = None
                    self.pos2 = None
                    self.pos3 = None
            elif self.shape == "Free" and self.pos2:
                sizetemp = QPoint(self.brushsize, self.brushsize)
                self.add_object(("Free", QRect(self.pos2 - sizetemp, self.pos2 + sizetemp), self.pencolor, self.pencolor))
                #self.add_object(("Ellipse", QRect(self.pos2, self.pos2), self.pencolor, self.pencolor))
                self.pos1 = None
                self.pos2 = None
                self.pos3 = None
            elif self.shape == "Eraser" and self.pos2:
                # Erase objects that intersect with the eraser
                sizetemp = QPoint(self.brushsize, self.brushsize)
                for obj in self.objects:
                    if obj[1].intersects(QRect(self.pos2 - sizetemp, self.pos2 + sizetemp)):
                        self.objects.remove(obj)
                self.pos1 = None
                self.pos2 = None
                self.pos3 = None
                

        if (self.mode == "Select") and self.pos1:
            self.selected_any = False

            for obj in self.objects:
                if obj[1].contains(self.pos1):
                    if not self.selected_any:
                        self.selected_any = True
                    if obj not in self.selected_objects:
                        #self.selected_objects.append(obj)
                        self.selected_objects = [obj]
            
            #if self.selected_any:
                #self.parent.log_action("Selected object: " + str(self.selected_objects))
                    


        if self.mode == "Select" and not self.selected_any and self.pos1 and len(self.selected_objects) > 0:
            self.selected_objects = []
            self.parent.log_action("Deselected")
        
            
        if self.mode == "Lasso" and self.drawing and self.current_gesture:
            if len(self.current_gesture) > 1:
                dotted_pen = QPen(Qt.black, 2, Qt.DotLine)
                self.painter.setPen(dotted_pen)
                self.painter.setBrush(Qt.NoBrush)
                self.lasso_object = QPolygonF(self.current_gesture)
                self.painter.drawPolyline(self.lasso_object)


        
        if self.mode == "Lasso" and not self.selected_any and self.pos1 and len(self.selected_objects) > 0:
            self.selected_objects = []
            self.parent.log_action("Deselected")
            

        if self.mode == "Move" and self.pos1:
            if not self.movepos:
                self.movepos = self.pos2
                #print("movepos initialized: " + str(self.movepos))

            if len(self.selected_objects) > 0:
                for obj in self.selected_objects:
                    obj[1].translate(self.pos2 - self.movepos)
                self.movepos = self.pos2
                self.update()
            else:
                for obj in self.objects:
                    obj[1].translate(self.pos2 - self.movepos)
                
                self.movepos = self.pos2
                self.update()


        self.painter.end()

    def mousePressEvent(self, event):
        self.drawing = True
        self.pos1 = event.pos()
        self.pos2 = event.pos()
        self.movepos = None

        if self.mode == "Lasso":
            self.current_gesture = [self.pos1]  # Start recording lasso points

        self.update()

    def mouseMoveEvent(self, event):
        self.pos2 = event.pos()

        if self.mode == "Lasso" and self.drawing:
            self.current_gesture.append(self.pos2)  # Add points to lasso as you move the mouse

        self.update()

    def mouseReleaseEvent(self, event):
        #print(f"mouse released at: {event.pos()}")
        self.drawing = False
        self.movepos = None
        self.pos2 = event.pos()
        self.pos3 = event.pos()
        #print(self.pos1, self.pos2, self.pos3)
        if self.mode == "Lasso":
            self.perform_lasso_selection()  # Perform selection after completing the lasso
            #print("1")
            command = self.recognize_scriboli_command()
            if command:
                #print("3")
                self.apply_scriboli_command(command)

            self.current_gesture = []
        #elif self.mode == "Move":
            # Reset after moving to allow drawing again
            #self.reset_selection_and_movement() 
            #self.mode = "Draw"
        self.update()


    def reset_selection_and_movement(self):
        self.selected_objects = []
        self.selected_any = False
        self.lasso_object = QPolygon()
        self.current_gesture = []
        self.movepos = None
        self.pos1 = None
        self.pos2 = None
        self.pos3 = None
        self.update()  # Refresh the canvas

    def perform_lasso_selection(self):
        if not self.lasso_object.isEmpty():
            self.selected_objects = []  # Clear previous selections
            self.selected_any = False

            for obj in self.objects:
                # Check if the center of the object is inside the lasso polygon
                center_point = obj[1].center()
                if self.lasso_object.containsPoint(center_point, Qt.WindingFill):
                    if obj not in self.selected_objects:
                        self.selected_objects.append(obj)
                        self.selected_any = True

    def reset(self):
        #print("reset")
        self.objects = []
        self.reset_selection_and_movement()
        self.update()

    def add_object(self, objtuple):
        #print("add object")
        self.objects.append(objtuple)
        self.update()

    def set_brushcolor(self, brushcolor):
        #print("set brush color")
        self.brushcolor = brushcolor
        self.update()

    def set_pencolor(self, pencolor):
        #print("set pen color")
        self.pencolor = pencolor
        self.update()

    def set_brushsize(self, size):
        #print("set brush size")
        self.brushsize = size
        self.update()

    def recognize_scriboli_command(self):
        #print("2")
        if len(self.current_gesture) < 2:
            #print("2.1")
            return None  # Not enough points to recognize a gesture

        line = QLineF(self.current_gesture[0], self.current_gesture[-1])
        gesture_length = line.length()
        #print("2.2")


        # Detect Zigzag Gesture (Delete)
        if self.is_zigzag_gesture(3):
            return "delete"

        # Simple threshold to differentiate between gestures
        # threshold is adjusted according to the lasso object size
        threshold = self.lasso_object.boundingRect().width() / 2

        if gesture_length > threshold:
            angle = line.angle()

            # Move Command: Horizontal Line Gesture
            #if 170 < angle < 190 or angle < 10 or angle > 350:
                #print("Detected Move Command")
            return "move" + str(int(angle))
        
        return None

    def is_zigzag_gesture(self, threshold=3):
        changes = 0
        prev_dx = None

        for i in range(1, len(self.current_gesture)):
            dx = self.current_gesture[i].x() - self.current_gesture[i - 1].x()
            if prev_dx is not None and dx * prev_dx < 0:
                changes += 1
            prev_dx = dx

        #print(f"Zigzag Direction Changes: {changes}")  # Debug output to see how many direction changes are detected
        return changes > threshold
    
    def apply_scriboli_command(self, command):
        #print("4")
        if not self.selected_objects:
            return  # No objects selected to apply commands

        if command[:4] == "move":
            angle = int(command[4:])
            movepoint = QPoint(int(math.cos(math.radians(angle)) * 10), -int(math.sin(math.radians(angle)) * 10))
            self.move_selected_objects(movepoint)

        elif command == "delete":
            self.delete_selected_objects()

        self.update()
        
    def move_selected_objects(self, offset):
        for obj in self.selected_objects:
            obj[1].translate(offset)

    def delete_selected_objects(self):
        for obj in self.selected_objects:
            if obj in self.objects:
                self.objects.remove(obj)
        self.selected_objects = []  # Clear selection after deletion


    def copy_selected(self):
        self.copied_objects = self.selected_objects

    def cut_selected(self):
        for obj in self.selected_objects:
            if obj in self.objects:
                self.objects.remove(obj)
        self.copied_objects = self.selected_objects
        self.selected_objects = []
        self.update()

    def paste_selected(self):
        if not self.copied_objects:
            return
        self.parent.move()
        self.selected_objects = []
        for obj in self.copied_objects:
            new_obj = (obj[0], obj[1].translated(20, 20), obj[2], obj[3])
            self.objects.append(new_obj)
            self.selected_objects.append(new_obj)

        self.update()