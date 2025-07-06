import re
from typing import List
from hazm import Lemmatizer, WordTokenizer, maketrans


class Normalizer:
    """کلاسی برای نرمال‌سازی متن فارسی."""

    def __init__(
        self,
        correct_spacing: bool = True,
        remove_diacritics: bool = True,
        remove_specials_chars: bool = True,
        decrease_repeated_chars: bool = True,
        persian_style: bool = True,
        persian_numbers: bool = True,
        unicodes_replacement: bool = True,
        seperate_mi: bool = True,
    ):
        self.options = {
            "correct_spacing": correct_spacing,
            "remove_diacritics": remove_diacritics,
            "remove_specials_chars": remove_specials_chars,
            "decrease_repeated_chars": decrease_repeated_chars,
            "persian_style": persian_style,
            "persian_numbers": persian_numbers,
            "unicodes_replacement": unicodes_replacement,
            "seperate_mi": seperate_mi,
        }

        self.tokenizer = WordTokenizer(join_verb_parts=False)
        self.lemmatizer = Lemmatizer(joined_verb_parts=False)

        self.translation_table = maketrans(
            "كي0123456789",
            "کی۰۱۲۳۴۵۶۷۸۹"
        )

        self.replacements = [
            ("﷽", "بسم الله الرحمن الرحیم"),
            ("ﷲ", "الله"),
            ("﷼", "ریال"),
            ("ﻻ", "لا"),
            ("…", " …"),
        ]

        self.diacritics_re = re.compile(r"[\u064B-\u0652]")

        self.repeated_re = re.compile(r"([آ-ی])\1{2,}")

    def normalize(self, text: str) -> str:
        """نرمال‌سازی کامل متن را انجام می‌دهد."""
        text = text.translate(self.translation_table)

        if self.options["unicodes_replacement"]:
            for old, new in self.replacements:
                text = text.replace(old, new)

        if self.options["persian_style"]:
            text = self.apply_persian_style(text)

        if self.options["persian_numbers"]:
            text = self.convert_numbers(text)

        if self.options["remove_diacritics"]:
            text = self.diacritics_re.sub("", text)

        if self.options["remove_specials_chars"]:
            text = self.remove_special_chars(text)

        if self.options["correct_spacing"]:
            text = self.correct_spacing(text)

        if self.options["decrease_repeated_chars"]:
            text = self.repeated_re.sub(r"\1\1", text)

        if self.options["seperate_mi"]:
            text = self.separate_mi_prefix(text)

        return text.strip()

    def apply_persian_style(self, text: str) -> str:
        text = re.sub(r'"([^"]+)"', r"«\1»", text)
        text = re.sub(r"\.\.\.", "…", text)
        text = re.sub(r"(\d)\.(\d)", r"\1٫\2", text)
        return text

    def convert_numbers(self, text: str) -> str:
        return text.translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))

    def correct_spacing(self, text: str) -> str:
        text = re.sub(r"\s{2,}", " ", text)
        text = re.sub(r"([^\s])([،؛:؟!\.])", r"\1 \2", text)
        text = re.sub(r"([،؛:؟!\.])([^\s])", r"\1 \2", text)
        return text

    def remove_special_chars(self, text: str) -> str:
        specials = re.compile(r"[\u0610-\u061A\u06D6-\u06ED\u08D4-\u08FF\uFE70-\uFEFF\u0600-\u0605\u06F0-\u06F9]")
        return specials.sub("", text)

    def separate_mi_prefix(self, text: str) -> str:
        return re.sub(r"\b(ن?می)(?=[آ-ی])", r"\1‌", text)
