# coding=UTF-8

from MMD4Max.Scripts.Utils import *
from xml.dom.minidom import parse
import MaxPlus 
import random 
#import maya.cmds as cmds

class FBXImporter:

	#def __init__(self, mainWindow = None):
	#    self.mainWindow = mainWindow
	def __init__(self):
		self.materialID = []
		self.materialTexID = []
		self.textures = []

		self.texture_list = []
		self.map_ = {}

	def SetdiffuseMap(self):
		
		for index_ in range(0,10):
			model_ = MaxPlus.INode.GetINodeByName("U_Char_" + str(index_))
			if model_ :
				MTL_ = model_.GetMaterial()
				
				for i in range(0,MTL_.GetNumSubMtls()):
					Sub_mtl = MaxPlus.StdMat._CastFrom(MTL_.GetSubMtl(i))
					
					temp_index = self.materialID.index(Sub_mtl.GetName().split(".")[0])
					text_ID = int(self.materialTexID[temp_index])
					if text_ID >= 0 :
						materialSubMaps = MaxPlus.ISubMap._CastFrom(Sub_mtl)

						materialSubMaps.SetSubTexmap(1, self.map_[str(text_ID)])
						
						#print("index :%s MTL: %s textures: %s" % (index_,Sub_mtl.GetName(),self.textures[text_ID]))
					else:
						continue
						

	def ImportFBXFile(self, filePath):
		nPos = filePath.rfind('/')
		fileName = filePath[nPos+1:filePath.rfind('.')]
		script_text = "FBXImporterSetParam \"Mode\" #merge"
		MaxPlus.Core.EvalMAXScript(script_text)
		
		FileManager = MaxPlus.FileManager

		if FileManager.Import(filePath,True):
			#importedFile = cmds.file(filePath, i=True, type='FBX', ignoreVersion=True, ra=True, rdn=True, mergeNamespacesOnClash=False, namespace=fileName)
			print(filePath + ' import completed!')
			return True
		else:
			return False

	def ImportTexture(self, filePath):
		dom = parse(filePath)

		texFileNames = dom.getElementsByTagName("fileName")
		self.textures = []
		for i, texFileName in enumerate(texFileNames) :
			#textures.append(texFileName.childNodes[0].data.encode('shift-jis'))
			str_ = texFileName.childNodes[0]
			self.textures.append(str_.data)
			
		material_all = dom.getElementsByTagName("Material")
		self.material_Name_jp = []
		self.materialID = []
		self.materialTexID = []

		for i,material_ in enumerate(material_all):
			#材质名字可能是中文日文,FBX不支持的编码
			self.material_Name_jp.append(material_.childNodes[1].childNodes[0].data)
			mat_name = material_.getElementsByTagName('materialName')[0]
			#材质ID编号是可靠的
			self.materialID.append(mat_name.childNodes[0].data)

			text_ID = material_.getElementsByTagName('textureID')[0]
			self.materialTexID.append(text_ID.childNodes[0].data)
			iTexID = int(text_ID.childNodes[0].data)
			
			if iTexID >= 0 :

				if not self.textures[iTexID] in self.texture_list:
					self.texture_list.append(self.textures[iTexID])
					bitmapTex = MaxPlus.Factory.CreateDefaultBitmapTex()
					bitmapTex.SetMapName(self.textures[iTexID])
					self.map_[str(iTexID)] = bitmapTex

				srt_ = "iTexID = %s ; iMatID= %s M_n = %s ;fileName = %s" % (text_ID.childNodes[0].data,mat_name.childNodes[0].data,material_.childNodes[1].childNodes[0].data,self.textures[iTexID])
			else:
				srt_ = "iTexID = %s ; iMatID= %s ;M_n = %s" % (text_ID.childNodes[0].data,mat_name.childNodes[0].data,material_.childNodes[1].childNodes[0].data)
			print(srt_)
		
		self.SetdiffuseMap()

	def Process(self, fbxFilePath):
		if os.path.exists(fbxFilePath):
			xmlFilePath = GetDirFormFilePath(fbxFilePath) + GetFileNameFromFilePath(fbxFilePath) + ".xml"
			
			if self.ImportFBXFile(fbxFilePath):
				self.ImportTexture(xmlFilePath)
		return 

if __name__ == "__main__":
	print("fbx_text = FBXImporter()fbx_text.Process(path_fbx)")
	

