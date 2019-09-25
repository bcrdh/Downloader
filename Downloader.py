# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'downloader.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QHeaderView
import getDOHCollns

"""
UI Setup
"""
class Ui_MainWindow(object):
    def __init__(self, MainWindow):
        """
        Setup the window with appropriate elements
        Auto-generated via Qt Designer. Using the downloader.ui file.
        :param MainWindow: the main PyQt window
        """
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(372, 394)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 10, 351, 261))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "PID")
        self.treeWidget.headerItem().setText(1, "Children")
        self.btnDownload = QtWidgets.QPushButton(self.centralwidget)
        self.btnDownload.setGeometry(QtCore.QRect(10, 310, 351, 31))
        self.btnDownload.setObjectName("btnDownload")
        self.dtStart = QtWidgets.QDateEdit(self.centralwidget)
        self.dtStart.setGeometry(QtCore.QRect(110, 280, 71, 22))
        self.dtStart.setObjectName("dtStart")
        self.lbllFrom = QtWidgets.QLabel(self.centralwidget)
        self.lbllFrom.setGeometry(QtCore.QRect(80, 280, 31, 16))
        self.lbllFrom.setObjectName("lbllFrom")
        self.lblTo = QtWidgets.QLabel(self.centralwidget)
        self.lblTo.setGeometry(QtCore.QRect(190, 280, 21, 16))
        self.lblTo.setObjectName("lblTo")
        self.dateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.dateEdit.setGeometry(QtCore.QRect(210, 280, 71, 22))
        self.dateEdit.setObjectName("dateEdit")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 372, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """
        Set names for all the elements
        :param MainWindow: the main PyQt window
        :return: None
        """
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Arca - Download V1.0"))
        self.btnDownload.setText(_translate("MainWindow", "Download selected"))
        self.lbllFrom.setText(_translate("MainWindow", "From:"))
        self.lblTo.setText(_translate("MainWindow", "To:"))
        self.load_tree()

    def populate_tree_widget(self, current_widget_item, collection):
        c = QtWidgets.QTreeWidgetItem(current_widget_item, [collection.pid, str(len(collection.get_children()))])
        for child in collection.get_children():
            self.populate_tree_widget(c, child)

    def load_tree(self):
        """
        Loads the tree into the QTreeWidget
        :return: None
        """
        import os

        """
        Try to load from the data file first.
        """

        if os.path.exists('tree.dat'):
            parent = getDOHCollns.get_parent_from_file()
        else:
            Ui_MainWindow.show_info_box\
                ("tree.dat file not found. Generating repositories from Arca website. This will take a few minutes...")
            parent = getDOHCollns.get_parent()

        self.populate_tree_widget(self.treeWidget, parent)

    @staticmethod
    def show_info_box(msg):
        """
        Helper method that encapsulates the show_message function
        :param msg: the message in the information message box
        :return: None
        """
        Ui_MainWindow.show_message("Information", msg, QMessageBox.Information)

    @staticmethod
    def show_error_box(msg):
        """
        Helper method that encapsulates the show_message function
        :param msg: the message in the error message box
        :return: None
        """
        Ui_MainWindow.show_message("There's a problem...", msg, QMessageBox.Critical)

    @staticmethod
    def show_message(title, msg, box_type):
        """
        Helper method to display a message box
        :param title: the title of the message box
        :param msg: the message in the message box
        :param box_type: the type of message e.g. QMessageBox.Critical for error
        :return: None
        """
        msg_box = QMessageBox()
        msg_box.setIcon(box_type)
        msg_box.setText(msg)
        msg_box.setWindowTitle(title)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

