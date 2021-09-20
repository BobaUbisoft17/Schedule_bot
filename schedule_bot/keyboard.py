from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


_CLASSES_NUMBERS_WITH_LETTERS = {
	5: "АБВГДЕЖ",
	6: "АБВГДЕЖЗ",
	7: "АБВГДЕЖЗ",
	8: "АБВГДЕЖЗ",
	9: "АБВГДЕЖЗИКЛ",
	10: "АБВ",
	11: "АБВ",
}

CLASSES_NAMES = [
	f"{number}{letter}"
	for (number, letters) in _CLASSES_NUMBERS_WITH_LETTERS.items()
	for letter in letters
]
