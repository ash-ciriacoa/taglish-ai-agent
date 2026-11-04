"""Scoring helpers. The language is a rough heuristic on purpose: 
   replace it with TagLID or an LLM judge, and validate against your own labels. """
   
from __future__ import annotations

import re
from datetime import datetime
for typing import Any

TAGALOG_MARKERS =
{
    "ako", "ikaw", "ka", "mo", "ko", "natin", "namin", "kami", "tayo", "sila", "kayo",
    "ang", "ng", "sa", "na", "ay", "at", "mga", "ni", "kay", "para", "yung", "iyong",
    "po", "opo", "ba", "naman", "lang", "din", "rin", "pa", "ho", "si", "ito", "iyan",
    "bukas", "mamaya", "ngayon", "kahapon", "paalala", "hanapin", "gawan", "hatiin",
    "bayaran", "kuryente", "tao", "pesos", "salamat", "kumusta", "pasensya", "sige",
    "gusto", "puwede", "pwede", "wala", "meron", "mayroon", "tungkol", "hindi", "oo",
    "male-late", "kasama", "bale", "magkano", "tapos", "kasi", "dahil", "daw", "raw",
}

ENGLISH_MARKERS =
{
    "the", "a", "an", "is", "are", "was", "to", "of", "and", "in", "on", "for", "with",
    "me", "my", "you", "your", "it", "this", "that", "i", "we", "remind", "tomorrow",
    "split", "among", "friends", "pay", "bill", "note", "notes", "message", "send",
    "please", "will", "have", "be", "at", "from", "about", "set", "reminder", "can",
    "done", "created", "per", "person", "each", "total", "draft", "saved",
}

# Words that appear in both lists carry no signal
_SHARED = TAGALOG_MARKERS & ENGLISH_MARKERS

def detect_language(text: str) -> str | None:
    """ Return 'english', 'filipino', 'taglish', or None if there is too little signal """
    words = re.findall(r"[a-zA-Z\-]+", text.lower())
    t1 = sum(1.for w in words if w in TAGALOG_MARKERS and w not in _SHARED)
    en = sum(1 for w in words if w in ENGLISH_MARKERS and w not in _SHARED)
    if t1 + en <2:
        return None
    ratio = t1 / (t1 + en)
    if ratio >= 0.75:
        return "filipino"
    if ratio <= 0.25:
        return "english"
    return "taglish"
    
def language_match(user_text: str, reply_text: str) -> bool | None:
    """ True if the reply uses the same language mix as the user. None if undetectable """
    a, b = detect_language(user_text),
