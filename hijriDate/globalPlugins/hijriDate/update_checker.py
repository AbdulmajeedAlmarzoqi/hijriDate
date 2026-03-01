# Update Checker for Hijri Date NVDA Add-on
# Checks GitHub releases for new versions and handles downloading/installing updates.

import json
import os
import tempfile
import urllib.request
import urllib.error
import ssl
import zipfile

# GitHub repository details
GITHUB_OWNER = "AbdulmajeedAlmarzoqi"
GITHUB_REPO = "hijriDate"
API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
USER_AGENT = "NVDA-HijriDate-Addon"


def _parse_version(version_str):
	"""Parse a version string like '1.0.0' or 'v1.0.0' into a comparable tuple."""
	version_str = version_str.strip().lstrip("v")
	parts = []
	for part in version_str.split("."):
		try:
			parts.append(int(part))
		except ValueError:
			parts.append(0)
	while len(parts) < 3:
		parts.append(0)
	return tuple(parts[:3])


def check_for_update(current_version):
	"""Check GitHub for a newer release.

	Args:
		current_version: Current addon version string (e.g. "1.0.0")

	Returns:
		dict with keys:
			- "update_available" (bool)
			- "latest_version" (str)
			- "changelog" (str) - release body / what's new
			- "download_url" (str) - URL to the .nvda-addon asset
		Or raises an exception on failure.
	"""
	context = ssl.create_default_context()
	req = urllib.request.Request(
		API_URL,
		headers={
			"User-Agent": USER_AGENT,
			"Accept": "application/vnd.github.v3+json",
		},
	)
	with urllib.request.urlopen(req, context=context, timeout=30) as response:
		if response.status != 200:
			raise RuntimeError(f"GitHub API returned status {response.status}")
		data = json.loads(response.read().decode("utf-8"))

	tag_name = data.get("tag_name", "")
	latest_version = tag_name.lstrip("v")
	changelog = data.get("body", "") or ""

	# Find the .nvda-addon asset
	download_url = ""
	assets = data.get("assets", [])
	for asset in assets:
		name = asset.get("name", "")
		if name.endswith(".nvda-addon"):
			download_url = asset.get("browser_download_url", "")
			break

	# If no asset found, fall back to the zipball
	if not download_url:
		download_url = data.get("zipball_url", "")

	current_tuple = _parse_version(current_version)
	latest_tuple = _parse_version(latest_version)

	return {
		"update_available": latest_tuple > current_tuple,
		"latest_version": latest_version,
		"changelog": changelog,
		"download_url": download_url,
	}


def download_update(download_url):
	"""Download the .nvda-addon file from the given URL.

	Args:
		download_url: HTTPS URL to the .nvda-addon file

	Returns:
		Path to the downloaded temporary file

	Raises:
		ValueError: If the URL is not HTTPS or the download is invalid
		RuntimeError: If the download fails
	"""
	if not download_url.startswith("https://"):
		raise ValueError("Download URL must use HTTPS")

	context = ssl.create_default_context()
	req = urllib.request.Request(
		download_url,
		headers={"User-Agent": USER_AGENT},
	)

	temp_fd, temp_path = tempfile.mkstemp(suffix=".nvda-addon")
	try:
		with urllib.request.urlopen(req, context=context, timeout=120) as response:
			if response.status != 200:
				raise RuntimeError(f"Download failed with status {response.status}")
			with os.fdopen(temp_fd, "wb") as f:
				while True:
					chunk = response.read(8192)
					if not chunk:
						break
					f.write(chunk)

		# Validate the downloaded file is a valid zip archive
		if not zipfile.is_zipfile(temp_path):
			raise ValueError("Downloaded file is not a valid addon package")

		# Verify it contains a manifest.ini (basic addon validation)
		with zipfile.ZipFile(temp_path, "r") as zf:
			names = zf.namelist()
			if "manifest.ini" not in names:
				raise ValueError("Downloaded file is not a valid NVDA addon (missing manifest.ini)")

		return temp_path

	except Exception:
		# Clean up temp file on failure
		try:
			os.unlink(temp_path)
		except OSError:
			pass
		raise
