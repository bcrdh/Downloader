from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, QRunnable, QObject, pyqtSignal, pyqtSlot, QThreadPool, QMutex, QTimer
from PyQt5.QtWidgets import QMessageBox, QAbstractItemView
from robobrowser import RoboBrowser
import getDOHCollns
import os
import re
from datetime import datetime

"""
Thread pool for all the threads
"""
threadpool = QThreadPool()
threadpool.setMaxThreadCount(50)

"""
The session that will be used by
all browser instances to access the
collections. Set in sign_in()
"""
global_session = None

"""
Regex to get individual collection objects that end
in numbers
"""
num_str = r'/islandora/object/\D*?%3A\d*?$'  # [a-z]+%3A[0-9]+

"""
Track how many MODS XML it is possible to download.
This value changes based on how many collections the
user selects.
"""
downloadable = 0

"""
Authentication
"""


def sign_in(username, password):
    """
    Signs into the DOH website and sets the global session
    to allow other browser instances to access the cookies
    :param username: the username to login with
    :param password: the password to login with
    """
    # If already logged in, don't log in again
    global global_session
    if global_session is not None:
        return True
    # Create Non-JS browser
    browser = RoboBrowser(parser='html.parser')
    # Open login page
    browser.open('https://doh.arcabc.ca/user/login')
    # Get the login form
    form = browser.get_form(id='user-login')
    # Set the username & password
    form['name'].value = username
    form['pass'].value = password
    # Submit the form
    browser.submit_form(form)
    # If successfully signed in
    h1 = browser.find(class_='page__title')
    if h1.text == username:
        # Set the global session
        global_session = browser.session
        return True
    else:
        return False


"""
Scraping / Downloading
"""


def scrape(pid, url, start_date, end_date):
    """
    Scrapes the MODS XML urls for collection objects
    :param url: the url to scrape from
    :param start_date: the starting date constraint for MODS XML files
    :param end_date: the ending date constraint for MODS XML files
    :return: the list of all the MODS XML urls
    """
    result = []

    try:
        browser = RoboBrowser(session=global_session, parser='html.parser')
        # Go to each mods xml page and scrape all the
        # valid mods xml files in the date range
        browser.open(url)
        # Get all MODS XML file links
        file_links = browser.find_all \
            ("a",
             href=re.compile(r'/islandora/object/' + pid.replace(':', '%3A') + '/datastream/MODS/version/\d+/view'))
        # Filter based on date
        for file_link in file_links:
            date = datetime.strptime(file_link.text, '%A, %d-%b-%y %H:%M:%S Z')
            # Remove the time segment since the user
            # does not enter a time (i.e. convert from datetime to date)
            date = date.date()
            # If the file is in range...
            if start_date <= date <= end_date:
                result.append(
                    (pid, 'https://doh.arcabc.ca' + file_link['href'], date.strftime('%m%d%y'))
                )
    except Exception as e:
        print('Line 109: ' + e)
        return []

    return result


def download(url, path, filename):
    """
    Downloads the MODS XML file and saves it
    :param url: the url to download from
    :param path: the path to save the MODS XML file
    :param filename: the name of the file to save the MODS XML file
    :return: tuple with a boolean and path indicating if it was successful
    """
    file_path = path + filename
    try:
        # Create directory if it does not exist
        if not os.path.exists(path):
            os.mkdir(path)
    except Exception as e:
        print('Line 129 ' + e)
        pass

    try:
        if os.path.exists(file_path):
            os.remove(file_path)

        # Create new browser instance
        browser = RoboBrowser(session=global_session, parser='html.parser')
        # Open the MODS XML file and save it
        request = browser.session.get(url, stream=True)
        with open(file_path, 'wb') as file:
            file.write(request.content)

        return True, file_path
    except Exception as e:
        print('Line 145: ' + e)
        return False, file_path


"""
Multithreading
"""


class WorkerSignals(QObject):
    """
    The possible return types from a Worker object
    """
    download_complete = pyqtSignal(tuple)
    scrape_complete = pyqtSignal(tuple)


