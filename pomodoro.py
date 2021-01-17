#!/usr/bin/env python

# Pomodoro is a small GUI for battling procrastination.
# Copyright (C) 2021  Burak Martin

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtCore import QTime, QTimer, Qt, QSettings
from PyQt5.QtWidgets import QSizePolicy, QWidget, QMainWindow, QVBoxLayout, QGroupBox, QHBoxLayout, QSpinBox, QLabel,\
                            QComboBox, QLCDNumber, QPushButton, QSystemTrayIcon, QMenu, QApplication, QTabWidget,\
                                 QTextEdit, QToolButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QFormLayout
from PyQt5.QtGui import QIcon
from qdarkstyle import load_stylesheet

from enum import Enum
from random import choice
from configparser import ConfigParser
from const import *


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
        settings = QSettings()
        self.setup_trayicon()
        self.setup_variables()
        self.setup_ui()
        self.setup_connections()
        self.show()

    def setup_variables(self):
        settings = QSettings()
        self.configParser = ConfigParser()
        self.configParser.read("config.ini")
        self.workEndTime        = QTime( settings.value(self.configParser["SETTINGS"]["WorkHours"],   0), 
                                         settings.value(self.configParser["SETTINGS"]["WorkMinutes"], 25), 
                                         settings.value(self.configParser["SETTINGS"]["WorkSeconds"], 0))
        self.restEndTime        = QTime( settings.value(self.configParser["SETTINGS"]["RestHours"],   0), 
                                         settings.value(self.configParser["SETTINGS"]["RestMinutes"], 5), 
                                         settings.value(self.configParser["SETTINGS"]["RestSeconds"], 0))
        self.timeFormat         = "hh:mm:ss"
        self.time               = QTime(0,0,0,0)
        self.workTime           = QTime(0,0,0,0)
        self.restTime           = QTime(0,0,0,0)
        self.totalTime          = QTime(0,0,0,0)
        self.currentMode        = Mode.work
        self.maxRepetitions     = -1
        self.currentRepetitions = 0

    def setup_connections(self):
        """ Create button connections """
        self.startButton.clicked.connect(self.start_timer)
        self.startButton.clicked.connect(lambda: self.startButton.setDisabled(True))
        self.startButton.clicked.connect(lambda: self.pauseButton.setDisabled(False))
        self.startButton.clicked.connect(lambda: self.resetButton.setDisabled(False))
        self.pauseButton.clicked.connect(self.pause_timer)
        self.pauseButton.clicked.connect(lambda: self.startButton.setDisabled(False))
        self.pauseButton.clicked.connect(lambda: self.pauseButton.setDisabled(True))
        self.pauseButton.clicked.connect(lambda: self.resetButton.setDisabled(False))
        self.pauseButton.clicked.connect(lambda: self.startButton.setText("continue"))
        self.resetButton.clicked.connect(self.reset_timer)
        self.resetButton.clicked.connect(lambda: self.startButton.setDisabled(False))
        self.resetButton.clicked.connect(lambda: self.pauseButton.setDisabled(True))
        self.resetButton.clicked.connect(lambda: self.resetButton.setDisabled(True))
        self.resetButton.clicked.connect(lambda: self.startButton.setText("start"))
        self.acceptTaskButton.pressed.connect(self.insert_task)
        self.deleteTaskButton.pressed.connect(self.delete_task)
        """ Create spinbox  connections """
        self.workHoursSpinBox.valueChanged.connect(self.update_work_end_time)
        self.workMinutesSpinBox.valueChanged.connect(self.update_work_end_time)
        self.workSecondsSpinBox.valueChanged.connect(self.update_work_end_time)
        self.restHoursSpinBox.valueChanged.connect(self.update_rest_end_time)
        self.restMinutesSpinBox.valueChanged.connect(self.update_rest_end_time)
        self.restSecondsSpinBox.valueChanged.connect(self.update_rest_end_time)
        self.repetitionsSpinBox.valueChanged.connect(self.update_max_repetitions)
        """ Create combobox connections """
        self.modeComboBox.currentTextChanged.connect(self.update_current_mode)
        """ Create tablewidget connections """
        self.tasksTableWidget.cellDoubleClicked.connect(self.mark_task_as_finished)

    def setup_ui(self):
        self.size_policy   = sizePolicy=QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        """ Create tabwidget """
        self.tabWidget     = QTabWidget()
        """ Create tab widgets """
        timerWidget        = self.setup_timer_tab()
        tasksWidget        = self.setup_tasks_tab()
        statisticsWidget   = self.setup_statistics_tab()
        """ add tab widgets to tabwidget"""
        self.timerTab      = self.tabWidget.addTab(timerWidget, QIcon("icons/timer.png"), "Timer")
        self.tasksTab      = self.tabWidget.addTab(tasksWidget, QIcon("icons/tasks.png"), "Tasks")
        self.statisticsTab = self.tabWidget.addTab(statisticsWidget, QIcon("icons/statistics.png"), "Statistics")
        """ Set mainwindows central widget """
        self.setCentralWidget(self.tabWidget)

    

    def setup_timer_tab(self):
        settings = QSettings()
        self.timerContainer       = QWidget(self)
        self.timerContainerLayout = QVBoxLayout(self.timerContainer)
        self.timerContainer.setLayout(self.timerContainerLayout)
        """ Create work groupbox"""
        self.workGroupBox       = QGroupBox("Work")
        self.workGroupBoxLayout = QHBoxLayout(self.workGroupBox)
        self.workGroupBox.setLayout(self.workGroupBoxLayout)
        self.workHoursSpinBox   = QSpinBox( minimum    = 0, 
                                            maximum    = 24, 
                                            value      = settings.value(self.configParser["SETTINGS"]["WorkHours"], 0), 
                                            suffix     = "h", 
                                            sizePolicy = self.size_policy)
        self.workMinutesSpinBox = QSpinBox( minimum    = 0, 
                                            maximum    = 60, 
                                            value      = settings.value(self.configParser["SETTINGS"]["WorkMinutes"], 25), 
                                            suffix     = "m",
                                            sizePolicy = self.size_policy)
        self.workSecondsSpinBox = QSpinBox( minimum    = 0, 
                                            maximum    = 60, 
                                            value      = settings.value(self.configParser["SETTINGS"]["WorkSeconds"], 0), 
                                            suffix     = "s",
                                            sizePolicy = self.size_policy)
        """ Create rest groupbox"""
        self.restGroupBox       = QGroupBox("Rest")
        self.restGroupBoxLayout = QHBoxLayout(self.restGroupBox)
        self.restGroupBox.setLayout(self.restGroupBoxLayout)
        self.restHoursSpinBox   = QSpinBox( minimum    = 0, 
                                            maximum    = 24, 
                                            value      = settings.value(self.configParser["SETTINGS"]["RestHours"], 0), 
                                            suffix     = "h",
                                            sizePolicy = self.size_policy)
        self.restMinutesSpinBox = QSpinBox( minimum    = 0, 
                                            maximum    = 60, 
                                            value      = settings.value(self.configParser["SETTINGS"]["RestMinutes"], 5), 
                                            suffix     = "m",
                                            sizePolicy = self.size_policy)
        self.restSecondsSpinBox = QSpinBox( minimum    = 0, 
                                            maximum    = 60, 
                                            value      = settings.value(self.configParser["SETTINGS"]["RestSeconds"], 0), 
                                            suffix     = "s",
                                            sizePolicy = self.size_policy)
        self.restGroupBoxLayout.addWidget(self.restHoursSpinBox)
        self.restGroupBoxLayout.addWidget(self.restMinutesSpinBox)
        self.restGroupBoxLayout.addWidget(self.restSecondsSpinBox)
        """ Create other groupbox"""
        self.otherGroupBox       = QGroupBox("Other")
        self.otherGroupBoxLayout = QHBoxLayout(self.otherGroupBox)
        self.otherGroupBox.setLayout(self.otherGroupBoxLayout)
        self.repetitionsLabel   = QLabel("Repetitions", sizePolicy=self.size_policy)
        self.repetitionsSpinBox = QSpinBox( minimum          = 0, 
                                            maximum          = 10000, 
                                            value            = 0, 
                                            sizePolicy       = self.size_policy, 
                                            specialValueText = "∞")
        self.modeLabel          = QLabel("Mode", sizePolicy=self.size_policy)
        self.modeComboBox       = QComboBox()
        self.modeComboBox.addItems(["work", "rest"])
        self.otherGroupBoxLayout.addWidget(self.repetitionsLabel)
        self.otherGroupBoxLayout.addWidget(self.repetitionsSpinBox)
        self.otherGroupBoxLayout.addWidget(self.modeLabel)
        self.otherGroupBoxLayout.addWidget(self.modeComboBox)
        """ Create timer groupbox"""
        self.lcdDisplayGroupBox       = QGroupBox("Time")
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
        self.startButton  = self.make_button("start", disabled=False)
        self.resetButton = self.make_button("reset")
        self.pauseButton = self.make_button("pause")
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

    def setup_tasks_tab(self):
        settings = QSettings()
        """ Create vertical tasks container """
        self.tasksWidget          = QWidget(self.tabWidget)
        self.tasksWidgetLayout    = QVBoxLayout(self.tasksWidget)
        self.tasksWidget.setLayout(self.tasksWidgetLayout)
        """ Create horizontal input container """
        self.inputContainer       = QWidget()
        self.inputContainer.setFixedHeight(50)
        self.inputContainerLayout = QHBoxLayout(self.inputContainer)
        self.inputContainerLayout.setContentsMargins(0,0,0,0)
        self.inputContainer.setLayout(self.inputContainerLayout)
        """ Create text edit """
        self.taskTextEdit = QTextEdit(placeholderText = "Describe your task briefly.", undoRedoEnabled=True)
        """ Create vertical buttons container """
        self.inputButtonContainer = QWidget()
        self.inputButtonContainerLayout = QVBoxLayout(self.inputButtonContainer)
        self.inputButtonContainerLayout.setContentsMargins(0,0,0,0)
        self.inputButtonContainer.setLayout(self.inputButtonContainerLayout)
        """ Create buttons """
        self.acceptTaskButton     = QToolButton(icon=QIcon("icons/check.png"))
        self.deleteTaskButton     = QToolButton(icon=QIcon("icons/trash.png"))
        """ Create tasks tablewidget """
        self.tasksTableWidget     = QTableWidget(0, 1)
        self.tasksTableWidget.setHorizontalHeaderLabels(["Tasks"])
        self.tasksTableWidget.horizontalHeader().setStretchLastSection(True)
        self.tasksTableWidget.verticalHeader().setVisible(False)
        self.tasksTableWidget.setWordWrap(True)
        self.tasksTableWidget.setTextElideMode(Qt.ElideNone)
        self.tasksTableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tasksTableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.insert_tasks(*settings.value(self.configParser["SETTINGS"]["Tasks"], []))
        """ Add widgets to container widgets """
        self.inputButtonContainerLayout.addWidget(self.acceptTaskButton)
        self.inputButtonContainerLayout.addWidget(self.deleteTaskButton)
        self.inputContainerLayout.addWidget(self.taskTextEdit)
        self.inputContainerLayout.addWidget(self.inputButtonContainer)
        self.tasksWidgetLayout.addWidget(self.inputContainer)
        self.tasksWidgetLayout.addWidget(self.tasksTableWidget)
        return self.tasksWidget

    def setup_statistics_tab(self):
        """ Create statistics container """
        self.statisticsContainer             = QWidget()
        self.statisticsContainerLayout       = QVBoxLayout(self.statisticsContainer)
        self.statisticsContainer.setLayout(self.statisticsContainerLayout)
        """ Create work time groupbox """
        self.statisticsWorkTimeGroupBox       = QGroupBox("Work Time")
        self.statisticsWorkTimeGroupBoxLayout = QHBoxLayout()
        self.statisticsWorkTimeGroupBox.setLayout(self.statisticsWorkTimeGroupBoxLayout)
        self.statisticsWorkTimeDisplay  = QLCDNumber(8)
        self.statisticsWorkTimeDisplay.display("00:00:00")
        self.statisticsWorkTimeGroupBoxLayout.addWidget(self.statisticsWorkTimeDisplay)
        """ Create rest time groupbox """
        self.statisticsRestTimeGroupBox       = QGroupBox("Rest Time")
        self.statisticsRestTimeGroupBoxLayout = QHBoxLayout()
        self.statisticsRestTimeGroupBox.setLayout(self.statisticsRestTimeGroupBoxLayout)
        self.statisticsRestTimeDisplay        = QLCDNumber(8)
        self.statisticsRestTimeDisplay.display("00:00:00")
        self.statisticsRestTimeGroupBoxLayout.addWidget(self.statisticsRestTimeDisplay)
        """ Create total time groupbox """
        self.statisticsTotalTimeGroupBox       = QGroupBox("Total Time")
        self.statisticsTotalTimeGroupBoxLayout = QHBoxLayout()
        self.statisticsTotalTimeGroupBox.setLayout(self.statisticsTotalTimeGroupBoxLayout)
        self.statisticsTotalTimeDisplay        = QLCDNumber(8)
        self.statisticsTotalTimeDisplay.display("00:00:00")
        self.statisticsTotalTimeGroupBoxLayout.addWidget(self.statisticsTotalTimeDisplay)
        """ Add widgets to container """
        self.statisticsContainerLayout.addWidget(self.statisticsTotalTimeGroupBox)
        self.statisticsContainerLayout.addWidget(self.statisticsWorkTimeGroupBox)
        self.statisticsContainerLayout.addWidget(self.statisticsRestTimeGroupBox)
        return self.statisticsContainer

    def setup_trayicon(self):
        self.trayIcon = QSystemTrayIcon(QIcon("icons/tomato.png"))
        self.trayIcon.setContextMenu(QMenu())
        self.quitAction = self.trayIcon.contextMenu().addAction(QIcon("icons/exit.png"), "Quit", self.exit)
        self.quitAction.triggered.connect(self.exit)
        self.trayIcon.activated.connect(self.onActivate) 
        self.trayIcon.show()

    def leaveEvent(self, event):
        super(MainWindow, self).leaveEvent(event)
        self.tasksTableWidget.clearSelection()

    def closeEvent(self, event):
        super(MainWindow, self).closeEvent(event)
        settings = QSettings()
        settings.setValue(self.configParser["SETTINGS"]["WorkHours"],   self.workHoursSpinBox.value())
        settings.setValue(self.configParser["SETTINGS"]["WorkMinutes"], self.workMinutesSpinBox.value())
        settings.setValue(self.configParser["SETTINGS"]["WorkSeconds"], self.workSecondsSpinBox.value())
        settings.setValue(self.configParser["SETTINGS"]["RestHours"],   self.restHoursSpinBox.value())
        settings.setValue(self.configParser["SETTINGS"]["RestMinutes"], self.restMinutesSpinBox.value())
        settings.setValue(self.configParser["SETTINGS"]["RestSeconds"], self.restSecondsSpinBox.value())

        tasks = []
        for i in range(self.tasksTableWidget.rowCount()):
            item = self.tasksTableWidget.item(i,0)
            if not item.font().strikeOut():
                tasks.append(item.text())
        settings.setValue(self.configParser["SETTINGS"]["Tasks"], tasks)



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

    def reset_timer(self):
        try:
            self.pause_timer()
            self.time = QTime(0,0,0,0)
            self.display_time()
        except:
            pass

    def maybe_start_timer(self):
        if self.currentRepetitions != self.maxRepetitions:
            self.start_timer()
            started = True
        else:
            self.currentRepetitions = 0
            started = False
        return started
    
    def update_work_end_time(self):
        self.workEndTime = QTime(self.workHoursSpinBox.value(), self.workMinutesSpinBox.value(), self.workSecondsSpinBox.value())

    def update_rest_end_time(self):
        self.restEndTime = QTime(self.restHoursSpinBox.value(), self.restMinutesSpinBox.value(), self.restSecondsSpinBox.value())

    def update_current_mode(self, mode:str):
        self.currentMode = Mode.work if mode == "work" else Mode.rest

    def update_time(self):
        self.time = self.time.addSecs(1)
        self.totalTime = self.totalTime.addSecs(1)
        if self.modeComboBox.currentText() == "work":
            self.workTime = self.workTime.addSecs(1)
        else:
            self.restTime = self.restTime.addSecs(1)
        self.display_time()

    def update_max_repetitions(self, value):
        if value == 0:
            self.currentRepetitions = 0
            self.maxRepetitions = -1
        else:
            self.maxRepetitions = 2 * value

    def maybe_change_mode(self):
        if self.currentMode is Mode.work and self.time >= self.workEndTime:
            self.reset_timer()
            self.modeComboBox.setCurrentIndex(1)
            self.increment_current_repetitions()
            started = self.maybe_start_timer()
            self.show_window_message(Status.workFinished if started else Status.repetitionsReached)
        elif self.currentMode is Mode.rest and self.time >= self.restEndTime:
            self.reset_timer()
            self.modeComboBox.setCurrentIndex(0)
            self.increment_current_repetitions()
            started = self.maybe_start_timer()
            self.show_window_message(Status.restFinished if started else Status.repetitionsReached)

    def increment_current_repetitions(self):
        if self.maxRepetitions > 0:
            self.currentRepetitions +=1  

    def insert_task(self):
        task = self.taskTextEdit.toPlainText()
        self.insert_tasks(task)
    
    def insert_tasks(self, *tasks):
        for task in tasks:
            if task:
                rowCount = self.tasksTableWidget.rowCount()
                self.tasksTableWidget.setRowCount(rowCount + 1)
                self.tasksTableWidget.setItem(rowCount, 0, QTableWidgetItem(task))
                self.tasksTableWidget.resizeRowsToContents()
                self.taskTextEdit.clear()

    def delete_task(self):
        selectedIndexes = self.tasksTableWidget.selectedIndexes()
        if selectedIndexes:
            self.tasksTableWidget.removeRow(selectedIndexes[0].row())
        
    def mark_task_as_finished(self, row, col):
        item = self.tasksTableWidget.item(row, col)
        font = self.tasksTableWidget.item(row, col).font()
        font.setStrikeOut(False if item.font().strikeOut() else True)
        item.setFont(font)
   
    def display_time(self):
        self.timeDisplay.display(self.time.toString(self.timeFormat))
        self.statisticsRestTimeDisplay.display(self.restTime.toString(self.timeFormat))
        self.statisticsWorkTimeDisplay.display(self.workTime.toString(self.timeFormat))
        self.statisticsTotalTimeDisplay.display(self.totalTime.toString(self.timeFormat))


    def show_window_message(self, status):
        if status is Status.workFinished:
            self.trayIcon.showMessage("Break", choice(work_finished_phrases), QIcon("icons/tomato.png"))
        elif status is Status.restFinished:
           self.trayIcon.showMessage("Work", choice(rest_finished_phrases), QIcon("icons/tomato.png"))
        else:
            self.trayIcon.showMessage("Finished", choice(pomodoro_finished_phrases), QIcon("icons/tomato.png"))
            self.resetButton.click()


    
    def make_button(self, text, iconPath=None, disabled=True):
        button = QPushButton(text, sizePolicy = self.size_policy)
        if iconPath:
            button.setIcon(QIcon(iconPath))
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
    app.setStyleSheet(load_stylesheet(qt_api="pyqt5"))
    mainWindow = MainWindow()
    sys.exit(app.exec_())
