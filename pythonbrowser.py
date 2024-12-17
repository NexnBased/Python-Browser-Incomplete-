import os, sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *

class AboutDialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(AboutDialog, self).__init__(*args, **kwargs)

        QBtn = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)

        layout = QVBoxLayout()

        title = QLabel("Xeon Web Browser")
        font = title.font()
        font.setPointSize(20)
        title.setFont(font)

        layout.addWidget(title)

        logo = QLabel()
        logo.setPixmap(QPixmap(os.path.join('icons', 'ma-icon-128.png')))
        layout.addWidget(logo)

        layout.addWidget(QLabel("V1"))
        layout.addWidget(QLabel("Copyright Nexn"))

        for i in range(layout.count()):
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

class BookmarkManager:
    def __init__(self):
        self.bookmarks = []

    def add_bookmark(self, url, title):
        self.bookmarks.append({"title": title, "url": url})

    def get_bookmarks(self):
        return self.bookmarks

class HistoryManager:
    def __init__(self):
        self.history = []

    def add_to_history(self, url, title):
        self.history.append({"title": title, "url": url})

    def get_history(self):
        return self.history

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.bookmark_manager = BookmarkManager()
        self.history_manager = HistoryManager()
        self.homepage = "https://start.duckduckgo.com"

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        self.addToolBar(navtb)

        back_btn = QAction(QIcon(os.path.join('icons', 'arrow-180.png')), "Back", self)
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        navtb.addAction(back_btn)

        next_btn = QAction(QIcon(os.path.join('icons', 'arrow-000.png')), "Forward", self)
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        navtb.addAction(next_btn)

        reload_btn = QAction(QIcon(os.path.join('icons', 'arrow-circle-315.png')), "Reload", self)
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        navtb.addAction(reload_btn)

        home_btn = QAction(QIcon(os.path.join('icons', 'home.png')), "Home", self)
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        bookmark_btn = QAction(QIcon(os.path.join('icons', 'star.png')), "Add Bookmark", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        navtb.addAction(bookmark_btn)

        history_btn = QAction(QIcon(os.path.join('icons', 'history.png')), "Show History", self)
        history_btn.triggered.connect(self.show_history)
        navtb.addAction(history_btn)

        self.urlbar = QLineEdit()
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        navtb.addWidget(self.urlbar)

        stop_btn = QAction(QIcon(os.path.join('icons', 'cross-circle.png')), "Stop", self)
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        navtb.addAction(stop_btn)

        settings_menu = self.menuBar().addMenu("&Settings")
        set_homepage_action = QAction("Set Homepage", self)
        set_homepage_action.triggered.connect(self.set_homepage)
        settings_menu.addAction(set_homepage_action)

        self.add_new_tab(QUrl(self.homepage), "Homepage")
        self.show()
        self.setWindowTitle("Xeon Web Browser")

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl('')

        browser = QWebEngineView()
        browser.setUrl(qurl)
        browser.urlChanged.connect(lambda q, browser=browser: self.update_urlbar(q, browser))
        browser.loadFinished.connect(lambda _, browser=browser: self.update_title(browser))
        browser.loadFinished.connect(lambda: self.history_manager.add_to_history(
            browser.url().toString(), browser.page().title()))

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = browser.page().title()
        self.setWindowTitle(f"{title} - Xeon Web Browser")

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(self.homepage))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def update_urlbar(self, q, browser=None):
        if browser != self.tabs.currentWidget():
            return
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)

    def set_homepage(self):
        new_homepage, ok = QInputDialog.getText(self, "Set Homepage", "Enter URL:")
        if ok and new_homepage:
            self.homepage = new_homepage

    def add_bookmark(self):
        current_url = self.tabs.currentWidget().url().toString()
        current_title = self.tabs.currentWidget().page().title()
        self.bookmark_manager.add_bookmark(current_url, current_title)
        QMessageBox.information(self, "Bookmark Added", f"Added: {current_title}")

    def show_history(self):
        history_list = self.history_manager.get_history()
        history_dialog = QDialog(self)
        history_dialog.setWindowTitle("Browsing History")
        layout = QVBoxLayout(history_dialog)

        for item in history_list:
            layout.addWidget(QLabel(f"{item['title']} - {item['url']}"))

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(history_dialog.close)
        layout.addWidget(close_btn)

        history_dialog.setLayout(layout)
        history_dialog.exec_()


app = QApplication(sys.argv)
app.setApplicationName("Xeon Web Browser")
window = MainWindow()
app.exec_()
