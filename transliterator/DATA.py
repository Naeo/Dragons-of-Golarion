"""
This file just contains a set of dictionaries defining how to map
IPA transliterations to other scripts.  Each script should have three
dictionaries:
    SCRIPTNAME_IPA
    SCRIPTNAME_CLEANER
    SCRIPTNAME_KEEPABLE

SCRIPTNAME_IPA defines the mappings of IPA characters to characters
in the script.

SCRIPTNAME_CLEANER defines any mappings from IPA-to-IPA that need to
be done to make the script work with English phonology.  E.g., mapping
a near-high near-back rounded vowel (like in "book") to a high back rounded
vowel (like in "blue").  In principle these dictionaries can be left
empty and everything can be done in trhe SCRIPTNAME_IPA dictionary.
However, as a general extensible framework, this lets script-specific
cleaning be done more easily, I find.

SCRIPTNAME_KEEPABLE defines any characters that are okay to keep,
untransliterated.
"""

# A set of common phonemes in English which need mappings.
USUAL_ENGLISH_SOUNDS = [
    'a', 'b', 'd', 'e', 'f', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 
    'p', 'r', 's', 't', 'u', 'v', 'w', 'z', 'æ', 'ð', 'ŋ', 'ɐ', 'ɑ', 
    'ɔ', 'ə', 'ɚ', 'ɛ', 'ɜ', 'g', 'ɪ', 'ɹ', 'ɾ', 'ʃ', 'ʊ', 'ʌ', 'ʒ', 
    'ʔ', 'ˈ', 'ˌ', 'ː', '̩', 'θ', 'ᵻ']


AVESTAN_IPA = {
    'eː': '𐬉', 'oː': '𐬋', 'ɒ': '𐬂', 'g': '𐬔', 'ʃ': '𐬱', 'aː': '𐬁', 
    't̚': '𐬝', 'r': '𐬭', 'ŋʲ': '𐬣', 'ɔ': '𐬊', 'uː': '𐬏', 'z': '𐬰', 
    'ʊ': '𐬎', 'h': '𐬵', 'ŋ': '𐬧', 'mʰ': '𐬩', 'β': '𐬡', 'm̥': '𐬩', 
    'ɲ': '𐬦', 'e': '𐬈', 'j': '𐬫', 'ɒː': '𐬃', 'd': '𐬛', 'a': '𐬀', 
    'gʲ': '𐬕', 's': '𐬯', 'ɟ': '𐬕', 'b': '𐬠', 'uu̯': '𐬎𐬎', 't': '𐬙', 
    'ʒ': '𐬲', 'tʃ': '𐬗', 'p': '𐬞', 'iː': '𐬍', 'v': '𐬬', 'ɪ': '𐬌', 
    'əː': '𐬇', 'ç': '𐬒', 'dʒ': '𐬘', 'xʷ': '𐬓', 'f': '𐬟', 'θ': '𐬚', 
    'ii̯': '𐬌𐬌', 'xʲ': '𐬒', 'x': '𐬑', 'ã': '𐬅', 'ð': '𐬜', 'm': '𐬨', 
    'n': '𐬥', 'ə': '𐬆', 'ŋʷ': '𐬤', 'ʂ': '𐬴', 'ɕ': '𐬳', 'k': '𐬐', 'l':'𐬮',
    'w':'𐬎𐬎', ".":"𐬽", ";":"𐬻", ":":"",
    
    # some custom ones, since cleaning with .replace would be too hard
    'i': '𐬍', 'u':'𐬏', 'o':'𐬋', 'ɔː': '𐬊',
}
AVESTAN_CLEANER = {
    "ɹ":"r",
    "ɛ":"e",
    "ɑ":"a",
    "æ":"a",
    "ᵻ":"ɪ",
    "ʌ":"ə:",
    "ɐ":"a",
    "ɜ":"e",
    "ɚ":"ər",
    "ɾ":"d", # trilled R already used for rhotic, so flap to d, I guess
    "n̩":"n",
    "ʔ":"", # no good glottal stop representation    
    "?":"",
    ",":"",
    "!":"",
}
AVESTAN_KEEPABLE = frozenset({
    "'", "\"", "𐬺", " "
})

