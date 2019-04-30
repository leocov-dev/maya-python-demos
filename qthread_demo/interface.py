import json
import urllib2

from maya.app.general.mayaMixin import MayaQWidgetBaseMixin

try:
    from PySide2 import QtCore, QtWidgets, QtGui
except ImportError:
    from vendor.Qt import QtCore, QtWidgets, QtGui


def load():
    """
    entry point for the UI, launch an instance of the tool with this method
    """
    global _win
    try:
        _win.close()
    except(NameError, RuntimeError):
        pass
    finally:
        _win = QThreadDemoWindow()
        _win.show()


class QThreadDemoWindow(MayaQWidgetBaseMixin, QtWidgets.QMainWindow):
    """
    A small window with a progress bar, a button to start ops, a button to reset and an output text-box
    When pushing start, the QThread will query a web api for some text, the progress bar will update,
    and the text will print in the text-box
    """

    def __init__(self):
        super(QThreadDemoWindow, self).__init__(parent=None)

        self.setFixedSize(QtCore.QSize(400, 250))
        self.setWindowTitle("QThread Demo GUI")
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        container = QtWidgets.QWidget()
        self.setCentralWidget(container)

        layout = QtWidgets.QVBoxLayout()
        container.setLayout(layout)

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setFixedHeight(40)
        layout.addWidget(self.progress_bar)

        ly_buttons = QtWidgets.QHBoxLayout()
        layout.addLayout(ly_buttons)

        self.btn_start = QtWidgets.QPushButton("Start")
        self.btn_start.setFixedHeight(30)
        self.btn_start.clicked.connect(self.start)
        ly_buttons.addWidget(self.btn_start)

        self.btn_reset = QtWidgets.QPushButton("Reset")
        self.btn_reset.setFixedHeight(30)
        self.btn_reset.setEnabled(False)
        self.btn_reset.clicked.connect(self.reset)
        ly_buttons.addWidget(self.btn_reset)

        bold_text = QtGui.QFont()
        bold_text.setPointSize(8)
        bold_text.setBold(True)

        label = QtWidgets.QLabel("Chuck Norris Jokes:")
        label.setFont(bold_text)
        layout.addWidget(label)

        self.te_sentences = QtWidgets.QPlainTextEdit()
        self.te_sentences.setReadOnly(True)
        layout.addWidget(self.te_sentences)

        self.thread = ProgressThread(15, self)
        self.thread.prog_started.connect(lambda: self.btn_start.setEnabled(False))
        self.thread.prog_started.connect(lambda: self.btn_reset.setEnabled(True))
        self.thread.prog_started.connect(self.progress_bar.setMaximum)
        self.thread.finished.connect(self.thread_finished)
        self.thread.prog_tick.connect(self.update_ui)
        self.thread.prog_abort.connect(self.te_sentences.clear)

    def start(self):
        """
        start operations by starting the thread if it is not already running
        """
        if not self.thread.isRunning():
            self.te_sentences.clear()
            self.thread.start()
        pass

    def reset(self):
        """
        if operations are running, stop the thread safely
        """
        if self.thread.isRunning():
            self.thread.abort()
            self.thread.wait()

    def thread_finished(self):
        """ when the thread is done, reset the button states """
        self.progress_bar.reset()
        self.btn_start.setEnabled(True)
        self.btn_reset.setEnabled(False)

    def update_ui(self, tick, sentence):
        """ update the main ui's progress bar and text-box """
        self.progress_bar.setValue(tick)
        self.te_sentences.appendHtml(sentence)

    def closeEvent(self, *args, **kwargs):
        """ when closing our window, close abort the thread safely first """
        self.thread.abort()
        self.thread.wait()
        self.thread.deleteLater()


class ProgressThread(QtCore.QThread):
    """
    This QThread makes http api calls to get random text and emits signals for progress status and text updates
    """
    prog_started = QtCore.Signal(int)
    prog_tick = QtCore.Signal(int, str)
    prog_done = QtCore.Signal(int)
    prog_abort = QtCore.Signal()

    def __init__(self, increments, parent):
        super(ProgressThread, self).__init__(parent=parent)

        self.increments = increments
        self._abort = False

    def abort(self):
        """ schedule an abort for the next loop iteration """
        self._abort = True

    def run(self):
        """ main loop """
        self._abort = False
        self.prog_started.emit(self.increments)

        for i in xrange(self.increments):
            if self._abort:
                self.prog_abort.emit()
                return
            sentence = "..."
            try:
                # ideally i'd use the 'requests' lib but it has lots of dependencies
                response = urllib2.urlopen("http://api.icndb.com/jokes/random").read()
                decode = json.loads(response)
                if decode:
                    value = decode.get("value")
                    if value:
                        sentence = value.get("joke")
            except urllib2.URLError as e:
                print(e)
                sentence = "Problem retrieving data from URL"

            self.prog_tick.emit(i, "{num:03d}.  {text}".format(num=i + 1, text=sentence))

        self.prog_done.emit(self.increments)
