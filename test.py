# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import (QGraphicsItem,
    QGraphicsView, QGraphicsScene, QGraphicsRectItem, QDialog, QHBoxLayout,
    QApplication, QGraphicsTextItem)
from PyQt5.QtCore import QPointF, Qt
from PyQt5.QtGui import QColor
import sys
class MyRect(QGraphicsRectItem):

    def __init__(self, parent = None):
        super(MyRect, self).__init__(parent)

        self.text_item  = QGraphicsTextItem('My Text Here', self)
        self.value_item = QGraphicsTextItem('My Value Here', self)
        self.text_item.setDefaultTextColor(QColor(Qt.blue))
        self.value_item.setDefaultTextColor(QColor(Qt.red))

        self.value_item.setPos(self.text_item.boundingRect().bottomLeft())

        width  = max(self.text_item.boundingRect().width(), self.value_item.boundingRect().width())
        height = self.text_item.boundingRect().height() + self.value_item.boundingRect().height()
        self.setRect(50, 50, width, height)


class MainFrame(QDialog):

    def __init__(self, parent = None):
        super(MainFrame, self).__init__(parent)

        ### setting up the scene
        self.view = QGraphicsView()
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)
        self.scene.setSceneRect(0, 0, 500, 500)

        ### setting up MyRect
        my_rect = MyRect()

        self.scene.addItem(my_rect)

        layout = QHBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)

        self.setWindowTitle("Basic test")
def main():                      
    app = QApplication(sys.argv)
    ex = MainFrame()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()