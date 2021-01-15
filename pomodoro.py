from PyQt5.QtCore import QTime, QTimer
from PyQt5.QtWidgets import QSizePolicy, QWidget, QMainWindow, QVBoxLayout, QGroupBox, QHBoxLayout, QSpinBox, QLabel, QComboBox, QLCDNumber, QPushButton, QSystemTrayIcon, QMenu, QApplication
from PyQt5.QtGui import QIcon

from enum import Enum
from random import choice

APP_ID = 'brkmrt.pomodoro'
work_finished_phrases = ["Its time to rest, but don't 😴...", "Take a rest and grab some 💧", "Rest a bit, you deserve it!🤓", "Okay...I Guess you can take a rest now...🙄"]
rest_finished_phrases = ["Enough rest, go back to work 💻", "Get back to work. You've got this! 😤", "Its time to work. You can do it!🧠", "You got this, get back to work 📚"]
pomodoro_finished_phrases = ["Good job, im proud of you!😊"]

class Mode(Enum):
    work = 1,
    rest = 2

class Status(Enum):
    workFinished = 1,
    restFinished = 2,
    repetitionsReached = 3

class MainWindow(QMainWindow):


    def __init__(self):
        super(MainWindow, self).__init__()
        self.setup_trayicon()
        self.setup_ui()
        self.setup_connections()
        self.time = QTime(0,0,0,0)
        self.workEndTime = QTime(0,25,0,0)
        self.restEndTime = QTime(0,5,0,0)
        self.currentMode = Mode.work
        self.maxRepetitions = -1
        self.currentRepetitions = 0
        self.show()


    def reset_time(self):
        self.time = QTime(0,0,0,0)
        self.display_time()

    def start_timer(self):
        try:
            if not self.timer.isActive():
                self.create_timer()
        except:
            self.create_timer()
    
    def create_timer(self):
            self.timer = QTimer()
            self.timer.timeout.connect(self.update_time)
            self.timer.timeout.connect(self.maybe_change_mode)
            self.timer.setInterval(1000)
            self.timer.setSingleShot(False)
            self.timer.start()

    def pause_timer(self):
        try:
            self.timer.stop()
            self.timer.disconnect()
        except:
            pass

    def stop_timer(self):
        try:
            self.pause_timer()
            self.reset_time()
        except:
            pass
    
    def update_work_end_time(self):
        self.workEndTime = QTime(self.workHoursSpinBox.value(), self.workMinutesSpinBox.value(), self.workSecondsSpinBox.value())

    def update_rest_end_time(self):
        self.restEndTime = QTime(self.restHoursSpinBox.value(), self.restMinutesSpinBox.value(), self.restSecondsSpinBox.value())

    def update_current_mode(self, mode:str):
        self.currentMode = Mode.work if mode == "work" else Mode.rest

    def update_time(self):
        self.time = self.time.addSecs(1)
        self.display_time()

    def update_max_repetitions(self, value):
        if value == 0:
            self.currentRepetitions = 0
            self.maxRepetitions = -1
        else:
            self.maxRepetitions = 2 * value

    def maybe_change_mode(self):
        if self.currentMode is Mode.work and self.time >= self.workEndTime:
            self.stop_timer()
            self.modeComboBox.setCurrentIndex(1)
            self.increment_current_repetitions()
            started = self.maybe_start_timer()
            self.show_window_message(Status.workFinished if started else Status.repetitionsReached)
        elif self.currentMode is Mode.rest and self.time >= self.restEndTime:
            self.stop_timer()
            self.modeComboBox.setCurrentIndex(0)
            self.increment_current_repetitions()
            started = self.maybe_start_timer()
            self.show_window_message(Status.restFinished if started else Status.repetitionsReached)

    def increment_current_repetitions(self):
        if self.maxRepetitions > 0:
            self.currentRepetitions +=1
            
    def maybe_start_timer(self):
        if self.currentRepetitions != self.maxRepetitions:
            self.start_timer()
            started = True
        else:
            self.currentRepetitions = 0
            started = False
        return started
        
            
    def display_time(self):
        self.timeDisplay.display(self.time.toString("hh:mm:ss"))

    def show_window_message(self, status):
        if status is Status.workFinished:
            self.trayIcon.showMessage("Work finished", choice(work_finished_phrases), QIcon("icons/tomato.png"))
        elif status is Status.restFinished:
           self.trayIcon.showMessage("Rest finished", choice(rest_finished_phrases), QIcon("icons/tomato.png"))
        else:
            self.trayIcon.showMessage("Pomodoro finished", choice(pomodoro_finished_phrases), QIcon("icons/tomato.png"))
            self.stopButton.click()


    def setup_connections(self):
        self.playButton.clicked.connect(self.start_timer)
        self.playButton.clicked.connect(lambda: self.playButton.setDisabled(True))
        self.playButton.clicked.connect(lambda: self.pauseButton.setDisabled(False))
        self.playButton.clicked.connect(lambda: self.stopButton.setDisabled(False))

        self.pauseButton.clicked.connect(self.pause_timer)
        self.pauseButton.clicked.connect(lambda: self.playButton.setDisabled(False))
        self.pauseButton.clicked.connect(lambda: self.pauseButton.setDisabled(True))
        self.pauseButton.clicked.connect(lambda: self.stopButton.setDisabled(False))

        self.stopButton.clicked.connect(self.stop_timer)
        self.stopButton.clicked.connect(lambda: self.playButton.setDisabled(False))
        self.stopButton.clicked.connect(lambda: self.pauseButton.setDisabled(True))
        self.stopButton.clicked.connect(lambda: self.stopButton.setDisabled(True))

        self.workHoursSpinBox.valueChanged.connect(self.update_work_end_time)
        self.workMinutesSpinBox.valueChanged.connect(self.update_work_end_time)
        self.workSecondsSpinBox.valueChanged.connect(self.update_work_end_time)

        self.restHoursSpinBox.valueChanged.connect(self.update_rest_end_time)
        self.restMinutesSpinBox.valueChanged.connect(self.update_rest_end_time)
        self.restSecondsSpinBox.valueChanged.connect(self.update_rest_end_time)

        self.modeComboBox.currentTextChanged.connect(self.update_current_mode)
        self.repetitionsSpinBox.valueChanged.connect(self.update_max_repetitions)


    def setup_ui(self):
        self.size_policy = sizePolicy=QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        #CENTRALWIDGET
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.centralWidgetLayout = QVBoxLayout(self.centralWidget)
        self.centralWidget.setLayout(self.centralWidgetLayout)
        # work
        self.workGroupBox = QGroupBox("Work")
        self.workGroupBoxLayout = QHBoxLayout(self.workGroupBox)
        self.workGroupBox.setLayout(self.workGroupBoxLayout)
        self.workHoursSpinBox = QSpinBox(minimum=0, maximum=24, value=0, suffix="h", sizePolicy=self.size_policy)
        self.workMinutesSpinBox = QSpinBox(minimum=0, maximum=60, value=25, suffix="m",sizePolicy=self.size_policy)
        self.workSecondsSpinBox = QSpinBox(minimum=0, maximum=60, value=0, suffix="s",sizePolicy=self.size_policy)
        self.workGroupBoxLayout.addWidget(self.workHoursSpinBox)
        self.workGroupBoxLayout.addWidget(self.workMinutesSpinBox)
        self.workGroupBoxLayout.addWidget(self.workSecondsSpinBox)
        # rest
        self.restGroupBox = QGroupBox("Rest")
        self.restGroupBoxLayout = QHBoxLayout(self.restGroupBox)
        self.restGroupBox.setLayout(self.restGroupBoxLayout)
        self.restHoursSpinBox = QSpinBox(minimum=0, maximum=24, value=0, suffix="h",sizePolicy=self.size_policy)
        self.restMinutesSpinBox = QSpinBox(minimum=0, maximum=60, value=5, suffix="m",sizePolicy=self.size_policy)
        self.restSecondsSpinBox = QSpinBox(minimum=0, maximum=60, value=0, suffix="s",sizePolicy=self.size_policy)
        self.restGroupBoxLayout.addWidget(self.restHoursSpinBox)
        self.restGroupBoxLayout.addWidget(self.restMinutesSpinBox)
        self.restGroupBoxLayout.addWidget(self.restSecondsSpinBox)
        #OTHER
        self.otherGroupBox = QGroupBox("Other")
        self.otherGroupBoxLayout = QHBoxLayout(self.otherGroupBox)
        self.otherGroupBox.setLayout(self.otherGroupBoxLayout)
        self.repetitionsLabel = QLabel("Repetitions", sizePolicy=self.size_policy)
        self.repetitionsSpinBox = QSpinBox(minimum=0, maximum=10000, value=0, sizePolicy=self.size_policy, specialValueText="∞")
        self.modeLabel = QLabel("Mode", sizePolicy=self.size_policy)
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItems(["work", "rest"])
        self.otherGroupBoxLayout.addWidget(self.repetitionsLabel)
        self.otherGroupBoxLayout.addWidget(self.repetitionsSpinBox)
        self.otherGroupBoxLayout.addWidget(self.modeLabel)
        self.otherGroupBoxLayout.addWidget(self.modeComboBox)
        #LCDDISPLAY
        self.timeDisplay = QLCDNumber(8, sizePolicy=self.size_policy)
        self.timeDisplay.setFixedHeight(100)
        self.timeDisplay.display("00:00:00")
        self.timeDisplay.setStyleSheet("""
        border: 2px solid;
        background-color: rgb(168, 198, 78);
        color: rgb(0, 0, 0);
        """)
        #BUTTONS
        self.buttonWidget = QWidget()
        self.buttonWidgetLayout = QHBoxLayout(self.buttonWidget)
        self.buttonWidget.setLayout(self.buttonWidgetLayout)
        self.playButton = self.make_round_button("icons/play.png", "start", False)
        self.stopButton = self.make_round_button("icons/stop.png", "stop")
        self.pauseButton = self.make_round_button("icons/pause.png", "pause")
        self.buttonWidgetLayout.addWidget(self.pauseButton)
        self.buttonWidgetLayout.addWidget(self.playButton)
        self.buttonWidgetLayout.addWidget(self.stopButton)

        #CENTRALWIDGET
        self.centralWidgetLayout.addWidget(self.workGroupBox)
        self.centralWidgetLayout.addWidget(self.restGroupBox)
        self.centralWidgetLayout.addWidget(self.otherGroupBox)
        self.centralWidgetLayout.addWidget(self.timeDisplay)
        self.centralWidgetLayout.addWidget(self.buttonWidget)
    
    def make_round_button(self, path, text, disabled=True):
        button = QPushButton(text, sizePolicy = self.size_policy)
        #button.setIcon(QIcon(path))
        #button.setStyleSheet("""border-radius : 200;  
        #                      border : 0px solid black""") 
        button.setDisabled(disabled)
        return button



    def setup_trayicon(self):
        self.trayIcon = QSystemTrayIcon(QIcon("icons/tomato.png"))
        self.trayIcon.setContextMenu(QMenu())
        self.quitAction = self.trayIcon.contextMenu().addAction(QIcon("icons/exit.png"), "Exit", self.exit)
        self.quitAction.triggered.connect(self.exit)
        self.trayIcon.activated.connect(self.onActivate) 
        self.trayIcon.show()

    def exit(self):
        self.close()
        app = QApplication.instance()
        if app:
            app.quit()

    def onActivate(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()

    
def make_app():
    try:
        from PyQt5.QtWinExtras import QtWin
        QtWin.setCurrentProcessExplicitAppUserModelID(APP_ID)
    except:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(QIcon("icons/tomato.png"))
    app.setApplicationName("Pomodoro")
    app.setOrganizationName("Burak Martin")
    app.setOrganizationDomain("https://github.com/burakmartin")
    return app


if __name__ == "__main__":
    import sys
    app = make_app()
    mainWindow = MainWindow()
    sys.exit(app.exec_())
