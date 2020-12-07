(
	if ((menuMan.findMenu "MMD4Max") != undefined) then
	(
		menuMan.unRegisterMenu (menuMan.findMenu "MMD4Max")
		menuMan.updateMenuBar()
	)


	macroScript MMD4MaxFBX category:"MMD4Max" buttonText: "MMD4Max_v1"
	(
		python.ExecuteFile((getDir #scripts) + "\\MMD4Max\\Scripts\\UI\\MainWindow.py")
	)
	


	Main = menuMan.getMainMenuBar()
	Menu = menuMan.createMenu "MMD4Max"
	theSubMenu = menuMan.createSubMenuItem "MMD4Max" Menu
	Main.addItem theSubMenu (Main.numItems()+1)

	Action = menuMan.createActionItem "MMD4MaxFBX" "MMD4Max"
	Menu.addItem Action (Menu.numItems() + 1 )
	
	menuMan.updateMenuBar()
)
