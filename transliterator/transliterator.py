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
import warnings

from DATA import IPAS, CLEANERS, KEEPABLES

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
    
    return text
    
def main():
    parser = argparse.ArgumentParser(
        # usage="python3 transliterator.py [options]"
    )
    parser.add_argument(
        "--script", 
        "-s", 
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
    parser.add_argument(
        "--show-langs",
        action="store_true",
        help="Print a list of supported languages and exit."
    )
    args = parser.parse_args()

    if args.show_langs:
        print(" ".join(IPAS.keys()))
        exit()

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
        if args.ipa:
            warnings.warn("--script medeival_runes not supported with --ipa.  Please pass raw English text.")
            exit(1)
        text = clean_text(orig.lower(), CLEANERS[args.script])
        print(text)
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
            subprocess.run([args.espeak, "--punct", "-q", "--ipa", "-v", "en-us", i], stdout=subprocess.PIPE).stdout
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
