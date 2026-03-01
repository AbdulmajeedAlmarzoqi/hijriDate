# Hijri Date Global Plugin for NVDA
# Speaks the Hijri (Islamic) date alongside the Gregorian date
# when pressing NVDA+F12 twice.

import ctypes
import datetime
import os
import threading
import wx

import addonHandler
import globalPluginHandler
import scriptHandler
import ui
import config
import gui
from gui.settingsDialogs import SettingsPanel
from gui import messageDialog
from scriptHandler import script
import inputCore
import languageHandler

from .hijri_converter import gregorian_to_hijri, format_hijri_date
from .update_checker import check_for_update, download_update

addonHandler.initTranslation()

# Configuration specification
confspec = {
	"datePriority": "string(default='hijri_first')",
}
config.conf.spec["hijriDate"] = confspec

# Get the current addon version
_addonVersion = "1.0.0"
for addon in addonHandler.getAvailableAddons():
	if addon.name == "hijriDate":
		_addonVersion = addon.version
		break


class HijriDateSettingsPanel(SettingsPanel):
	# Translators: Title of the Hijri Date settings panel in NVDA Preferences.
	title = _("Hijri Date")

	def makeSettings(self, settingsSizer):
		sHelper = gui.guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: Label for the date priority combo box in settings.
		datePriorityLabel = _("Date announcement &priority:")
		# Translators: Option to announce Hijri date before Gregorian date.
		hijriFirstLabel = _("Hijri first")
		# Translators: Option to announce Gregorian date before Hijri date.
		gregorianFirstLabel = _("Gregorian first")
		self.datePriorityChoices = ["hijri_first", "gregorian_first"]
		self.datePriorityLabels = [hijriFirstLabel, gregorianFirstLabel]
		self.datePriorityCombo = sHelper.addLabeledControl(
			datePriorityLabel,
			wx.Choice,
			choices=self.datePriorityLabels,
		)
		currentPriority = config.conf["hijriDate"]["datePriority"]
		if currentPriority in self.datePriorityChoices:
			self.datePriorityCombo.SetSelection(self.datePriorityChoices.index(currentPriority))
		else:
			self.datePriorityCombo.SetSelection(0)

		# Translators: Label for the check for updates button in settings.
		self.updateButton = sHelper.addItem(
			wx.Button(self, label=_("Check for &updates"))
		)
		self.updateButton.Bind(wx.EVT_BUTTON, self.onCheckForUpdates)

	def onSave(self):
		selected = self.datePriorityCombo.GetSelection()
		config.conf["hijriDate"]["datePriority"] = self.datePriorityChoices[selected]

	def onCheckForUpdates(self, evt):
		self.updateButton.Disable()
		# Translators: Message shown while checking for updates.
		self.updateButton.SetLabel(_("Checking for updates..."))
		t = threading.Thread(target=self._checkUpdateThread, daemon=True)
		t.start()

	def _checkUpdateThread(self):
		try:
			result = check_for_update(_addonVersion)
			wx.CallAfter(self._onUpdateResult, result)
		except Exception as e:
			wx.CallAfter(self._onUpdateError, str(e))

	def _onUpdateResult(self, result):
		# Translators: Label for the check for updates button in settings.
		self.updateButton.SetLabel(_("Check for &updates"))
		self.updateButton.Enable()
		if not result["update_available"]:
			# Translators: Message shown when the addon is up to date.
			gui.messageBox(
				_("You are up to date. Current version: {version}").format(version=_addonVersion),
				# Translators: Title of the no update available message box.
				_("Hijri Date"),
				wx.OK | wx.ICON_INFORMATION,
			)
		else:
			dlg = UpdateAvailableDialog(
				self,
				currentVersion=_addonVersion,
				newVersion=result["latest_version"],
				changelog=result["changelog"],
				downloadUrl=result["download_url"],
			)
			dlg.ShowModal()
			dlg.Destroy()

	def _onUpdateError(self, error_msg):
		# Translators: Label for the check for updates button in settings.
		self.updateButton.SetLabel(_("Check for &updates"))
		self.updateButton.Enable()
		# Translators: Error message shown when update check fails.
		gui.messageBox(
			_("Error checking for updates: {error}").format(error=error_msg),
			# Translators: Title of the update error message box.
			_("Hijri Date"),
			wx.OK | wx.ICON_ERROR,
		)


