# Hijri Date - NVDA Add-on

[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![NVDA](https://img.shields.io/badge/NVDA-2023.1%2B-green.svg)](https://www.nvaccess.org)
[![GitHub release](https://img.shields.io/github/v/release/AbdulmajeedAlmarzoqi/hijriDate)](https://github.com/AbdulmajeedAlmarzoqi/hijriDate/releases/latest)

An NVDA add-on that speaks the Hijri (Islamic) date alongside the Gregorian date.

---

## Features

- **NVDA+F12** (press once): Reports the current time
- **NVDA+F12** (press twice): Reports Gregorian and Hijri dates together
- **Settings panel** to choose date priority (Hijri first or Gregorian first)
- **Built-in update checker** with automatic silent background checks
- **Umm al-Qura calendar** for accurate Hijri dates with Kuwaiti algorithm fallback
- Gregorian date follows the Windows system locale format
- Hijri date displayed with era abbreviation (AH / هـ)
- Full Arabic translation included

---

## Installation

### From GitHub Releases
1. Download the latest `.nvda-addon` file from the [Releases page](https://github.com/AbdulmajeedAlmarzoqi/hijriDate/releases/latest)
2. Open the downloaded file to install it in NVDA
3. Restart NVDA

### From NVDA Add-on Store
Search for "Hijri Date" in the NVDA Add-on Store (Tools > Add-on Store).

---

## Settings

Go to **NVDA Preferences > Settings > Hijri Date** to configure:

| Option | Description |
|---|---|
| Date announcement priority | Choose Hijri first (default) or Gregorian first |
| Check for updates | Check GitHub for the latest version |

---

## Building from Source

```bash
# Compile Arabic translations
python compile_mo.py

# Package as .nvda-addon
python build.py
```

The output file will be created in the project root with the version from manifest.ini.

---

## Project Structure

```
hijriDate/
  manifest.ini
  globalPlugins/hijriDate/
    __init__.py          # Main plugin (settings, script, UI)
    hijri_converter.py   # Hijri calendar conversion (Umm al-Qura + fallback)
    update_checker.py    # GitHub update checker
    hijridate/           # Vendored Umm al-Qura calendar library
  locale/ar/
    manifest.ini
    LC_MESSAGES/nvda.mo
  doc/
    en/readme.html
    ar/readme.html
```

---

## Compatibility

- Minimum NVDA version: **2023.1**
- Last tested NVDA version: **2025.3**

---

## License

This project is licensed under the [GNU General Public License v2.0](LICENSE).

## Author

**Abdulmajeed Almarzoqi** - [abdulmjad01@gmail.com](mailto:abdulmjad01@gmail.com)
