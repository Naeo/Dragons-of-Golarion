#!/use/bin/python3

"""
CLI Python script to take English input text, generate an IPA
phonetic rendering with eSpeak, and very roughly transliterate 
intoto one of several non-Latin script.  The transcriptions are
meant to be "good enough" for basic flavor text--this is NOT
meant, and is likely not suitable, for serious transliteration
work.

REQUIRES that eSpeak, a free and open source text-to-speech 
synthesizer, be installed, and that the eSpeak executable
be in your system's PATH variable.

REQUIRES Python 3.5 or later

Requires no third-party Python libraries.
"""

import argparse
from copy import deepcopy
import sys
import subprocess

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
    "ʔ":"" # no good glottal stop representation    
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

ELDERFUTHARK_IPA = {
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
ELDERFUTHARK_CLEANER = {
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
ELDERFUTHARK_KEEPABLE = frozenset({';', '!', '?', ':', '.', ','})

MEDEIVALRUNES_IPA = {
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
MEDEIVALRUNES_CLEANER = {
    "j":"i",
}
MEDEIVALRUNES_KEEPABLE = frozenset({';', '!', '?', ':', '.', ','})

# collect languages into a dict to more programmatically reference
# them later
IPAS = {
    "avestan":AVESTAN_IPA,
    "georgian":GEORGIAN_IPA,
    "tifinagh":TIFINAGH_IPA,
    "elder_futhark":ELDERFUTHARK_IPA,
    "medeival_runes":MEDEIVALRUNES_IPA,
}
CLEANERS = {
    "avestan":AVESTAN_CLEANER,
    "georgian":GEORGIAN_CLEANER,
    "tifinagh":TIFINAGH_CLEANER,
    "elder_futhark":ELDERFUTHARK_CLEANER,
    "medeival_runes":MEDEIVALRUNES_CLEANER,
}
KEEPABLES = {
    "avestan":AVESTAN_KEEPABLE,
    "georgian":GEORGIAN_KEEPABLE,
    "tifinagh":TIFINAGH_KEEPABLE,
    "elder_futhark":ELDERFUTHARK_KEEPABLE,
    "medeival_runes":MEDEIVALRUNES_KEEPABLE,
}

def simple_transliterate(text, textdict, keepable):
    """
    A simple .replace()-based transliteration.
    """
    
    keys = textdict.keys()
    # replace long vowels first if applicable
    keys_1 = sorted([i.strip() for i in keys if "ː" in i], key=len, reverse=True)
    keys_2 = sorted([i.strip() for i in keys if "ː" not in i], key=len, reverse=True)

    text_old = text
    for i in keys_1:
        text = text.replace(i, textdict[i])
    for i in keys_2:
        text = text.replace(i, textdict[i])
        
    errs = {
        i 
        for i in set(text_old)
        if i.strip()
        and i in set(text)
        and i not in keepable
    }
    #assert len(errs) == 0, "ERROR: the following characters have no defined mapping: {} \nin\n {}".format(errs, text)
    assert len(errs) == 0, "ERROR: the following characters have no defined mapping: {}".format(errs)
        
    return text

def clean_text(text, cleandict):
    """
    Clean up IPA so it conforms to Avestan characters.
    """
    # FIRST AND FOREMOST: replace lines that are just the explicitly
    # read punctuation.
    text = text.replace("\n dˈɒt\n", ".")
    text=  text.replace("\n pˈiəɹɪəd\n", ".")
    text = text.replace("\n kˈɑːmə\n", ",")
    text = text.replace("\n kˈoʊlən\n", ":")
    text = text.replace("\n sˌɛmɪkˈəʊlən\n", ";")
    text = text.replace("\n sˌɛmɪkˈoʊlən\n", ";")
    text = text.replace("\n kwˈɛstʃən\n", "?")
    text = text.replace("\n ˌɛkskləmˈeɪʃən\n", "!")
    text = text.replace("\n kwˈoʊt\n", "'")
    text = text.replace("\n kwˈoʊts\n", "\"")
    
    text = text.replace("ˌ", "")
    text = text.replace("ˈ", "")
    text = text.replace("̩", "") # syllabic marker
    text = text.replace("ɡ", "g") # IPA 'g', not regualr 'g'--different code point, this one causes trouble a lot

    for i in cleandict: text = text.replace(i, cleandict[i])
    
    text = text.replace("\n", "")
    
    return text
    
def main():
    parser = argparse.ArgumentParser(
        # usage="python3 transliterator.py [options]"
    )
    parser.add_argument(
        "script", 
        # "-s", 
        type=str, 
        metavar="script",
        choices=list(IPAS.keys()),
        help="The script into which to transliterate. Valid options are: {}"\
              .format("'" + "', '".join(IPAS.keys()) + "'")
        
    )
    parser.add_argument(
        "--input", 
        "-i", 
        type=str,
        metavar="input",
        help="File containing raw English text to transliterate.  "
             "If --text is passed, this is raw input instead; if --stdin is passed, "
             "read input from stdin instead."
    )
    parser.add_argument(
        "--outfile", 
        "-o", 
        type=str, 
        metavar="FILENAME",
        help="Optional, file to dump results to.  Defaults to stdout."
    )
    parser.add_argument(
        "--espeak", 
        type=str, 
        metavar="/path/to/eSpeak/executable",
        default="espeak", 
        help="Full path of the location of your eSpeak binary, if it's not in your PATH variable.  Optional."
    )
    parser.add_argument(
        "--text", 
        "-t", 
        action="store_true",
        help="If passed, treat input argument as raw text rather than a filename."
    )
    parser.add_argument(
        "--stdin", 
        action="store_true", 
        help="If passed, read input from stdin.  Useful for piping text from other commands.  Implies --text."
    )
    parser.add_argument(
        "--ipa", 
        action="store_true", 
        help="If passed, the provided text is already in IPA transcribed format and does NOT need to be run through eSpeak."
    )
    args = parser.parse_args()

    # check that eSpeak is installed
    try:
        subprocess.run([args.espeak, "--version"], stdout=subprocess.PIPE)
    except FileNotFoundError:
        print("ERROR!  You must install eSpeak for this to program to "
              "work.  \nIf you have eSpeak installed, make sure you've "
              "added it to your \nsystem's PATH variable, or explicitly "
              "pass the full path to the binary \nwith the --espeak "
              "flag.")
        exit()
    
    # Parse the input text per CLI arguments.
    if args.stdin:
        orig = sys.stdin.read()
    elif args.text:
        orig = args.input
    else:
        orig = open(args.input, "r", encoding="utf8").read()
    
    # Current hacky check for medeival runes, which can be done as
    # a letter-by-letter substitution on the raw text--no eSpeak
    # transcription needed.
    if args.script == "medeival_runes":
        text = clean_text(orig.lower(), CLEANERS[args.script])
        text = simple_transliterate(text.lower(), IPAS[args.script], KEEPABLES[args.script])
        return text, args.outfile
    
    # Split at newlines--eSpeak does line breaks at prosodic boundaries,
    # so doing this lets us preserve the original line breaks.
    orig = [i for i in orig.split('\n') if i.strip()]
    
    # Make a deep copy so we can zip back up later for auto LaTeX formatting
    text = deepcopy(orig)
    
    # use eSpeak to get ipa renderings of text
    if not args.ipa:
        text = [
            subprocess.run([args.espeak, "-q", "--ipa", "-v", "en-us", i], stdout=subprocess.PIPE).stdout
            for i in text
        ]
        text = [str(i, encoding="utf8") for i in text]
    
    # Do the cleaning and transliteration steps, rejoin and return text
    text = [clean_text(i, CLEANERS[args.script]) for i in text]
    text = [simple_transliterate(i, IPAS[args.script], KEEPABLES[args.script]) for i in text]
    text_final = "\n\n".join(i.strip() for i in text)
    
    # for outputting stuff to a .tex file--uses some macros I've defined,
    # so this probably won't work and isn't needed for you.
    # text_final = "\n\n".join("{{{}}}\n&\n{{\\tifinagh {}}} \\\\".format(i.strip(),j.strip()) for i,j in zip(orig, text))
    
    return text_final, args.outfile

if __name__ == "__main__":
    text, outfile = main()
    if outfile:
        with open(outfile, "w", encoding="utf8") as F:
            F.write(text)
    else:
        print(text)