GEORGIAN_CLEANER = {
    "ɚ":"ər", 
    "ɹ":"r",
    "ɜ":"ɛr",
    "ʌ":"ə",
    "ɪ":"i",
    "ʊ":"u",
    "ɐ":"a",
    "ᵻ":"i",
    "ŋ":"ng",
    "ɾ":"d",
    "ː":"",
}
GEORGIAN_IPA = {
    "a":"ა",
    "æ":"ა",
    "ɑ":"ა",
    "b":"ბ",
    "d":"დ",
    "dz":"ძ",
    "dʒ":"ჯ",
    "e":"ჱ",
    "eɪ":"ჱ",
    "ə":"ჷ",
    "ɛ":"ე",
    "f":"ჶ",
    "g":"გ", # not a regular G--is the IPA G, different codepoint
    "g":"გ",
    "ɣ":"ღ",
    "h":"ჰ",
    "i":"ი",
    "j":"ჲ",
    "je":"ჲ",
    "k":"ქ",
    "kʰ":"ქ",
    "kʼ":"კ",
    "l":"ლ",
    "m":"მ",
    "n":"ნ",
    "o":"ჵ",
    "œ":"ო",
    "ɔ":"ო",
    "pʰ":"ფ",
    "pʼ":"პ",
    "p":"ფ",
    "θ":"ჴ", # originally qh
    "ð":"ყ", # originally q'
    "r":"რ",
    "s":"ს",
    "ʃ":"შ",
    "t":"თ",
    "tsʰ":"ც",
    "tsʼ":"წ",
    "tʃʰ":"ჩ",
    "tʃʼ":"ჭ",
    # "t":"ტ",
    "u":"უ",
    "ui":"ჳ",
    "v":"ვ",
    "w":"ჳ",
    "y":"უ",
    "z":"ზ",
    "ʒ":"ჟ",
    "ʔ":"ჸ",
    "χ":"ხ",
}
GEORGIAN_KEEPABLE = frozenset({".", ",", ":", ";", "?", "!", " "})

TIFINAGH_CLEANER = {
    ":":"",
    "ᵻ":"i",
    "ɹ":"r",
    "ɐ":"a", 
    "ɜ":"er", 
    "ɾ":"d",
    "ɛ":"e",
    "ɚ":"er", 
    "ɪ":"i",
    "ɔ":"o", 
    "ɑ":"a",
    "ʔ":"",
    "!":".", # looks too much like ng letter
    "ː":""
}
TIFINAGH_IPA = {
    "æ":"ⴰ",
    "b":"ⴱ",
    # "b":"ⵀ", # tuareg yab
    "d":"ⴷ",
    "ð":"ⴸ",
    "d͡ʒ":"ⴵ",
    "d͡ʒ":"ⴶ",
    "dˤ":"ⴹ",
    "ðˤ":"ⴺ",
    "e":"ⵦ",
    "ə":"ⴻ",
    "f":"ⴼ",
    "g":"ⴳ",
    "ɣ":"ⴴ",
    "ʌ":"ⵖ", # originally ɣ
    # "ɣ":"ⵗ",
    "ʊ":"ⵘ", # originally ɣ
    # "h":"ⵁ",
    "h":"ⵂ",
    # "h":"ⵀ",
    "ħ":"ⵃ",
    "i":"ⵉ",
    "j":"ⵢ",
    "k":"ⴽ",
    "k":"ⴾ",
    "l":"ⵍ",
    "m":"ⵎ",
    "n":"ⵏ",
    "nj":"ⵐ",
    "ŋ":"ⵑ",
    "o":"ⵧ",
    "p":"ⵒ",
    "q":"ⵇ",
    "q":"ⵈ",
    "r":"ⵔ",
    "rˤ":"ⵕ",
    "s":"ⵙ",
    "sˤ":"ⵚ",
    "ʃ":"ⵛ",
    "t":"ⵜ",
    "t͡ʃ":"ⵞ",
    "tˤ":"ⵟ",
    "v":"ⵠ",
    "u":"ⵓ", # originally w
    "w":"ⵡ",
    "ʷ":" ⵯ",
    "x":"ⴿ",
    "z":"ⵣ",
    # "z":"ⵤ",
    "zˤ":"ⵥ",
    # "ʒ":"ⵊ",
    # "ʒ":"ⵋ",
    # "ʒ":"ⵌ",
    "ʒ":"ⵘ",
    "a":"ⵄ", # originally ʕ
    "β":"ⴲ",
    "θ":"ⵝ",
     "χ":"ⵆ",
     # "χ":"ⵅ",
}
TIFINAGH_KEEPABLE = frozenset(
    {".", ",", ";", "?", " "}
)

