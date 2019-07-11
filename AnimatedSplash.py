# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 20:25:35 2019

@author: Jordan
"""

import sys, time
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import *
#from PyQt5.QtWidgets import *
import PyQt5.QtWidgets as we

class MovieSplashScreen(we.QSplashScreen):

    def __init__(self, movie, parent = None):
    
        movie.jumpToFrame(0)
        pixmap = QPixmap(movie.frameRect().size())
        
        we.QSplashScreen.__init__(self, pixmap)
        self.movie = movie
        self.movie.frameChanged.connect(self.repaint)
    
    def showEvent(self, event):
        self.movie.start()
    
    def hideEvent(self, event):
        self.movie.stop()
    
    def paintEvent(self, event):
    
        painter = QPainter(self)
        pixmap = self.movie.currentPixmap()
        self.setMask(pixmap.mask())
        painter.drawPixmap(0, 0, pixmap)
    
    def sizeHint(self):
    
        return self.movie.scaledSize()


if __name__ == "__main__":

    app = we.QApplication(sys.argv)
    movie = QMovie("PhobosLoading.gif")
    splash = MovieSplashScreen(movie)
    splash.show()
    
    start = time.time()
    
    while movie.state() == QMovie.Running and time.time() < start + 10:
        app.processEvents()
    
    window = we.QWidget()
    window.show()
    splash.finish(window)
    
    sys.exit(app.exec_())