class UpdateAvailableDialog(wx.Dialog):
	"""Dialog shown when a new version is available."""

	def __init__(self, parent, currentVersion, newVersion, changelog, downloadUrl):
		# Translators: Title of the update available dialog.
		super().__init__(parent, title=_("Update Available"))
		self._downloadUrl = downloadUrl
		self._newVersion = newVersion

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		contentSizer = wx.BoxSizer(wx.VERTICAL)

		# Translators: Message showing that a new version is available.
		# {new_version} is the new version number, {current_version} is the current version.
		versionMsg = _("A new version {new_version} is available. You are currently using version {current_version}.").format(
			new_version=newVersion,
			current_version=currentVersion,
		)
		contentSizer.Add(wx.StaticText(self, label=versionMsg), flag=wx.ALL, border=10)

		if changelog:
			# Translators: Label for the what's new section in the update dialog.
			contentSizer.Add(wx.StaticText(self, label=_("What's New:")), flag=wx.LEFT | wx.TOP, border=10)
			changelogText = wx.TextCtrl(
				self,
				value=changelog,
				style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2,
				size=(450, 200),
			)
			contentSizer.Add(changelogText, flag=wx.ALL | wx.EXPAND, border=10, proportion=1)

		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		# Translators: Label for the download and install button in the update dialog.
		self.downloadButton = wx.Button(self, label=_("&Download and Install"))
		self.downloadButton.Bind(wx.EVT_BUTTON, self.onDownloadAndInstall)
		buttonSizer.Add(self.downloadButton, flag=wx.ALL, border=5)

		closeButton = wx.Button(self, wx.ID_CLOSE)
		closeButton.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CLOSE))
		buttonSizer.Add(closeButton, flag=wx.ALL, border=5)

		contentSizer.Add(buttonSizer, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
		mainSizer.Add(contentSizer, proportion=1, flag=wx.EXPAND)
		self.SetSizerAndFit(mainSizer)
		self.CenterOnParent()
		self.downloadButton.SetFocus()

	def onDownloadAndInstall(self, evt):
		self.downloadButton.Disable()
		# Translators: Label shown while downloading the update.
		self.downloadButton.SetLabel(_("Downloading..."))
		t = threading.Thread(target=self._downloadThread, daemon=True)
		t.start()

	def _downloadThread(self):
		try:
			temp_path = download_update(self._downloadUrl)
			wx.CallAfter(self._onDownloadComplete, temp_path)
		except Exception as e:
			wx.CallAfter(self._onDownloadError, str(e))

	def _onDownloadComplete(self, temp_path):
		try:
			bundle = addonHandler.AddonBundle(temp_path)
			addonHandler.installAddonBundle(bundle)
			# Translators: Message shown after successfully installing the update.
			gui.messageBox(
				_("Update installed successfully. Please restart NVDA to apply the changes."),
				# Translators: Title of the update success message.
				_("Hijri Date"),
				wx.OK | wx.ICON_INFORMATION,
			)
			self.EndModal(wx.ID_OK)
		except Exception as e:
			# Translators: Error message when installation fails.
			gui.messageBox(
				_("Error installing update: {error}").format(error=str(e)),
				# Translators: Title of the installation error message.
				_("Hijri Date"),
				wx.OK | wx.ICON_ERROR,
			)
			# Translators: Label for the download and install button in the update dialog.
			self.downloadButton.SetLabel(_("&Download and Install"))
			self.downloadButton.Enable()
		finally:
			try:
				os.unlink(temp_path)
			except OSError:
				pass

	def _onDownloadError(self, error_msg):
		# Translators: Error message when download fails.
		gui.messageBox(
			_("Error downloading update: {error}").format(error=error_msg),
			# Translators: Title of the download error message.
			_("Hijri Date"),
			wx.OK | wx.ICON_ERROR,
		)
		# Translators: Label for the download and install button in the update dialog.
		self.downloadButton.SetLabel(_("&Download and Install"))
		self.downloadButton.Enable()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(HijriDateSettingsPanel)

	def terminate(self, *args, **kwargs):
		super().terminate(*args, **kwargs)
		gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(HijriDateSettingsPanel)

	@script(
		# Translators: Description of the date/time script shown in input gestures.
		description=_("Reports the current time. Press twice to report the Gregorian and Hijri dates."),
		gesture="kb:NVDA+f12",
		category=inputCore.SCRCAT_MISC,
		speakOnDemand=True,
	)
	def script_dateTimeWithHijri(self, gesture):
		repeatCount = scriptHandler.getLastScriptRepeatCount()
		if repeatCount == 0:
			# Single press: announce time
			now = datetime.datetime.now()
			timeStr = now.strftime("%I:%M %p" if not self._use24HourFormat() else "%H:%M")
			ui.message(timeStr)
		elif repeatCount == 1:
			# Double press: announce date with Hijri
			self._announceDate()

	def _use24HourFormat(self):
		"""Check if the system uses 24-hour time format."""
		try:
			buf = ctypes.create_unicode_buffer(10)
			ctypes.windll.kernel32.GetLocaleInfoW(
				0x0400,  # LOCALE_USER_DEFAULT
				0x00001003,  # LOCALE_ITIME
				buf,
				10,
			)
			return buf.value == "1"
		except Exception:
			return False

	def _getSystemDateString(self):
		"""Get the current date formatted according to the Windows system locale."""
		buf = ctypes.create_unicode_buffer(256)
		result = ctypes.windll.kernel32.GetDateFormatW(
			0x0400,  # LOCALE_USER_DEFAULT
			0x00000002,  # DATE_LONGDATE
			None,  # current system date
			None,  # use locale default format
			buf,
			256,
		)
		if result > 0:
			return buf.value
		# Fallback to Python strftime if the API call fails
		return datetime.datetime.now().strftime("%A, %B %d, %Y")

	def _announceDate(self):
		"""Announce the Gregorian and Hijri dates based on user preference."""
		# Get Gregorian date string from system locale
		gregorianStr = self._getSystemDateString()
		# Get Hijri date from current system time
		now = datetime.datetime.now()
		hYear, hMonth, hDay = gregorian_to_hijri(now.year, now.month, now.day)
		# Determine display language for Hijri month names
		lang = languageHandler.getLanguage()
		hijriLang = "ar" if lang and lang.startswith("ar") else "en"
		hijriStr = format_hijri_date(hYear, hMonth, hDay, hijriLang)
		# Get user preference for date priority
		priority = config.conf["hijriDate"]["datePriority"]
		if priority == "gregorian_first":
			# Translators: Date announcement with Gregorian date first.
			# {gregorian} is the Gregorian date, {hijri} is the Hijri date.
			msg = _("{gregorian}, {hijri}").format(
				gregorian=gregorianStr,
				hijri=hijriStr,
			)
		else:
			# Translators: Date announcement with Hijri date first.
			# {hijri} is the Hijri date, {gregorian} is the Gregorian date.
			msg = _("{hijri}, {gregorian}").format(
				hijri=hijriStr,
				gregorian=gregorianStr,
			)
		ui.message(msg)
