import sys
from pomodoro import MainWindow, makeIcon
from pomodoro import makeIcon
from PyQt5.QtWidgets import QApplication
from qdarkstyle import load_stylesheet

def makeApp():
    try:
        from PyQt5.QtWinExtras import QtWin
        QtWin.setCurrentProcessExplicitAppUserModelID(APP_ID)
    except:
        pass
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(makeIcon("tomato"))
    app.setApplicationName("Pomodoro")
    app.setOrganizationName("Burak Martin")
    app.setOrganizationDomain("https://github.com/burakmartin")
    return app

def main():
    app = makeApp()
    app.setStyleSheet(load_stylesheet(qt_api="pyqt5"))
    mainWindow = MainWindow()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()