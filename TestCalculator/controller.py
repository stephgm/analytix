import os
import sys

import h5py
import tables

import Test

import matplotlib.pyplot as plt
import numpy as np

import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
from PyQt5 import QtWidgets
from PyQt5.Qt import *
from PyQt5 import QtSql
from PyQt5.QtCore import QVariant


class MainFrame(QtWidgets.QMainWindow, Test.Ui_MainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        self.tree_model = QStandardItemModel()

        self.windowPrintBtn.clicked.connect(self.file_Open)
        # This opens a search function for user to specify the hdf5 file they want to open
        self.windowDataBtn.clicked.connect(self.retrieve_Data)
        self.tree_model.itemChanged.connect(self.chosen_Field)

        # self.windowPlotBtn.clicked.connect(self.plot_Data)
        # self.windowPlotBtn.clicked.connect(self.SubWindow)
        self.windowPlotBtn.clicked.connect(self.print_test)

        #self.tableWidget.itemSelectionChanged.connect(self.selection_view)

        ##Global Variables (Not sure if they need to be initialized here)
        self.field_count = 0  # count number of fields within given DB


    # def SubWindow(self):
    # self.plot_init = PlotWindow(self, self.header)
    # self.plot_init.exec_()

    def file_Open(self):
        self.filename = QtGui.QFileDialog.getOpenFileName(self, 'Open File (*.hdf5)', '')
        # This is the way the filename is found.  User finds the file on the system.
        self.f = h5py.File(str(self.filename), 'r+')

        self.db_list = []
        self.db_field_list = []
        self.field_keys = []
        self.db_dict = {}
        # Variables for the tree of items we will show in the listView
        # Must be cleared everytime a new file is open

        self.get_DB_List()
        # This is the next step after the file has been opened to get the DB lists

    def get_DB_List(self):
        self.f.visititems(self.file_Tree_Search)
        # Searches through the hdf5 file and keeps the node names
        # Will print out DB names into a list

        self.selected_db_name = [self.db_list]

        self.get_Field_List()

    def file_Tree_Search(self, name, node):
        if isinstance(node, h5py.Dataset):
            self.db_list.append(node.name)

    def chosen_DB(self):
        i = 0
        self.f = h5py.File(str(self.filename), 'r+')
        self.selected_db = []
        self.db_dict = {}
        self.db_field_list = []
        self.field_model.clear()
        while self.db_model.item(i):
            if self.db_model.item(i).checkState():
                print str(self.db_model.item(i)) + " is checked"
                self.selected_db.append(self.db_list[i])
            i += 1
        self.get_Field_List()

    def get_Field_List(self):
        for i in range(0, len(self.db_list)):
            try:
                self.field_keys = self.f[self.db_list[i]].dtype.fields.keys()
                self.db_field_list.append(self.field_keys)
                self.db_dict[self.db_list[i]] = self.field_keys

            except AttributeError:
                self.db_field_list.append([self.db_list[i].rsplit('/', 1)[1]])
                self.db_dict[self.db_list[i]] = ['0']
        print self.db_dict
        self.tree_View()
        self.f.close()

        # Tree view

    def tree_View(self):
        self.treeView.setModel(self.tree_model)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSortingEnabled(True)
        self.treeView.setHeaderHidden(False)
        self.treeView.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)

        self.treeView.model().setHorizontalHeaderLabels(["Databases"])

        for x in sorted(self.db_dict):
            if not self.db_dict[x]:
                continue
            parent = QtGui.QStandardItem(x)
            parent.setFlags(QtCore.Qt.NoItemFlags)
            for y in range(0, len(self.db_dict[x])):
                value = self.db_dict[x][y]
                child = QtGui.QStandardItem(str(value))
                child.setFlags(child.flags() | QtCore.Qt.ItemIsEnabled |
                               QtCore.Qt.ItemIsEditable |
                               ~ QtCore.Qt.ItemIsSelectable)
                child.setCheckState(Qt.Unchecked)
                child.setCheckable(True)
                parent.appendRow(child)
            self.treeView.model().appendRow(parent)

    def chosen_Field(self):
        root = self.tree_model.invisibleRootItem()
        self.checked_data = {}
        self.table_column = 0

        signal_count = root.rowCount()
        for i in range(signal_count):
            signal = root.child(i)
            num_children = signal.rowCount()
            checked_sweep = []
            for n in range(num_children):
                child = signal.child(n)
                if child.checkState():
                    checked_sweep.append(child.text())
                    self.table_column += 1
            self.checked_data[signal.text()] = checked_sweep
        print self.checked_data

    def retrieve_Data(self):
        self.f = h5py.File(str(self.filename), 'r+')
        self.data = {}
        self.data_name = []
        for key in self.checked_data:
            for field in self.checked_data[key]:
                new_key = str(key) + '/' + str(field)
                try:
                    self.data[new_key] = self.f[str(key)][str(field)]
                except ValueError:
                    self.data[new_key] = self.f[str(key)][:]
                self.data_name.append(new_key)

        print len(self.data[self.data_name[0]])
        print self.data
        self.f.close()
        # ADD FUNCTION FOR TABLE!
        self.create_Table()

    def create_Table(self):

        # tablemodel = MyTableModel(self.data,self)
        # tablemodel.headerData(self.selected_field)
        # self.tableView.setModel(tablemodel)


        ##self.row_count = len(self.data[self.data_name[-1]])
        ##self.column_count = len(self.data_name)
        ##self.tableWidget.setColumnCount(self.column_count)
        ##self.tableWidget.setRowCount(self.row_count)
        self.header = []
        j = 0
        for key in sorted(self.data):
            self.header.append(key)
            #for i in range(len(self.data[key])):
            #    item = QtGui.QTableWidgetItem(str(self.data[key][i]).replace("[", "").replace("]", ""))
            #    self.tableWidget.setItem(i, j, item)
            #j += 1
        ##self.tableWidget.setHorizontalHeaderLabels(self.header)
        self.tableView.show()
        self.table_model = FieldTableModel(self.data,self.header)
        self.tableView.setModel(self.table_model)

        smodel = self.tableView.selectionModel()


        #self.tableView.headerData(self.header)


    def selection_view(self):
        self.plot_cols_y = []
        print self.tableView.selectionModel().selectedColumns()
        for idx in self.tableView.selectionModel().selectedColumns():
            self.plot_cols_y.append(idx.column())
        print self.plot_cols_y

    def print_test(self):
        self.selection_view()
        self.y = []
        self.plot_label = []
        print len(self.plot_cols_y)
        print self.plot_cols_y
        for i in self.plot_cols_y:
            self.y.append(self.data[self.header[i]])
            self.plot_label.append(self.header[i])
            
        print self.y
        self.score()
        

    def mean(self, array):
        sum = 0
        for i in range(len(array)):
            sum = sum + array[i]
        return sum/len(array)
   
    def std(self, array):
        sum = 0
        mean = self.mean(array)
        for i in range(len(array)):
            sum = (array[i] - mean)**2 + sum 
        return (sum/len(array))**.5
    
    def largest(self, array1, array2):
        temp1 = 0
        temp2 = 0
        for i in range(len(array1)):
            if temp1 < array1[i]:
                temp1 = array1[i]
        for i in range(len(array2)):
            if temp2 < array2[i]:
                temp2 = array2[i]
        return temp1, temp2
    
    def score(self):
        large_x, large_y = self.largest(self.y[0],self.y[1])
        meanx = self.mean(self.y[0])
        meany = self.mean(self.y[1])
        stdx = self.std(self.y[0])
        stdy = self.std(self.y[1])
        
        x = (large_x - meanx)/stdx
        y = (large_y - meany)/stdy
        
        score = (x**2 + y**2)**.5
        
        print score
        return

class FieldTableModel(QAbstractTableModel):
    def __init__(self, datain={}, header=[], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.arraydata = datain
        self.header = header

    def rowCount(self, parent):
        return len(self.arraydata[self.header[0]])

    def columnCount(self, parent):
        return len(self.arraydata)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header[section]
            else:
                return section

    def flags(self, index):
        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable

    def data(self, index, role):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            value = self.arraydata[self.header[index.column()]][index.row()]
            return str(value)


def main():
    app = QtWidgets.QApplication(sys.argv)
    frame = MainFrame()
    frame.show()
    retval = app.exec_()
    sys.exit(retval)


if __name__ == '__main__':
    main()