ELDER_FUTHARK_IPA = {
    "f":"ᚠ",
    "u":"ᚢ",
    "ð":"ᚦ",
    "θ":"ᚦ",
    "a":"ᚨ",
    "r":"ᚱ",
    "k":"ᚲ",
    "g":"ᚷ",
    "w":"ᚹ",
    # "h":"ᚺ",
    "h":"ᚻ",
    "n":"ᚾ",
    "i":"ᛁ",
    "j":"ᛃ",
    "æ":"ᛇ",
    "p":"ᛈ",
    "z":"ᛉ",
    # "s":"ᛊ",
    "s":"ᛋ",
    "t":"ᛏ",
    "b":"ᛒ",
    "e":"ᛖ",
    "m":"ᛗ",
    "l":"ᛚ",
    # "ŋ":"ᛜ",
    "ŋ":"ᛝ",
    "d":"ᛞ",
    "o":"ᛟ",
}
ELDER_FUTHARK_CLEANER = {
    "ː":"",
    "ɚ":"er", 
    "ɹ":"r",
    "ɜ":"er",
    "ʌ":"u",
    "ɪ":"i",
    "ʊ":"u",
    "ɐ":"a",
    "ᵻ":"i",
    "ŋ":"ng",
    "ɾ":"d",
    "ɑ":"a",
    "ɛ":"e",
    "ə":"e",
    "ʔ":"",
    "v":"f",
    "ʒ":"zh",
    "ʃ":"sh",
    "ɔ":"a",
}
ELDER_FUTHARK_KEEPABLE = frozenset({';', '!', '?', ':', '.', ','})

MEDEIVAL_RUNES_IPA = {
    'a':'ᛆ',
    'b':'ᛒ',
    'c':'ᛍ',
    'd':'ᛑ',
    'e':'ᛂ',
    'f':'ᚠ',
    'g':'ᚵ',
    'h':'ᚼ',
    'i':'ᛁ',
    'k':'ᚴ',
    'l':'ᛚ',
    'm':'ᛘ',
    'n':'ᚿ',
    'o':'ᚮ',
    'p':'ᛕ',
    'p':'ᛔ',
    'q':'ᛩ',
    'r':'ᚱ',
    's':'ᛋ',
    't':'ᛐ',
    'u':'ᚢ',
    'v':'ᚡ',
    'v':'ᚢ',
    'w':'ᚥ',
    'x':'ᛪ',
    'y':'ᚤ',
    'y':'ᛨ',
    'y':'ᛦ',
    'z':'ᛎ',
    'th':'ᚦ',
}
MEDEIVAL_RUNES_CLEANER = {
    "j":"i",
}
MEDEIVAL_RUNES_KEEPABLE = frozenset({';', '!', '?', ':', '.', ','})

