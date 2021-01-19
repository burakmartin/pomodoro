# SPDX-License-Identifier: GPL-3.0-or-later (see AUTHORS file)
from PyQt5.QtCore import Qt, QTime, QTimer, QSettings, QDir
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLCDNumber,
    QMainWindow,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QSystemTrayIcon,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from enum import Enum
from random import choice
from .const import *
from .util import makeIcon
from qdarkstyle import load_stylesheet
import sys


class Mode(Enum):
    work = 1
    rest = 2


class Status(Enum):
    workFinished = 1
    restFinished = 2
    repetitionsReached = 3


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        settings = QSettings()
        self.setupTrayicon()
        self.setupVariables()
        self.setupUi()
        self.setupConnections()
        self.show()

    def setupVariables(self):
        settings = QSettings()
        self.workEndTime = QTime(
            settings.value(workHoursKey, 0),
            settings.value(workMinutesKey, 25),
            settings.value(workSecondsKey, 0),
        )
        self.restEndTime = QTime(
            settings.value(restHoursKey, 0),
            settings.value(restMinutesKey, 5),
            settings.value(restSecondsKey, 0),
        )
        self.timeFormat = "hh:mm:ss"
        self.time = QTime(0, 0, 0, 0)
        self.workTime = QTime(0, 0, 0, 0)
        self.restTime = QTime(0, 0, 0, 0)
        self.totalTime = QTime(0, 0, 0, 0)
        self.currentMode = Mode.work
        self.maxRepetitions = -1
        self.currentRepetitions = 0

    def setupConnections(self):
        """ Create button connections """
        self.startButton.clicked.connect(self.startTimer)
        self.startButton.clicked.connect(lambda: self.startButton.setDisabled(True))
        self.startButton.clicked.connect(lambda: self.pauseButton.setDisabled(False))
        self.startButton.clicked.connect(lambda: self.resetButton.setDisabled(False))
        self.pauseButton.clicked.connect(self.pauseTimer)
        self.pauseButton.clicked.connect(lambda: self.startButton.setDisabled(False))
        self.pauseButton.clicked.connect(lambda: self.pauseButton.setDisabled(True))
        self.pauseButton.clicked.connect(lambda: self.resetButton.setDisabled(False))
        self.pauseButton.clicked.connect(lambda: self.startButton.setText("continue"))
        self.resetButton.clicked.connect(self.resetTimer)
        self.resetButton.clicked.connect(lambda: self.startButton.setDisabled(False))
        self.resetButton.clicked.connect(lambda: self.pauseButton.setDisabled(True))
        self.resetButton.clicked.connect(lambda: self.resetButton.setDisabled(True))
        self.resetButton.clicked.connect(lambda: self.startButton.setText("start"))
        self.acceptTaskButton.pressed.connect(self.insertTask)
        self.deleteTaskButton.pressed.connect(self.deleteTask)
        """ Create spinbox  connections """
        self.workHoursSpinBox.valueChanged.connect(self.updateWorkEndTime)
        self.workMinutesSpinBox.valueChanged.connect(self.updateWorkEndTime)
        self.workSecondsSpinBox.valueChanged.connect(self.updateWorkEndTime)
        self.restHoursSpinBox.valueChanged.connect(self.updateRestEndTime)
        self.restMinutesSpinBox.valueChanged.connect(self.updateRestEndTime)
        self.restSecondsSpinBox.valueChanged.connect(self.updateRestEndTime)
        self.repetitionsSpinBox.valueChanged.connect(self.updateMaxRepetitions)
        """ Create combobox connections """
        self.modeComboBox.currentTextChanged.connect(self.updateCurrentMode)
        """ Create tablewidget connections """
        self.tasksTableWidget.cellDoubleClicked.connect(self.markTaskAsFinished)

    def setupUi(self):
        self.size_policy = sizePolicy = QSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        """ Create tabwidget """
        self.tabWidget = QTabWidget()
        """ Create tab widgets """
        timerWidget = self.setupTimerTab()
        tasksWidget = self.setupTasksTab()
        statisticsWidget = self.setupStatisticsTab()
        """ add tab widgets to tabwidget"""
        self.timerTab = self.tabWidget.addTab(timerWidget, makeIcon("timer"), "Timer")
        self.tasksTab = self.tabWidget.addTab(tasksWidget, makeIcon("tasks"), "Tasks")
        self.statisticsTab = self.tabWidget.addTab(
            statisticsWidget, makeIcon("statistics"), "Statistics"
        )
        """ Set mainwindows central widget """
        self.setCentralWidget(self.tabWidget)

    def setupTimerTab(self):
        settings = QSettings()
        self.timerContainer = QWidget(self)
        self.timerContainerLayout = QVBoxLayout(self.timerContainer)
        self.timerContainer.setLayout(self.timerContainerLayout)
        """ Create work groupbox"""
        self.workGroupBox = QGroupBox("Work")
        self.workGroupBoxLayout = QHBoxLayout(self.workGroupBox)
        self.workGroupBox.setLayout(self.workGroupBoxLayout)
        self.workHoursSpinBox = QSpinBox(
            minimum=0,
            maximum=24,
            value=settings.value(workHoursKey, 0),
            suffix="h",
            sizePolicy=self.size_policy,
        )
        self.workMinutesSpinBox = QSpinBox(
            minimum=0,
            maximum=60,
            value=settings.value(workMinutesKey, 25),
            suffix="m",
            sizePolicy=self.size_policy,
        )
        self.workSecondsSpinBox = QSpinBox(
            minimum=0,
            maximum=60,
            value=settings.value(workSecondsKey, 0),
            suffix="s",
            sizePolicy=self.size_policy,
        )
        """ Create rest groupbox"""
        self.restGroupBox = QGroupBox("Rest")
        self.restGroupBoxLayout = QHBoxLayout(self.restGroupBox)
        self.restGroupBox.setLayout(self.restGroupBoxLayout)
        self.restHoursSpinBox = QSpinBox(
            minimum=0,
            maximum=24,
            value=settings.value(restHoursKey, 0),
            suffix="h",
            sizePolicy=self.size_policy,
        )
        self.restMinutesSpinBox = QSpinBox(
            minimum=0,
            maximum=60,
            value=settings.value(restMinutesKey, 5),
            suffix="m",
            sizePolicy=self.size_policy,
        )
        self.restSecondsSpinBox = QSpinBox(
            minimum=0,
            maximum=60,
            value=settings.value(restSecondsKey, 0),
            suffix="s",
            sizePolicy=self.size_policy,
        )
        self.restGroupBoxLayout.addWidget(self.restHoursSpinBox)
        self.restGroupBoxLayout.addWidget(self.restMinutesSpinBox)
        self.restGroupBoxLayout.addWidget(self.restSecondsSpinBox)
        """ Create other groupbox"""
        self.otherGroupBox = QGroupBox("Other")
        self.otherGroupBoxLayout = QHBoxLayout(self.otherGroupBox)
        self.otherGroupBox.setLayout(self.otherGroupBoxLayout)
        self.repetitionsLabel = QLabel("Repetitions", sizePolicy=self.size_policy)
        self.repetitionsSpinBox = QSpinBox(
            minimum=0,
            maximum=10000,
            value=0,
            sizePolicy=self.size_policy,
            specialValueText="∞",
        )
        self.modeLabel = QLabel("Mode", sizePolicy=self.size_policy)
        self.modeComboBox = QComboBox()
        self.modeComboBox.addItems(["work", "rest"])
        self.otherGroupBoxLayout.addWidget(self.repetitionsLabel)
        self.otherGroupBoxLayout.addWidget(self.repetitionsSpinBox)
        self.otherGroupBoxLayout.addWidget(self.modeLabel)
        self.otherGroupBoxLayout.addWidget(self.modeComboBox)
        """ Create timer groupbox"""
        self.lcdDisplayGroupBox = QGroupBox("Time")
        self.lcdDisplayGroupBoxLayout = QHBoxLayout(self.lcdDisplayGroupBox)
        self.lcdDisplayGroupBox.setLayout(self.lcdDisplayGroupBoxLayout)
        self.timeDisplay = QLCDNumber(8, sizePolicy=self.size_policy)
        self.timeDisplay.setFixedHeight(100)
        self.timeDisplay.display("00:00:00")
        self.lcdDisplayGroupBoxLayout.addWidget(self.timeDisplay)
        """ Create pause, start and reset buttons"""
        self.buttonContainer = QWidget()
        self.buttonContainerLayout = QHBoxLayout(self.buttonContainer)
        self.buttonContainer.setLayout(self.buttonContainerLayout)
        self.startButton = self.makeButton("start", disabled=False)
        self.resetButton = self.makeButton("reset")
        self.pauseButton = self.makeButton("pause")
        """ Add widgets to container """
        self.workGroupBoxLayout.addWidget(self.workHoursSpinBox)
        self.workGroupBoxLayout.addWidget(self.workMinutesSpinBox)
        self.workGroupBoxLayout.addWidget(self.workSecondsSpinBox)
        self.timerContainerLayout.addWidget(self.workGroupBox)
        self.timerContainerLayout.addWidget(self.restGroupBox)
        self.timerContainerLayout.addWidget(self.otherGroupBox)
        self.timerContainerLayout.addWidget(self.lcdDisplayGroupBox)
        self.buttonContainerLayout.addWidget(self.pauseButton)
        self.buttonContainerLayout.addWidget(self.startButton)
        self.buttonContainerLayout.addWidget(self.resetButton)
        self.timerContainerLayout.addWidget(self.buttonContainer)
        return self.timerContainer

    def setupTasksTab(self):
        settings = QSettings()
        """ Create vertical tasks container """
        self.tasksWidget = QWidget(self.tabWidget)
        self.tasksWidgetLayout = QVBoxLayout(self.tasksWidget)
        self.tasksWidget.setLayout(self.tasksWidgetLayout)
        """ Create horizontal input container """
        self.inputContainer = QWidget()
        self.inputContainer.setFixedHeight(50)
        self.inputContainerLayout = QHBoxLayout(self.inputContainer)
        self.inputContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.inputContainer.setLayout(self.inputContainerLayout)
        """ Create text edit """
        self.taskTextEdit = QTextEdit(
            placeholderText="Describe your task briefly.", undoRedoEnabled=True
        )
        """ Create vertical buttons container """
        self.inputButtonContainer = QWidget()
        self.inputButtonContainerLayout = QVBoxLayout(self.inputButtonContainer)
        self.inputButtonContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.inputButtonContainer.setLayout(self.inputButtonContainerLayout)
        """ Create buttons """
        self.acceptTaskButton = QToolButton(icon=makeIcon("check"))
        self.deleteTaskButton = QToolButton(icon=makeIcon("trash"))
        """ Create tasks tablewidget """
        self.tasksTableWidget = QTableWidget(0, 1)
        self.tasksTableWidget.setHorizontalHeaderLabels(["Tasks"])
        self.tasksTableWidget.horizontalHeader().setStretchLastSection(True)
        self.tasksTableWidget.verticalHeader().setVisible(False)
        self.tasksTableWidget.setWordWrap(True)
        self.tasksTableWidget.setTextElideMode(Qt.ElideNone)
        self.tasksTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tasksTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.insertTasks(*settings.value(tasksKey, []))
        """ Add widgets to container widgets """
        self.inputButtonContainerLayout.addWidget(self.acceptTaskButton)
        self.inputButtonContainerLayout.addWidget(self.deleteTaskButton)
        self.inputContainerLayout.addWidget(self.taskTextEdit)
        self.inputContainerLayout.addWidget(self.inputButtonContainer)
        self.tasksWidgetLayout.addWidget(self.inputContainer)
        self.tasksWidgetLayout.addWidget(self.tasksTableWidget)
        return self.tasksWidget

    def setupStatisticsTab(self):
        """ Create statistics container """
        self.statisticsContainer = QWidget()
        self.statisticsContainerLayout = QVBoxLayout(self.statisticsContainer)
        self.statisticsContainer.setLayout(self.statisticsContainerLayout)
        """ Create work time groupbox """
        self.statisticsWorkTimeGroupBox = QGroupBox("Work Time")
        self.statisticsWorkTimeGroupBoxLayout = QHBoxLayout()
        self.statisticsWorkTimeGroupBox.setLayout(self.statisticsWorkTimeGroupBoxLayout)
        self.statisticsWorkTimeDisplay = QLCDNumber(8)
        self.statisticsWorkTimeDisplay.display("00:00:00")
        self.statisticsWorkTimeGroupBoxLayout.addWidget(self.statisticsWorkTimeDisplay)
        """ Create rest time groupbox """
        self.statisticsRestTimeGroupBox = QGroupBox("Rest Time")
        self.statisticsRestTimeGroupBoxLayout = QHBoxLayout()
        self.statisticsRestTimeGroupBox.setLayout(self.statisticsRestTimeGroupBoxLayout)
        self.statisticsRestTimeDisplay = QLCDNumber(8)
        self.statisticsRestTimeDisplay.display("00:00:00")
        self.statisticsRestTimeGroupBoxLayout.addWidget(self.statisticsRestTimeDisplay)
        """ Create total time groupbox """
        self.statisticsTotalTimeGroupBox = QGroupBox("Total Time")
        self.statisticsTotalTimeGroupBoxLayout = QHBoxLayout()
        self.statisticsTotalTimeGroupBox.setLayout(
            self.statisticsTotalTimeGroupBoxLayout
        )
        self.statisticsTotalTimeDisplay = QLCDNumber(8)
        self.statisticsTotalTimeDisplay.display("00:00:00")
        self.statisticsTotalTimeGroupBoxLayout.addWidget(
            self.statisticsTotalTimeDisplay
        )
        """ Add widgets to container """
        self.statisticsContainerLayout.addWidget(self.statisticsTotalTimeGroupBox)
        self.statisticsContainerLayout.addWidget(self.statisticsWorkTimeGroupBox)
        self.statisticsContainerLayout.addWidget(self.statisticsRestTimeGroupBox)
        return self.statisticsContainer

    def setupTrayicon(self):
        self.trayIcon = QSystemTrayIcon(makeIcon("tomato"))
        self.trayIcon.setContextMenu(QMenu())
        self.quitAction = self.trayIcon.contextMenu().addAction(
            makeIcon("exit"), "Quit", self.exit
        )
        self.quitAction.triggered.connect(self.exit)
        self.trayIcon.activated.connect(self.onActivate)
        self.trayIcon.show()

    def leaveEvent(self, event):
        super(MainWindow, self).leaveEvent(event)
        self.tasksTableWidget.clearSelection()

    def closeEvent(self, event):
        super(MainWindow, self).closeEvent(event)
        settings = QSettings()
        settings.setValue(workHoursKey, self.workHoursSpinBox.value())
        settings.setValue(
            workMinutesKey,
            self.workMinutesSpinBox.value(),
        )
        settings.setValue(
            workSecondsKey,
            self.workSecondsSpinBox.value(),
        )
        settings.setValue(restHoursKey, self.restHoursSpinBox.value())
        settings.setValue(
            restMinutesKey,
            self.restMinutesSpinBox.value(),
        )
        settings.setValue(
            restSecondsKey,
            self.restSecondsSpinBox.value(),
        )

        tasks = []
        for i in range(self.tasksTableWidget.rowCount()):
            item = self.tasksTableWidget.item(i, 0)
            if not item.font().strikeOut():
                tasks.append(item.text())
        settings.setValue(tasksKey, tasks)

    def startTimer(self):
        try:
            if not self.timer.isActive():
                self.createTimer()
        except:
            self.createTimer()

    def createTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateTime)
        self.timer.timeout.connect(self.maybeChangeMode)
        self.timer.setInterval(1000)
        self.timer.setSingleShot(False)
        self.timer.start()

    def pauseTimer(self):
        try:
            self.timer.stop()
            self.timer.disconnect()
        except:
            pass

    def resetTimer(self):
        try:
            self.pauseTimer()
            self.time = QTime(0, 0, 0, 0)
            self.displayTime()
        except:
            pass

    def maybeStartTimer(self):
        if self.currentRepetitions != self.maxRepetitions:
            self.startTimer()
            started = True
        else:
            self.currentRepetitions = 0
            started = False
        return started

    def updateWorkEndTime(self):
        self.workEndTime = QTime(
            self.workHoursSpinBox.value(),
            self.workMinutesSpinBox.value(),
            self.workSecondsSpinBox.value(),
        )

    def updateRestEndTime(self):
        self.restEndTime = QTime(
            self.restHoursSpinBox.value(),
            self.restMinutesSpinBox.value(),
            self.restSecondsSpinBox.value(),
        )

    def updateCurrentMode(self, mode: str):
        self.currentMode = Mode.work if mode == "work" else Mode.rest

    def updateTime(self):
        self.time = self.time.addSecs(1)
        self.totalTime = self.totalTime.addSecs(1)
        if self.modeComboBox.currentText() == "work":
            self.workTime = self.workTime.addSecs(1)
        else:
            self.restTime = self.restTime.addSecs(1)
        self.displayTime()

    def updateMaxRepetitions(self, value):
        if value == 0:
            self.currentRepetitions = 0
            self.maxRepetitions = -1
        else:
            self.maxRepetitions = 2 * value

    def maybeChangeMode(self):
        if self.currentMode is Mode.work and self.time >= self.workEndTime:
            self.resetTimer()
            self.modeComboBox.setCurrentIndex(1)
            self.incrementCurrentRepetitions()
            started = self.maybeStartTimer()
            self.showWindowMessage(
                Status.workFinished if started else Status.repetitionsReached
            )
        elif self.currentMode is Mode.rest and self.time >= self.restEndTime:
            self.resetTimer()
            self.modeComboBox.setCurrentIndex(0)
            self.incrementCurrentRepetitions()
            started = self.maybeStartTimer()
            self.showWindowMessage(
                Status.restFinished if started else Status.repetitionsReached
            )

    def incrementCurrentRepetitions(self):
        if self.maxRepetitions > 0:
            self.currentRepetitions += 1

    def insertTask(self):
        task = self.taskTextEdit.toPlainText()
        self.insertTasks(task)

    def insertTasks(self, *tasks):
        for task in tasks:
            if task:
                rowCount = self.tasksTableWidget.rowCount()
                self.tasksTableWidget.setRowCount(rowCount + 1)
                self.tasksTableWidget.setItem(rowCount, 0, QTableWidgetItem(task))
                self.tasksTableWidget.resizeRowsToContents()
                self.taskTextEdit.clear()

    def deleteTask(self):
        selectedIndexes = self.tasksTableWidget.selectedIndexes()
        if selectedIndexes:
            self.tasksTableWidget.removeRow(selectedIndexes[0].row())

    def markTaskAsFinished(self, row, col):
        item = self.tasksTableWidget.item(row, col)
        font = self.tasksTableWidget.item(row, col).font()
        font.setStrikeOut(False if item.font().strikeOut() else True)
        item.setFont(font)

    def displayTime(self):
        self.timeDisplay.display(self.time.toString(self.timeFormat))
        self.statisticsRestTimeDisplay.display(self.restTime.toString(self.timeFormat))
        self.statisticsWorkTimeDisplay.display(self.workTime.toString(self.timeFormat))
        self.statisticsTotalTimeDisplay.display(
            self.totalTime.toString(self.timeFormat)
        )

    def showWindowMessage(self, status):
        if status is Status.workFinished:
            self.trayIcon.showMessage(
                "Break", choice(work_finished_phrases), makeIcon("tomato")
            )
        elif status is Status.restFinished:
            self.trayIcon.showMessage(
                "Work", choice(rest_finished_phrases), makeIcon("tomato")
            )
        else:
            self.trayIcon.showMessage(
                "Finished", choice(pomodoro_finished_phrases), makeIcon("tomato")
            )
            self.resetButton.click()

    def makeButton(self, text, iconName=None, disabled=True):
        button = QPushButton(text, sizePolicy=self.size_policy)
        if iconName:
            button.setIcon(makeIcon(iconName))
        button.setDisabled(disabled)
        return button

    def exit(self):
        self.close()
        app = QApplication.instance()
        if app:
            app.quit()

    def onActivate(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show()

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