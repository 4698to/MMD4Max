import sys
script = "(getDir #scripts)"
temp = MaxPlus.Core.EvalMAXScript(script).Get()
sys.path.append(temp)

from MMD4Max.Scripts.FBXConverter import *
from MMD4Max.Scripts.FBXImporter import *
from MMD4Max.Scripts.FBXModifier import *
from MMD4Max.Scripts.Utils import *
from PySide import QtGui, QtCore


#import shiboken
from PySide import shiboken
import shutil
#import threading
import os
import glob
import MaxPlus
import ctypes

class _GCProtector(object):
    widgets = []

app = QtGui.QApplication.instance()
if not app:
	app = QtGui.QApplication([])

class SuperDuperQList(QtGui.QListView):
	def __init__(self,arg,parent= None):
		super(SuperDuperQList, self).__init__(parent)
		self.arg = arg
		self.setAcceptDrops(True)
		self.setDragEnabled(True)
		self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
		self.path = []

		self.Model = QtGui.QStandardItemModel(self)
		self.setModel(self.Model)

	def Model_add_item(self,_list):
		for item in _list :
			if not item in self.path:
				listitem = QtGui.QStandardItem(item)
				self.Model.appendRow(listitem)
				self.path.append(item)

	def canInsertFromMimeData(self,mimeData):
		if mimeData.hasUrls():
			return True

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls(): # 如果是.srt结尾的路径接受
			#event.accept()
			event.acceptProposedAction()
		else:
			event.ignore()
		super(SuperDuperQList, self).dragEnterEvent(event)

	def dropEvent(self, event): # 放下文件后的动作
		#path = []
		if event.mimeData().hasUrls():
			for url in event.mimeData().urls():
				if url.toString().endswith('.vmd'):
					#if IsContainEastAsianWord(url.toString()):
					#	continue
					temp_file = url.toString().replace('file:///', '')
					if not temp_file in self.path:
						listitem = QtGui.QStandardItem(temp_file)
						self.Model.appendRow(listitem)

						print(temp_file)
						self.path.append(temp_file)


		super(SuperDuperQList, self).dropEvent(event)

	def dragMoveEvent(self, event):
		super(SuperDuperQList, self).dragMoveEvent(event)

class SuperDuperText(QtGui.QLineEdit):
	def __init__(self,parent= None):
		#QtGui.QLineEdit.__init__(self)
		super(SuperDuperText,self).__init__(parent)
		self.setAcceptDrops(True) # 设置接受拖放动作

	def canInsertFromMimeData(self,mimeData):
		if mimeData.hasUrls():
			return True

	def dragEnterEvent(self, event):
		if event.mimeData().hasUrls(): # 如果是.srt结尾的路径接受
			#event.accept()
			event.acceptProposedAction()
		else:
			event.ignore()
		super(SuperDuperText, self).dragEnterEvent(event)

	def dropEvent(self, event): # 放下文件后的动作
		path = []
		if event.mimeData().hasUrls():
			for url in event.mimeData().urls():
				if IsContainEastAsianWord(url.toString()):
					continue
				if url.toString().endswith('.pmx'):
					path.append(url.toString().replace('file:///', ''))
		if len(path) > 0:
			self.setText(path[0])

		#MainWindow.SetPmxFile()

		super(SuperDuperText, self).dropEvent(event)

	def dragMoveEvent(self, event):
		super(SuperDuperText, self).dragMoveEvent(event)


