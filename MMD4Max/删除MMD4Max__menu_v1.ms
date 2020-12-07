python.Init()
(
	if ((menuMan.findMenu "MMD4Max") != undefined) then
	(
		menuMan.unRegisterMenu (menuMan.findMenu "MMD4Max")
		menuMan.updateMenuBar()
	)

)
