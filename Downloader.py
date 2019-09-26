# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'downloader.ui'
#
# Created by: PyQt5 UI code generator 5.13.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, QDateTime
from PyQt5.QtWidgets import QMessageBox, QHeaderView, QAbstractItemView
import getDOHCollns
import datetime


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
        MainWindow.resize(371, 543)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 130, 351, 261))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "PID")
        self.treeWidget.headerItem().setText(1, "Children")
        # Allow selection of multiple objects
        self.treeWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.btnDownload = QtWidgets.QPushButton(self.centralwidget)
        self.btnDownload.setGeometry(QtCore.QRect(10, 430, 351, 31))
        self.btnDownload.setObjectName("btnDownload")
        # Connect download button to function
        self.btnDownload.pressed.connect(self.init_download)
        self.dtStart = QtWidgets.QDateEdit(self.centralwidget)
        self.dtStart.setGeometry(QtCore.QRect(110, 400, 71, 22))
        self.dtStart.setObjectName("dtStart")
        self.lbllFrom = QtWidgets.QLabel(self.centralwidget)
        self.lbllFrom.setGeometry(QtCore.QRect(80, 400, 31, 16))
        self.lbllFrom.setObjectName("lbllFrom")
        self.lblTo = QtWidgets.QLabel(self.centralwidget)
        self.lblTo.setGeometry(QtCore.QRect(190, 400, 21, 16))
        self.lblTo.setObjectName("lblTo")
        self.dtEnd = QtWidgets.QDateEdit(self.centralwidget)
        self.dtEnd.setGeometry(QtCore.QRect(210, 400, 71, 22))
        self.dtEnd.setObjectName("dtEnd")
        # Set end date to today
        self.dtEnd.setDate(QDate.currentDate())
        self.lblLogo = QtWidgets.QLabel(self.centralwidget)
        self.lblLogo.setGeometry(QtCore.QRect(0, 0, 121, 61))
        self.lblLogo.setText("")
        self.lblLogo.setPixmap(QtGui.QPixmap("data_files/DOH.gif"))
        self.lblLogo.setScaledContents(True)
        self.lblLogo.setWordWrap(False)
        self.lblLogo.setObjectName("lblLogo")
        self.lblTitle = QtWidgets.QLabel(self.centralwidget)
        self.lblTitle.setGeometry(QtCore.QRect(130, 20, 241, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.lblTitle.setFont(font)
        self.lblTitle.setObjectName("lblTitle")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(10, 470, 351, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(0, 60, 371, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.lblUsername = QtWidgets.QLabel(self.centralwidget)
        self.lblUsername.setGeometry(QtCore.QRect(10, 90, 71, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblUsername.setFont(font)
        self.lblUsername.setObjectName("lblUsername")
        self.lblPassword = QtWidgets.QLabel(self.centralwidget)
        self.lblPassword.setGeometry(QtCore.QRect(190, 90, 71, 16))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.lblPassword.setFont(font)
        self.lblPassword.setObjectName("lblPassword")
        self.txtUsername = QtWidgets.QLineEdit(self.centralwidget)
        self.txtUsername.setGeometry(QtCore.QRect(80, 90, 101, 20))
        self.txtUsername.setInputMask("")
        self.txtUsername.setObjectName("txtUsername")
        self.txtPassword = QtWidgets.QLineEdit(self.centralwidget)
        self.txtPassword.setGeometry(QtCore.QRect(260, 90, 101, 20))
        self.txtPassword.setInputMask("")
        self.txtPassword.setObjectName("txtPassword")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 371, 25))
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
        MainWindow.setWindowTitle(_translate("MainWindow", "Arca - MODS XML Downloader V1.0"))
        self.btnDownload.setText(_translate("MainWindow", "Download selected"))
        self.lbllFrom.setText(_translate("MainWindow", "From:"))
        self.lblTo.setText(_translate("MainWindow", "To:"))
        self.lblTitle.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" color:#0000ff;\">Arca - MODS XML Downloader</span></p></body></html>"))
        self.lblUsername.setText(_translate("MainWindow", "Username:"))
        self.lblPassword.setText(_translate("MainWindow", "Password:"))
        # Load the tree into the UI
        self.load_tree()


    def init_download(self):
        for item in self.treeWidget.selectedItems():
            print(item.text(0))

    def populate_tree_widget(self, current_widget_item, collection):
        if collection.non_collection_child is True:
            c = QtWidgets.QTreeWidgetItem(current_widget_item, [collection.pid, str(len(collection.get_children()))])
        else:
            c = current_widget_item
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

        # Populate the widget recursively
        self.populate_tree_widget(self.treeWidget, parent)
        # Set width of PID column to fit largest PID
        self.treeWidget.resizeColumnToContents(0)

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


"""
Entry point
"""
if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

