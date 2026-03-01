# Hijri (Islamic) Calendar Converter
# Uses the official Umm al-Qura calendar data via the hijridate library
# Accurate dates based on data from King Abdulaziz City for Science and Technology (KACST)

from .hijridate import Gregorian


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


def gregorian_to_hijri(year, month, day):
	"""Convert a Gregorian date to a Hijri date using the official Umm al-Qura calendar.

	Args:
		year: Gregorian year
		month: Gregorian month (1-12)
		day: Gregorian day (1-31)

	Returns:
		Tuple of (hijri_year, hijri_month, hijri_day)
	"""
	hijri = Gregorian(year, month, day).to_hijri()
	return (hijri.year, hijri.month, hijri.day)


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