class DownloaderWorker(QRunnable):
    """
    Worker class that downloads the MODS XML file and returns
    success
    """

    def __init__(self, fn, *args, **kwargs):
        super(DownloaderWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        url, path, filename = self.args
        result = self.fn(url, path, filename)
        self.signals.download_complete.emit(result)


class ScraperWorker(QRunnable):
    """
    Worker class that scrapes the downloadable MODS XML files from
    a repository. It submits these MODS XML files to the DownloaderWorker
    class to download the mods XML file.
    """

    def __init__(self, fn, *args, **kwargs):
        super(ScraperWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        pid, path, start_date, end_date = self.args
        result = self.fn(pid,
                         'https://doh.arcabc.ca/islandora/object/' + pid.replace(":", "%3A") +
                         '/datastream/MODS/version',
                         start_date,
                         end_date)
        # Sends scraped results to UI so it can
        # start the downloader
        self.signals.scrape_complete.emit((path, result))


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
        MainWindow.resize(371, 500)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(10, 130, 351, 261))
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "PID")
        self.treeWidget.headerItem().setText(1, "Children")
        self.treeWidget.headerItem().setText(2, "Title")
        # Allow selection of multiple objects
        self.treeWidget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.btnDownload = QtWidgets.QPushButton(self.centralwidget)
        self.btnDownload.setGeometry(QtCore.QRect(10, 430, 351, 31))
        self.btnDownload.setObjectName("btnDownload")
        # Connect download button to function
        self.btnDownload.pressed.connect(self.init_download)
        self.dtStart = QtWidgets.QDateEdit(self.centralwidget)
        self.dtStart.setGeometry(QtCore.QRect(40, 400, 71, 22))
        self.dtStart.setObjectName("dtStart")
        self.lbllFrom = QtWidgets.QLabel(self.centralwidget)
        self.lbllFrom.setGeometry(QtCore.QRect(10, 400, 31, 16))
        self.lbllFrom.setObjectName("lbllFrom")
        self.lblTo = QtWidgets.QLabel(self.centralwidget)
        self.lblTo.setGeometry(QtCore.QRect(120, 400, 21, 16))
        self.lblTo.setObjectName("lblTo")
        self.dtEnd = QtWidgets.QDateEdit(self.centralwidget)
        self.dtEnd.setGeometry(QtCore.QRect(140, 400, 71, 22))
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
        # Set password
        self.txtPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        # Check box
        self.chkBoxLatest = QtWidgets.QCheckBox(self.centralwidget)
        self.chkBoxLatest.setGeometry(QtCore.QRect(240, 400, 101, 17))
        self.chkBoxLatest.setObjectName("chkBoxLatest")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 371, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslate_ui(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # Multithreading safety
        self.threadpool_lock = QMutex()

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)

        self.time_elapsed_zero = 0

    def tick(self):
        """
        Called every time the timer ticks during a download
        :return: None
        """
        if threadpool.activeThreadCount() is 0:
            self.time_elapsed_zero = self.time_elapsed_zero + 1
        else:
            self.time_elapsed_zero = 0

        if self.time_elapsed_zero is 30:
            self.show_info_box('Finished downloading!')
            self.btnDownload.setDisabled(False)
            self.timer.stop()

    def download_scraped_links(self, result):
        """
        Called by Scraper threads. Will create Downloader threads to start
        MODS XML downloading process
        :param result: the result from the scraper thread emitted as a signal
        :return: None
        """
        path, mods = result
        # Failed to scrape MODS
        if mods is None or len(mods) is 0:
            self.show_error_box('Failed to scrape (& download) ' + path)
            return

        # Start downloading in multiple threads
        for (pid, url, date) in mods:
            # Path format e.g.: arms_1234_092919_MODS.xml, 092919 = 09/29/2019
            worker = DownloaderWorker(download,
                                      url,
                                      path,
                                      os.sep + pid.replace(':', '_') + '_' + date + '_MODS.xml')

            worker.signals.download_complete.connect(self.download_complete)

            self.threadpool_lock.lock()
            threadpool.start(worker)
            self.threadpool_lock.unlock()

    def download_complete(self, result):
        success, path = result

        if not success:
            self.show_error_box('Failed to download ' + path)

    def create_dirs_and_download(self, root, path):
        """
        Creates directories for each collection object in which MODS XML will be stored.
        :param root: the root of the collection being downloaded, also the children (recursively set)
        :param path: the path at which the folder is for this collection
        :return: None
        """
        global downloadable
        # Make the path if it does not exist.
        if not os.path.exists(path):
            os.mkdir(path)

        # Scrape this URL and download valid MODS XML files
        if root.childCount() is 0:
            downloadable = downloadable+1
            worker = ScraperWorker(scrape,
                                   root.text(0),
                                   path,
                                   self.dtStart.date().toPyDate(),
                                   self.dtEnd.date().toPyDate())

            worker.signals.scrape_complete.connect(self.download_scraped_links)

            threadpool.start(worker)

        # Recursively call this for the children
        for x in range(root.childCount()):
            child = root.child(x)
            self.create_dirs_and_download(child, path + os.sep + child.text(0).replace(":", "_"))

    def init_download(self):
        """
        Performs checks before starting download and displays content to download
        :return: None
        """
        if len(self.treeWidget.selectedItems()) is 0:
            self.show_error_box('You must make a selection before downloading!')
        elif len(self.txtUsername.text().strip()) is 0:
            self.show_error_box("You must enter a username!")
        elif len(self.txtPassword.text().strip()) is 0:
            self.show_error_box("You must enter a password!")
        elif not self.dtStart.date() <= self.dtEnd.date():
            self.show_error_box('The start date must be smaller than or equal to the end date!')
        elif not sign_in(self.txtUsername.text(), self.txtPassword.text()):
            self.show_error_box('Ensure your username and password are correct!')
        else:
            # Display message to user
            msg = ['You will download MODS XML files for the selected PIDs and all of its children:\n\n']
            for item in self.treeWidget.selectedItems():
                msg.append('- ')
                msg.append(item.text(0))
                msg.append('\n')

            self.show_info_box(''.join(msg))
            # Disable download button until download is complete
            self.btnDownload.setDisabled(True)
            # Create all the directories to save files
            for item in self.treeWidget.selectedItems():
                self.create_dirs_and_download(item, item.text(0).replace(":", "_"))

            # Start timer
            self.timer.start(1000)

    def populate_tree_widget(self, current_widget_item, collection):
        """
        Recursively populates the tree widget with all the collections
        :param current_widget_item: Initially the root, then each child (recursively set)
        :param collection: the Arca collection object
        :return: None
        """
        if collection.non_collection_child is True:
            c = QtWidgets.QTreeWidgetItem(
                current_widget_item, [collection.pid, str(len(collection.get_children())), collection.title])
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
            import time
            self.start_time = time.time()
            Ui_MainWindow.show_info_box \
                ("tree.dat file not found. Generating repositories from Arca website. This will take a few minutes...")
            parent = getDOHCollns.get_parent()
            print(time.time() - self.start_time)

        # Populate the widget recursively
        self.populate_tree_widget(self.treeWidget, parent)
        # Set width of the PID column to resize to content
        self.treeWidget.resizeColumnToContents(0)
        self.treeWidget.resizeColumnToContents(2)

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

    def retranslate_ui(self, MainWindow):
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
        self.lblTitle.setText(_translate("MainWindow",
                                         "<html><head/><body><p><span style=\" color:#0000ff;\">Arca - MODS XML Downloader</span></p></body></html>"))
        self.lblUsername.setText(_translate("MainWindow", "Username:"))
        self.lblPassword.setText(_translate("MainWindow", "Password:"))
        self.chkBoxLatest.setText(_translate("MainWindow", "Download latest"))
        # Load the tree into the UI
        self.load_tree()


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
