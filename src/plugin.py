# for localized messages
from os import path, listdir

from . import _
from Plugins.Plugin import PluginDescriptor
from Components.config import config, ConfigBoolean
from Components.Harddisk import harddiskmanager
from BackupManager import BackupManagerautostart
from ImageManager import ImageManagerautostart
from SwapManager import SwapAutostart
from SoftcamManager import SoftcamAutostart
from ScriptRunner import ScriptRunnerAutostart
from IPKInstaller import IpkgInstaller

config.misc.restorewizardrun = ConfigBoolean(default=False)

def checkConfigBackup():
	try:
		devices = [(r.description, r.mountpoint) for r in harddiskmanager.getMountedPartitions(onlyhotplug=False)]
		list = []
		files = []
		for x in devices:
			if x[1] == '/':
				devices.remove(x)
		if len(devices):
			for x in devices:
				devpath = path.join(x[1], 'backup')
				if path.exists(devpath):
					try:
						files = listdir(devpath)
					except:
						files = []
				else:
					files = []
				if len(files):
					for file in files:
						if file.endswith('.tar.gz'):
							list.append((path.join(devpath, file), devpath, file))
		if len(list):
			return True
		else:
			return None
	except IOError, e:
		print "[ViX] unable to use device (%s)..." % str(e)
		return None


if checkConfigBackup() is None:
	backupAvailable = 0
else:
	backupAvailable = 1


def VIXMenu(session):
	import ui
	return ui.VIXMenu(session)

def UpgradeMain(session, **kwargs):
	session.open(VIXMenu)

def startSetup(menuid):
	if menuid != "setup":
		return []
	return [(_("ViX"), UpgradeMain, "vix_menu", 1010)]

def RestoreWizard(*args, **kwargs):
	from RestoreWizard import RestoreWizard
	return RestoreWizard(*args, **kwargs)

def SoftcamManager(session):
	from SoftcamManager import VIXSoftcamManager
	return VIXSoftcamManager(session)

def SoftcamMenu(session, **kwargs):
	session.open(SoftcamManager)

def SoftcamSetup(menuid):
	if menuid == "cam":
		return [(_("Softcam manager"), SoftcamMenu, "softcamsetup", 1005)]
	return []

def BackupManager(session):
	from BackupManager import VIXBackupManager
	return VIXBackupManager(session)

def BackupManagerMenu(session, **kwargs):
	session.open(BackupManager)

def ImageManager(session):
	from ImageManager import VIXImageManager
	return VIXImageManager(session)

def ImageMangerMenu(session, **kwargs):
	session.open(ImageManager)

def MountManager(session):
	from MountManager import VIXDevicesPanel
	return VIXDevicesPanel(session)

def MountManagerMenu(session, **kwargs):
	session.open(MountManager)

def ScriptRunner(session):
	from ScriptRunner import VIXScriptRunner
	return VIXScriptRunner(session)

def ScriptRunnerMenu(session, **kwargs):
	session.open(ScriptRunner)

def SwapManager(session):
	from SwapManager import VIXSwap
	return VIXSwap(session)

def SwapManagerMenu(session, **kwargs):
	session.open(SwapManager)

def filescan_open(list, session, **kwargs):
	filelist = [x.path for x in list]
	session.open(IpkgInstaller, filelist)  # list

def filescan(**kwargs):
	from Components.Scanner import Scanner, ScanPath
	return Scanner(mimetypes=["application/x-debian-package"],
				paths_to_scan=
				[
					ScanPath(path="ipk", with_subdirs=True),
					ScanPath(path="", with_subdirs=False),
				],
				name="Ipkg",
				description=_("Install extensions."),
				openfnc=filescan_open)


def Plugins(**kwargs):
	plist = [PluginDescriptor(where=PluginDescriptor.WHERE_MENU, needsRestart=False, fnc=startSetup),
			 PluginDescriptor(name=_("ViX"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=UpgradeMain),
			 PluginDescriptor(where=PluginDescriptor.WHERE_MENU, fnc=SoftcamSetup)]
	if config.softcammanager.showinextensions.value:
		plist.append(PluginDescriptor(name=_("Softcam manager"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=SoftcamMenu))
	if config.scriptrunner.showinextensions.value:
		plist.append(PluginDescriptor(name=_("Script runner"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=ScriptRunnerMenu))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=SoftcamAutostart))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_AUTOSTART, fnc=SwapAutostart))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=ImageManagerautostart))
	plist.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=BackupManagerautostart))
	if config.misc.firstrun.value and not config.misc.restorewizardrun.value and backupAvailable == 1:
		plist.append(PluginDescriptor(name=_("Restore wizard"), where=PluginDescriptor.WHERE_WIZARD, needsRestart=False, fnc=(3, RestoreWizard)))
	plist.append(PluginDescriptor(name=_("Ipkg"), where=PluginDescriptor.WHERE_FILESCAN, needsRestart=False, fnc=filescan))
	plist.append(PluginDescriptor(name=_("ViX Backup manager"), where=PluginDescriptor.WHERE_VIXMENU, fnc=BackupManagerMenu))
	plist.append(PluginDescriptor(name=_("ViX Image manager"), where=PluginDescriptor.WHERE_VIXMENU, fnc=ImageMangerMenu))
	plist.append(PluginDescriptor(name=_("ViX Mount manager"), where=PluginDescriptor.WHERE_VIXMENU, fnc=MountManagerMenu))
	plist.append(PluginDescriptor(name=_("ViX Script runner"), where=PluginDescriptor.WHERE_VIXMENU, fnc=ScriptRunnerMenu))
	plist.append(PluginDescriptor(name=_("ViX Swap manager"), where=PluginDescriptor.WHERE_VIXMENU, fnc=SwapManagerMenu))
	return plist

