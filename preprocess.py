from langdetect import detect
import re
from pypinyin import lazy_pinyin
from transliterate import translit

def normalize_name(name):
    """Lowercase, remove extra spaces, keep multilingual chars."""
    name = name.lower().strip()
    name = re.sub(r"\s+", " ", name)  # normalize spaces
    return name

def detect_language(name):
    """Detect main language/script."""
    try:
        return detect(name)
    except:
        return "unknown"

def is_chinese(name):
    """Check if string contains Chinese characters."""
    return bool(re.search(r"[\u4e00-\u9fff]", name))

def is_russian(name):
    """Check if string contains Cyrillic characters."""
    return bool(re.search(r"[\u0400-\u04FF]", name))

def chinese_to_pinyin(name):
    """Convert Chinese characters to pinyin."""
    return " ".join(lazy_pinyin(name))

def russian_to_latin(name):
    """Transliterate Russian to Latin."""
    try:
        return translit(name, 'ru', reversed=True)
    except:
        return name