MONGOLIAN_IPA = {
    'a':'ᠠ',
    'e':'ᠡ',
    'i':'ᠢ',
    'o':'ᠣ',
    'ʊ':'ᠤ',
    'ɵ':'ᠥ',
    'u':'ᠦ',
    'e:':'ᠧ',
    'n':'ᠨ',
    'ŋ':'ᠩ',
    'b':'ᠪ',
    'p':'ᠫ',
    'χ':'ᠬ',
    'g':'ᠭ', # originally ɢ
    'm':'ᠮ',
    'l':'ᠯ',
    's':'ᠰ',
    'ʃ':'ᠱ',
    't':'ᠲ',
    'd':'ᠳ',
    't͡ʃ':'ᠴ',
    'd͡ʒ':'ᠵ',
    'j':'ᠶ',
    'r':'ᠷ',
    'w':'ᠸ',
    'f':'ᠹ',
    'k':'ᠺ',
    'k':'ᠻ',
    't͡s':'ᠼ',
    'd͡z':'ᠽ',
    'h':'ᠾ', # originally x
    'ɹ':'ᠿ',
    'ɬ':'ᡀ',
    'ð':'ᡁ', # originally ɖ͡ʐ
    'θ':'ᡂ', # originally ʈ͡ʂʰ
    ':':'ᡃ',
    'ʒ':'ᡲ', # sibe script
    'z':'ᡯ', # sibe script
    'v':'ᡫ', # sibe fa
    'ɛ':'ᡄ', # todo e
    'ɪ':'ᡅ', # todo i
    'ʌ':'ᡇ',# todo u
    '…':'᠁',
    ',':'᠂',
    '.':'᠃',
    ':':'᠄',
    '-':'᠆',

}
MONGOLIAN_CLEANER = {
    ";":"",
    'ə':"ɵ",
    'ɚ':'ɵr', 
    'æ':'a', 
    'ː':':', 
    'ɑ':'a', 
    'ɐ':'a', 
    'ʔ':'', 
    'ɜ':'er', 
    'ᵻ':'i', 
    'ɔ':'o', 
    'ɾ':'d',
    "!":"",
    "?":"",
        
}
MONGOLIAN_KEEPABLE = frozenset({})

PHAGSPA_IPA = {
    'a':'ꡖ',
    'ʌ':'ꡝ',
    'b':'ꡎ',
    'ð':'ꡫ',
    'd':'ꡊ',
    'd͡z':'ꡒ',
    'd͡ʒ':'ꡆ',
    'ɛ':'ꡠ',
    'e':'ꡦ',
    'f':'ꡤ',
    'g':'ꡂ',
    'h':'ꡜ',
    'i':'ꡞ',
    'j':'ꡗ',
    'j':'ꡨ',
    'k':'ꡀ',
    'k’':'ꡁ',
    'l':'ꡙ',
    'm':'ꡏ',
    'n:':'ꡬ',
    'n':'ꡋ',
    'nj':'ꡇ',
    'ŋ':'ꡃ',
    'o':'ꡡ',
    'p':'ꡌ',
    'p’':'ꡍ',
    'q':'ꡢ',
    'r':'ꡘ',
    's':'ꡛ',
    'ʃ':'ꡚ',
    't:':'ꡩ',
    't':'ꡈ',
    't’':'ꡉ',
    'θ':'ꡪ',
    't͡s’':'ꡑ',
    't͡s':'ꡐ',
    'tsh’':'ꡅ',
    't͡ʃ':'ꡄ',
    'u':'ꡟ',
    'v':'ꡓ',
    'w':'ꡧ',
    'x':'ꡣ',
    'z':'ꡕ',
    'ʒ':'ꡔ',
    'ʔ':'ꡥ',
}
PHAGSPA_CLEANER = {
    ":":"",
    'æ':'a', 
    'ɜ':'er',
    'ɪ':'i', 
    'ɹ':'r', 
    'ː':'', 
    'ɾ':'r', 
    'ɔ':'a', 
    'ʊ':'u', 
    'ɑ':'a', 
    'a':'a',
    'ɐ':'a',
    'ə':'ʌ',
    'ɚ':'er',
    'ᵻ':'i',
    ".":"",
    ",":"",
    ":":"",
    ";":"",
    "!":"",
    "?":"",
}
PHAGSPA_KEEPABLE = frozenset({})

# collect languages into a dict to more programmatically reference
# them later
IPAS = {i.rsplit("_", maxsplit=1,)[0].lower():globals()[i] for i in globals() if i.endswith("_IPA")}
CLEANERS = {i.rsplit("_", maxsplit=1,)[0].lower():globals()[i] for i in globals() if i.endswith("_CLEANER")}
KEEPABLES = {i.rsplit("_", maxsplit=1,)[0].lower():globals()[i] for i in globals() if i.endswith("_KEEPABLE")}
