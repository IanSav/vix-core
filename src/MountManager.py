# for localized messages
from . import _

from Screens.Screen import Screen
from enigma import eTimer
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigSelection, NoSave, configfile
from Components.Console import Console
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Tools.LoadPixmap import LoadPixmap
from os import system, rename, path, mkdir, remove
from time import sleep
from re import search

class VIXDevicesPanel(Screen):
	skin = """
	<screen position="center,center" size="640,460" title="Mount Manager">
		<ePixmap pixmap="skin_default/buttons/red.png" position="25,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="175,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="325,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="475,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="25,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="175,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_yellow" position="325,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget name="key_blue" position="475,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		<widget source="list" render="Listbox" position="10,50" size="620,450" scrollbarMode="showOnDemand" >
			<convert type="TemplatedMultiContent">
				{"template": [
				 MultiContentEntryText(pos = (90, 0), size = (600, 30), font=0, text = 0),
				 MultiContentEntryText(pos = (110, 30), size = (600, 50), font=1, flags = RT_VALIGN_TOP, text = 1),
				 MultiContentEntryPixmapAlphaBlend(pos = (0, 0), size = (80, 80), png = 2),
				],
				"fonts": [gFont("Regular", 24),gFont("Regular", 20)],
				"itemHeight": 85
				}
			</convert>
		</widget>
		<widget name="lab1" zPosition="2" position="50,90" size="600,40" font="Regular;22" halign="center" transparent="1"/>
	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Mount Manager"))
		self['key_red'] = Label(" ")
		self['key_green'] = Label(_("Setup Mounts"))
		self['key_yellow'] = Label("Unmount")
		self['key_blue'] = Label("Mount")
		self['lab1'] = Label()
		self.onChangedEntry = [ ]
		self.list = []
		self['list'] = List(self.list)
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self['actions'] = ActionMap(['WizardActions', 'ColorActions', "MenuActions"], {'back': self.close, 'green': self.SetupMounts, 'red': self.saveMypoints, 'yellow': self.Unmount, 'blue': self.Mount, "menu": self.close})
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.updateList2)
		self.updateList()

	def createSummary(self):
		return VIXDevicesPanelSummary

	def selectionChanged(self):
		if len(self.list) == 0:
			return
		self.sel = self['list'].getCurrent()
		seldev = self.sel
		for line in self.sel:
			try:
				line = line.strip()
				if line.find('Mount') >= 0:
					if line.find('/media/hdd') < 0:
						self["key_red"].setText(_("Use as HDD"))
				else:
					self["key_red"].setText(" ")
			except:
				pass
		if self.sel:
			try:
				name = str(self.sel[0])
				desc = str(self.sel[1].replace('\t','  '))
			except:
				name = ""
				desc = ""
		else:
			name = ""
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def updateList(self, result = None, retval = None, extra_args = None):
		scanning = _("Wait please while scanning for devices...")
		self['lab1'].setText(scanning)
		self.activityTimer.start(10)

	def updateList2(self):
		self.activityTimer.stop()
		self.list = []
		list2 = []
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
 			if not search('sd[a-z][1-9]',device):
				continue
			if device in list2:
				continue
			self.buildMy_rec(device)
			list2.append(device)

		f.close()
		self['list'].list = self.list
		self['lab1'].hide()

	def buildMy_rec(self, device):
		try:
			if device.find('1') > 0:
				device2 = device.replace('1', '')
		except:
			device2 = ''
		try:
			if device.find('2') > 0:
				device2 = device.replace('2', '')
		except:
			device2 = ''
		try:
			if device.find('3') > 0:
				device2 = device.replace('3', '')
		except:
			device2 = ''
		try:
			if device.find('4') > 0:
				device2 = device.replace('4', '')
		except:
			device2 = ''
		devicetype = path.realpath('/sys/block/' + device2 + '/device')
		d2 = device
		name = 'USB: '
		mypixmap = '/usr/share/enigma2/ViX_HD_Common/icons/dev_usb.png'
		model = file('/sys/block/' + device2 + '/device/model').read()
		model = str(model).replace('\n', '')
		des = ''
		if devicetype.find('/devices/pci') != -1:
			name = _("HARD DISK: ")
			mypixmap = '/usr/share/enigma2/ViX_HD_Common/icons/dev_hdd.png'
		name = name + model
		self.Console = Console()
		self.Console.ePopen("sfdisk -l /dev/sd? | grep swap | awk '{print $(NF-9)}' >/tmp/devices.tmp")
		sleep(0.5)
		f = open('/tmp/devices.tmp', 'r')
		swapdevices = f.read()
		f.close()
		swapdevices = swapdevices.replace('\n','')
		swapdevices = swapdevices.split('/')
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				d1 = parts[1]
				dtype = parts[2]
				rw = parts[3]
				break
				continue
			else:
				if device in swapdevices:
					parts = line.strip().split()
					d1 = _("None")
					dtype = 'swap'
					rw = _("None")
					break
					continue
				else:
					d1 = _("None")
					dtype = _("unavailable")
					rw = _("None")
		f.close()
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				size = int(parts[2])
				if ((size / 1024) / 1024) > 1:
					des = _("Size: ") + str((size / 1024) / 1024) + _("GB")
				else:
					des = _("Size: ") + str(size / 1024) + _("MB")
			else:
				try:
					size = file('/sys/block/' + device2 + '/' + device + '/size').read()
					size = str(size).replace('\n', '')
					size = int(size)
				except:
					size = 0
				if (((size / 2) / 1024) / 1024) > 1:
					des = _("Size: ") + str(((size / 2) / 1024) / 1024) + _("GB")
				else:
					des = _("Size: ") + str((size / 2) / 1024) + _("MB")
		f.close()
		if des != '':
			if rw.startswith('rw'):
				rw = ' R/W'
			elif rw.startswith('ro'):
				rw = ' R/O'
			else:
				rw = ""
			des += '\t' + _("Mount: ") + d1 + '\n' + _("Device: ") + '/dev/' + device + '\t' + _("Type: ") + dtype + rw
			png = LoadPixmap(mypixmap)
			res = (name, des, png)
			self.list.append(res)

	def SetupMounts(self):
		self.session.openWithCallback(self.updateList, VIXDevicePanelConf)

	def Mount(self):
		sel = self['list'].getCurrent()
		if sel:
			des = sel[1]
			des = des.replace('\n', '\t')
			parts = des.strip().split('\t')
			mountp = parts[1].replace(_("Mount: "), '')
			device = parts[2].replace(_("Device: "), '')
			system ('mount ' + device)
			mountok = False
			f = open('/proc/mounts', 'r')
			for line in f.readlines():
				if line.find(device) != -1:
					mountok = True
			if not mountok:
				self.session.open(MessageBox, _("Mount failed"), MessageBox.TYPE_INFO, timeout=5)
			self.updateList()

	def Unmount(self):
		sel = self['list'].getCurrent()
		if sel:
			des = sel[1]
			des = des.replace('\n', '\t')
			parts = des.strip().split('\t')
			mountp = parts[1].replace(_("Mount: "), '')
			device = parts[2].replace(_("Device: "), '')
			system ('umount ' + mountp)
			try:
				mounts = open("/proc/mounts")
			except IOError:
				return -1
			mountcheck = mounts.readlines()
			mounts.close()
			for line in mountcheck:
				parts = line.strip().split(" ")
				if path.realpath(parts[0]).startswith(device):
					self.session.open(MessageBox, _("Can't unmount partiton, make sure it is not being used for swap or record/timeshift paths"), MessageBox.TYPE_INFO)
			self.updateList()

	def saveMypoints(self):
		sel = self['list'].getCurrent()
		if sel:
			parts = sel[1].split()
			self.device = parts[5]
			self.mountp = parts[3]
			self.Console.ePopen('umount /media/hdd')
			self.Console.ePopen('umount ' + self.device)
			if self.mountp.find('/media/hdd') < 0:
				self.Console.ePopen("/sbin/blkid | grep " + self.device, self.add_fstab, [self.device, self.mountp])
			else:
				self.session.open(MessageBox, _("This Device is already mounted as HDD."), MessageBox.TYPE_INFO, timeout = 10, close_on_any_key = True)

	def add_fstab(self, result = None, retval = None, extra_args = None):
		self.device = extra_args[0]
		self.mountp = extra_args[1]
		self.device_uuid_tmp = result.split('UUID=')
		self.device_uuid_tmp = self.device_uuid_tmp[1].replace('"',"")
		self.device_uuid_tmp = self.device_uuid_tmp.replace('\n',"")
		self.device_uuid = 'UUID=' + self.device_uuid_tmp
		if not path.exists(self.mountp):
			mkdir(self.mountp, 0755)
		file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if '/media/hdd' not in l])
		rename('/etc/fstab.tmp','/etc/fstab')
		file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device not in l])
		rename('/etc/fstab.tmp','/etc/fstab')
		file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device_uuid not in l])
		rename('/etc/fstab.tmp','/etc/fstab')
		out = open('/etc/fstab', 'a')
		line = self.device_uuid + '\t/media/hdd\tauto\tdefaults\t0 0\n'
		out.write(line)
		out.close()
		self.Console.ePopen('mount /media/hdd', self.updateList)

	def restBo(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.updateList()
			self.selectionChanged()

class VIXDevicePanelConf(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="640,460" title="Choose where to mount your devices to:">
		<ePixmap pixmap="skin_default/buttons/red.png" position="25,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="175,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="25,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="175,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="config" position="30,60" size="580,275" scrollbarMode="showOnDemand"/>
		<widget name="Linconn" position="30,375" size="580,20" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313"/>
	</screen>"""
	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		Screen.setTitle(self, _("Choose where to mount your devices to:"))
		self['key_green'] = Label(_("Save"))
		self['key_red'] = Label(_("Cancel"))
		self['Linconn'] = Label(_("Wait please while scanning your STB_BOX devices..."))
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.saveMypoints, 'red': self.close, 'back': self.close})
		self.updateList()

	def updateList(self):
		self.list = []
		list2 = []
		self.Console = Console()
		self.Console.ePopen("sfdisk -l /dev/sd? | grep swap | awk '{print $(NF-9)}' >/tmp/devices.tmp")
		sleep(0.5)
		f = open('/tmp/devices.tmp', 'r')
		swapdevices = f.read()
		f.close()
		swapdevices = swapdevices.replace('\n','')
		swapdevices = swapdevices.split('/')
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
 			if not search('sd[a-z][1-9]',device):
				continue
			if device in list2:
				continue
			if device in swapdevices:
				continue
			self.buildMy_rec(device)
			list2.append(device)
		f.close()
		self['config'].list = self.list
		self['config'].l.setList(self.list)
		self['Linconn'].hide()

	def buildMy_rec(self, device):
		try:
			if device.find('1') > 0:
				device2 = device.replace('1', '')
		except:
			device2 = ''
		try:
			if device.find('2') > 0:
				device2 = device.replace('2', '')
		except:
			device2 = ''
		try:
			if device.find('3') > 0:
				device2 = device.replace('3', '')
		except:
			device2 = ''
		try:
			if device.find('4') > 0:
				device2 = device.replace('4', '')
		except:
			device2 = ''
		devicetype = path.realpath('/sys/block/' + device2 + '/device')
		d2 = device
		name = 'USB: '
		mypixmap = '/usr/share/enigma2/ViX_HD_Common/icons/dev_usb.png'
		model = file('/sys/block/' + device2 + '/device/model').read()
		model = str(model).replace('\n', '')
		des = ''
		if devicetype.find('/devices/pci') != -1:
			name = _("HARD DISK: ")
			mypixmap = '/usr/share/enigma2/ViX_HD_Common/icons/dev_hdd.png'
		name = name + model
		if path.exists('/tmp/devices.tmp'):
			remove('/tmp/devices.tmp')
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				print 'device',device
				parts = line.strip().split()
				d1 = parts[1]
				dtype = parts[2]
				break
				continue
			else:
				d1 = _("None")
				dtype = _("unavailable")
		f.close()
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				size = int(parts[2])
				if ((size / 1024) / 1024) > 1:
					des = _("Size: ") + str((size / 1024) / 1024) + _("GB")
				else:
					des = _("Size: ") + str(size / 1024) + _("MB")
			else:
				try:
					size = file('/sys/block/' + device2 + '/' + device + '/size').read()
					size = str(size).replace('\n', '')
					size = int(size)
				except:
					size = 0
				if (((size / 2) / 1024) / 1024) > 1:
					des = _("Size: ") + str(((size / 2) / 1024) / 1024) + _("GB")
				else:
					des = _("Size: ") + str((size / 2) / 1024) + _("MB")
		f.close()
		item = NoSave(ConfigSelection(default='/media/' + device, choices=[('/media/' + device, '/media/' + device),
		('/media/hdd', '/media/hdd'),
		('/media/hdd2', '/media/hdd2'),
		('/media/hdd3', '/media/hdd3'),
		('/media/usb', '/media/usb'),
		('/media/usb2', '/media/usb2'),
		('/media/usb3', '/media/usb3')]))
		if (d1 == '/media/meoboot'):
			item = NoSave(ConfigSelection(default='/media/meoboot', choices=[('/media/meoboot', '/media/meoboot')]))
		if dtype == 'Linux':
			dtype = 'ext3'
		else:
			dtype = 'auto'
		item.value = d1.strip()
		text = name + ' ' + des + ' /dev/' + device
		res = getConfigListEntry(text, item, device, dtype)

		if des != '' and self.list.append(res):
			pass

	def saveMypoints(self):
		self.Console = Console()
		mycheck = False
		for x in self['config'].list:
			self.device = x[2]
			self.mountp = x[1].value
			self.type = x[3]
			self.Console.ePopen('umount ' + self.device)
			self.Console.ePopen("/sbin/blkid | grep " + self.device, self.add_fstab, [self.device, self.mountp] )
		message = _("Devices changes need a system restart to take effects.\nRestart your STB_BOX now?")
		ybox = self.session.openWithCallback(self.restartBox, MessageBox, message, MessageBox.TYPE_YESNO)
		ybox.setTitle(_("Restart STB_BOX."))

	def add_fstab(self, result = None, retval = None, extra_args = None):
		self.device = extra_args[0]
		self.mountp = extra_args[1]
		self.device_uuid_tmp = result.split('UUID=')
		self.device_uuid_tmp = self.device_uuid_tmp[1].replace('"',"")
		self.device_uuid_tmp = self.device_uuid_tmp.replace('\n',"")
		self.device_uuid = 'UUID=' + self.device_uuid_tmp
		if not path.exists(self.mountp):
			mkdir(self.mountp, 0755)
		file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device not in l])
		rename('/etc/fstab.tmp','/etc/fstab')
		file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device_uuid not in l])
		rename('/etc/fstab.tmp','/etc/fstab')
		out = open('/etc/fstab', 'a')
		line = self.device_uuid + '\t' + self.mountp + '\tauto\tdata=ordered\t0 0\n'
		out.write(line)
		out.close()

	def restartBox(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.close()

class VIXDevicesPanelSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["entry"] = StaticText("")
		self["desc"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)

	def selectionChanged(self, name, desc):
		self["entry"].text = name
		self["desc"].text = desc

