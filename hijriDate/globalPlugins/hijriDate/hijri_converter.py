# Hijri (Islamic) Calendar Converter
# Primary: Official Umm al-Qura calendar data (hijridate library)
# Fallback: Kuwaiti algorithm for dates outside supported range or import errors

import math

# Hijri month names in English
HIJRI_MONTHS_EN = [
	"Muharram",
	"Safar",
	"Rabi' al-Awwal",
	"Rabi' al-Thani",
	"Jumada al-Ula",
	"Jumada al-Thani",
	"Rajab",
	"Sha'ban",
	"Ramadan",
	"Shawwal",
	"Dhul-Qi'dah",
	"Dhul-Hijjah",
]

# Hijri month names in Arabic
HIJRI_MONTHS_AR = [
	"\u0645\u062d\u0631\u0645",
	"\u0635\u0641\u0631",
	"\u0631\u0628\u064a\u0639 \u0627\u0644\u0623\u0648\u0644",
	"\u0631\u0628\u064a\u0639 \u0627\u0644\u062b\u0627\u0646\u064a",
	"\u062c\u0645\u0627\u062f\u0649 \u0627\u0644\u0623\u0648\u0644\u0649",
	"\u062c\u0645\u0627\u062f\u0649 \u0627\u0644\u062b\u0627\u0646\u064a\u0629",
	"\u0631\u062c\u0628",
	"\u0634\u0639\u0628\u0627\u0646",
	"\u0631\u0645\u0636\u0627\u0646",
	"\u0634\u0648\u0627\u0644",
	"\u0630\u0648 \u0627\u0644\u0642\u0639\u062f\u0629",
	"\u0630\u0648 \u0627\u0644\u062d\u062c\u0629",
]

# Try to import the Umm al-Qura library
try:
	from .hijridate import Gregorian as _UmmAlQuraGregorian
	_HAS_UMMALQURA = True
except Exception:
	_HAS_UMMALQURA = False


def _gregorian_to_jd(year, month, day):
	"""Convert a Gregorian date to Julian Day Number (Kuwaiti fallback)."""
	if month <= 2:
		year -= 1
		month += 12
	A = math.floor(year / 100)
	B = 2 - A + math.floor(A / 4)
	return math.floor(365.25 * (year + 4716)) + math.floor(30.6001 * (month + 1)) + day + B - 1524.5


def _jd_to_hijri(jd):
	"""Convert Julian Day Number to Hijri date using the Kuwaiti algorithm."""
	jd = math.floor(jd) + 0.5
	L = math.floor(jd) - 1948440 + 10632
	N = math.floor((L - 1) / 10631)
	L = L - 10631 * N + 354
	J = (math.floor((10985 - L) / 5316)) * (math.floor((50 * L) / 17719)) + (math.floor(L / 5670)) * (math.floor((43 * L) / 15238))
	L = L - (math.floor((30 - J) / 15)) * (math.floor((17719 * J) / 50)) - (math.floor(J / 16)) * (math.floor((15238 * J) / 43)) + 29
	month = int(math.floor((24 * L) / 709))
	day = int(L - math.floor((709 * month) / 24))
	year = int(30 * N + J - 30)
	return (year, month, day)


def _kuwaiti_gregorian_to_hijri(year, month, day):
	"""Kuwaiti algorithm fallback for Hijri conversion."""
	jd = _gregorian_to_jd(year, month, day)
	return _jd_to_hijri(jd)


def gregorian_to_hijri(year, month, day):
	"""Convert a Gregorian date to a Hijri date.

	Uses the official Umm al-Qura calendar as primary source.
	Falls back to the Kuwaiti algorithm if unavailable or out of range.

	Args:
		year: Gregorian year
		month: Gregorian month (1-12)
		day: Gregorian day (1-31)

	Returns:
		Tuple of (hijri_year, hijri_month, hijri_day)
	"""
	if _HAS_UMMALQURA:
		try:
			hijri = _UmmAlQuraGregorian(year, month, day).to_hijri()
			return (hijri.year, hijri.month, hijri.day)
		except (OverflowError, ValueError):
			pass
	return _kuwaiti_gregorian_to_hijri(year, month, day)


def get_hijri_month_name(month, language="en"):
	"""Get the Hijri month name.

	Args:
		month: Hijri month number (1-12)
		language: Language code ("en" or "ar")

	Returns:
		Month name string
	"""
	if language == "ar":
		return HIJRI_MONTHS_AR[month - 1]
	return HIJRI_MONTHS_EN[month - 1]


def format_hijri_date(year, month, day, language="en"):
	"""Format a Hijri date as a readable string with era abbreviation.

	Args:
		year: Hijri year
		month: Hijri month (1-12)
		day: Hijri day
		language: Language code ("en" or "ar")

	Returns:
		Formatted date string (e.g. "11 Ramadan, 1448 AH" or "11 رمضان، 1448 هـ")
	"""
	month_name = get_hijri_month_name(month, language)
	if language == "ar":
		return f"{day} {month_name}\u060c {year} \u0647\u0640"
	return f"{day} {month_name}, {year} AH"