class MainWindows(QtGui.QDialog):
	def __init__(self, parent=None):
		QtGui.QDialog.__init__(self)
		self.__converter = FBXConverter()
		self.__modifier = FBXModifier()
		self.__importer = FBXImporter()
		self.init_UI()
	'''

	# Process thread
	class Processor(threading.Thread):
		def __init__(self, threadname, mainWindow = None):
			self.mainWindow = mainWindow
			threading.Thread.__init__(self, name = threadname)
			print(self.mainWindow)
		def run(self):
			print("Processor Go !")
			#self.mainWindow.AsyncProcess()

	'''
	def On_button_btn_ImpClicked(self):
		index_ = self.fbx_List.currentIndex().row()
		if index_ >= 0 :
			self.fbxFilePath = self.fbx_List.path[index_]

			if self.__importer.Process(self.fbxFilePath):
				self.Log(self.fbxFilePath + ' import completed!')

			else:
				pass

			self.fbx_List.path.pop(index_)
			self.fbx_List.Model.removeRow(index_)
		else:
			self.Log(" No selected")

	def OnDeleteButtonClicked(self):
		self.DeleteSelectedVmdFile()

	def OnProcessButtonClicked(self):
		self.SetPmxFile()
		self.AddVmdFile()
		self.__agreeTerms = self.checkBox_chk.isChecked()
		self.Process()
		#
	def init_UI(self):
		# private attribute
		#self.__converter = FBXConverter(self)
		#self.__modifier = FBXModifier(self)
		#self.__importer = FBXImporter(self)
		self.__pmxFile = ''
		self.__vmdFileList = []
		self.__fbxFileList = []

		self.__selectedVmdFileIndex = 0
		self.__agreeTerms = False
		self.__importTransparency = False
		self.__isProcessing = False
		self.__isHasTransparencyTexture = False
		self.explorerWin = None
		self.setWindowTitle(u"MMD4Max")
		self.resize(603, 420)
		#self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint|QtCore.Qt.WindowCloseButtonHint)

		version_ = MaxPlus.Application
		version_number =  (version_.Get3DSMAXVersion() >> 16) & 0xffff

		if version_number < 19000:
			hwnd = self.winId()
			ctypes.pythonapi.PyCObject_AsVoidPtr.restype = ctypes.c_void_p
			ctypes.pythonapi.PyCObject_AsVoidPtr.argtypes = [ctypes.py_object]
			int_hwnd = ctypes.pythonapi.PyCObject_AsVoidPtr(hwnd)
			MaxPlus.Win32_Set3dsMaxAsParentWindow(int_hwnd)
		else:
			self.setParent(MaxPlus.GetQMaxWindow())

		self.vbox = QtGui.QGridLayout(self)
		self.setLayout(self.vbox)


		self.pmxText = SuperDuperText(self)
		self.pmxText.setAcceptDrops(True)
		self.vbox.addWidget(self.pmxText,0,1)


		self.button_btn = QtGui.QPushButton(self)
		self.button_btn.setText('drop Import pmx/pmd file')
		self.button_btn.setEnabled(False)
		self.vbox.addWidget(self.button_btn,0,2)

		self.vmdScrollList = SuperDuperQList(self)
		self.vmdScrollList.setAcceptDrops(True)

		self.vmdScrollList.setFixedHeight(110)
		self.vbox.addWidget(self.vmdScrollList,1,1)

		self.button_btn_Add = QtGui.QPushButton(self)
		self.button_btn_Add.setText('drop Add vmd file')
		self.button_btn_Add.setEnabled(False)
		#self.button_btn_Add.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

		self.vbox.addWidget(self.button_btn_Add,1,2)
		self.button_btn_Delete = QtGui.QPushButton('Delete selected vmd file')
		self.button_btn_Delete.clicked.connect(self.OnDeleteButtonClicked)
		#self.button_btn_Delete.setEnabled(False)
		self.vbox.addWidget(self.button_btn_Delete,2,2)

		self.logText = QtGui.QTextBrowser(self)
		self.logText.setFixedHeight(200)
		self.vbox.addWidget(self.logText,3,1)
		self.logText.insertPlainText("https://gitee.com/to4698/ND_tools/tree/master/MMD4Max \n")

		#self.logText.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

		self.checkBox_chk =  QtGui.QCheckBox(self)
		self.checkBox_chk.setText(u"You must agree to these terms of use before using the model/motion")
		self.vbox.addWidget(self.checkBox_chk,2,1)

		self.processButton =QtGui.QPushButton(self)
		self.processButton.setText(u"Process")
		self.vbox.addWidget(self.processButton,3,2)
		self.processButton.clicked.connect(self.OnProcessButtonClicked)

		self.fbx_List = SuperDuperQList(self)
		self.fbx_List.setAcceptDrops(False)
		self.fbx_List.setDragEnabled(False)

		self.fbx_List.setFixedHeight(110)
		self.vbox.addWidget(self.fbx_List,4,1)

		self.button_btn_Imp = QtGui.QPushButton(self)
		self.button_btn_Imp.setText('Import selected FBX file')
		#self.button_btn_Imp.setEnabled(False)
		self.vbox.addWidget(self.button_btn_Imp,4,2)
		self.button_btn_Imp.clicked.connect(self.On_button_btn_ImpClicked)

	def CheckReadmeFile(self, pmxFilePath):
		def ShowDefaultReadme():
			self.Log('================ ReadMe ==================')
			self.Log("Please contact the model/motion author if you need them for commercial use!")
		self.ClearLog()
		txtFilenames = glob.glob(GetDirFormFilePath(pmxFilePath) + '*.txt')
		if txtFilenames:
			for readmeFile in txtFilenames:
				readmeFile = ConvertToUnixPath(readmeFile)
				if os.path.exists(readmeFile):
					inputFile = open(readmeFile)
					lines = inputFile.readlines()
					inputFile.close()
					try:
						fileName = GetFileNameFromFilePath(readmeFile).decode('shift-jis') + '.txt'
						self.Log('================ ' + fileName + ' ================')
						for line in lines:
							self.Log(line.decode('shift-jis'))
					except:
						ShowDefaultReadme()
		else:
			ShowDefaultReadme()

	#def SetPmxFile(self, fileName):
	def SetPmxFile(self):

		if(IsContainEastAsianWord(self.pmxText.text())):
			#self.MessageBox('Only support English path!')
			self.Log(u'只支持英文路径!')
			return
		self.__pmxFile = ConvertToUnixPath(self.pmxText.text()).encode('ascii','ignore')
		#cmds.textField(self.pmxText, edit=True, text=self.__pmxFile)
		self.CheckReadmeFile(self.__pmxFile)
		self.Log(self.__pmxFile)

	def AddVmdFile(self):
		for fileName in self.vmdScrollList.path:
			self.Log(fileName)
			if(IsContainEastAsianWord(fileName)):
				self.MessageBox(u'只支持英文路径!')
				continue
			fileName = ConvertToUnixPath(fileName).encode('ascii','ignore')
			self.__vmdFileList.append(fileName)
		#cmds.textScrollList(self.vmdScrollList, edit = True, append=[fileName])

	def SetHasTransparencyTexture(self, isHas):
		self.__isHasTransparencyTexture = isHas

	def IsImportTransparency(self):
		return self.__importTransparency

	def Log(self, _log):
		self.logText.insertPlainText(_log + "\n")
		def WriteToLog(_log):
			pass
			#cmds.scrollField(self.logText, edit = True, insertText = log + '\n')
		# executeInMainThreadWithResult() can't call recursively, so Log() can't be called in executeInMainThreadWithResult()
		#maya.utils.executeInMainThreadWithResult(WriteToLog, log)

	def ClearLog(self):
		self.logText.clear()
		#pass

	def MessageBox(self, msg = ''):
		self.logText.insertPlainText(msg + "\n")
		#pass



	def DeleteSelectedVmdFile(self):
		index_ = self.vmdScrollList.currentIndex().row()
		if index_ >= 0 :
			self.vmdScrollList.path.pop(index_)
			self.vmdScrollList.Model.removeRow(index_)

		#print(self.vmdScrollList.currentIndex().row())
		#index = int(self.__selectedVmdFileIndex) - 1
		#lenth = len(self.__vmdFileList)
		##if self.__selectedVmdFileIndex > 0 and index < lenth:
		#	del self.__vmdFileList[index]

	def CleanTempFiles(self):
		# clean temp fbx directory
		shutil.rmtree(GetDirFormFilePath(self.fbxFilePath),True)
		# clean *.anim.bytes files
		for vmdFile in self.__vmdFileList:
			bytesFile = GetDirFormFilePath(vmdFile) + GetFileNameFromFilePath(vmdFile) + '.anim.bytes'
			if os.path.exists(bytesFile):
				os.remove(bytesFile)

	def AsyncProcess(self):
		self.__isProcessing = True
		self.__isHasTransparencyTexture = False
		#print("AsyncProcess")
		try:
			self.Log('Start convert ' + self.__pmxFile)
			self.fbxFilePath = self.__converter.Process(self.__pmxFile, self.__vmdFileList)
			if self.fbxFilePath :
				self.fbx_List.Model_add_item([self.fbxFilePath])

			self.Log('Start modify ' + self.fbxFilePath)
			#self.__modifier.Process(self.fbxFilePath)
			# run import process in GUI thread
			def ImportProcess():
				pass
				#self.__importer.Process(self.fbxFilePath)
			self.Log('Start import ' + self.fbxFilePath)
			#maya.utils.executeInMainThreadWithResult(ImportProcess)
			self.Log('Import successed!')
		finally:
			print("CleanTempFiles")
			#self.CleanTempFiles()
			self.__isProcessing = False
			if(self.__importTransparency and self.__isHasTransparencyTexture):
				pass
				#cmds.setAttr('hardwareRenderingGlobals.transparencyAlgorithm', 3)
			else:
				pass
				#cmds.setAttr('hardwareRenderingGlobals.transparencyAlgorithm', 1)

	#def test_target(self):
	#	for i in range(1,50):
	#		print(i)

	def Process(self):
		if not self.__agreeTerms:
			self.MessageBox('You must agree to these terms to continue!')
			return
		if self.__isProcessing:
			self.MessageBox('Processing now!')
			return
		if self.__pmxFile is '':
			self.MessageBox('Please import a pmx/pmd file!')
			return
		self.ClearLog()
		#preProcessor = threading.Thread(target=self.test_target)
		#preProcessor = self.Processor('MMD4MaxProcessor', self)
		#preProcessor.daemon = True
		#preProcessor.start()
		self.AsyncProcess()

if __name__ == "__main__":
	app = QtGui.QApplication.instance()
	MainWindow = MainWindows()
	_GCProtector.widgets.append(MainWindow)
	MainWindow.show()

	#app.exec_()
