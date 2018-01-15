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
from collections import deque
import re
import sys
import subprocess

from DATA import IPAS, CLEANERS, KEEPABLES

class Transliterator:
    """
    Abstract class for transforming input text using a user-provided mapping.
    This version does a replacement-based approach to phonetic scripts, and
    should be suitable for alphabetic scripts with nearly one-to-one ratios
    of phonemes-to-graphemes.
    """

    def __init__(self, ipa_dict, cleaner_dict, keepable_set):
        """
        :param ipa_dict: dictionary to map IPA characters to characters in the script.
        :param cleaner_dict: dictionary to map IPA characters to other IPA characters.
        :param keepable_set: set or frozenset of characters that do not need changing.
        """
        self.ipa = ipa_dict
        self.cleaner = cleaner_dict
        self.keepable = keepable_set
        self.text = ""

    def espeak(self, text, espeak="espeak"):
        """
        Convert some text with eSpeak.
        :param text: string; raw English text to convert.
        :param espeak: string; path to eSpeak executable, or command-line
            command to run for eSpeak.
        :return: list of IPA strings, with one string
        """
        # Split at newlines--eSpeak does line breaks at prosodic boundaries,
        # so doing this lets us preserve the original line breaks.
        text = [i.strip() for i in text.split('\n')]
        # Convert to ipa with eSpeak
        text = [
            subprocess.run([espeak, "--punct", "-q", "--ipa", "-v", "en-us", i], stdout=subprocess.PIPE).stdout
            for i in text
        ]
        text = [str(i.strip(), encoding="utf8") for i in text]

        return text

    def preprocess_text(self, text):
        """
        Perform basic preprocessing on some text.

        Replaces eSpeak's reading of punctuation with actual punctuation,
        strip stress marks, syllabic N/R marks, and replace the IPA 'g' with the
        Latin 'g'--they're different code points, and 'g' was one that seemed to
        commonly alternate between IPA and Latin encoding in my sources.

        :param text: text to preprocess
        :return: cleaned text
        """
        # Punctuation
        text = text.replace("\n dˈɒt", ".")
        text = text.replace("\n pˈiəɹɪəd", ".")
        text = text.replace("\n kˈɑːmə", ",")
        text = text.replace("\n kˈoʊlən", ":")
        text = text.replace("\n sˌɛmɪkˈəʊlən", ";")
        text = text.replace("\n sˌɛmɪkˈoʊlən", ";")
        text = text.replace("\n kwˈɛstʃən", "?")
        text = text.replace("\n ɛkskləmˈeɪʃən", "!")
        text = text.replace("\n kwˈoʊt", "'")
        text = text.replace("\n kwˈoʊts", "\"")
        text = text.replace("\n bˈækslæʃ", "\\")
        # miscellaneous symbols
        text = text.replace("ˌ", "") # secondary stress
        text = text.replace("ˈ", "") # primary stress
        text = text.replace("̩", "") # syllabic marker
        text = text.replace("ɡ", "g") # IPA 'g' to Latin 'g'
        # Lastly, replace any newline characters with spaces--newlines
        # were from eSpeak splitting at prosodic bounds.
        text = text.replace("\r", "")
        text = text.replace("\n", "")

        return text

    def convert_text(self, text, is_ipa=False):
        """
        A simple .replace()-based transliteration.
        Expects a single IPA string input.

        :param text: string; IPA text to transliterate.
        """
        # Run the cleaner on the text
        for i in sorted(self.cleaner, key=len, reverse=True):
            text = text.replace(i, self.cleaner[i])

        # replace long vowels first if applicable
        keys_1 = sorted(
            [i.strip() for i in self.ipa.keys() if "ː" in i],
            key=len,
            reverse=True
        )
        keys_2 = sorted(
            [i.strip() for i in self.ipa.keys() if "ː" not in i],
            key=len,
            reverse=True
        )

        text_old = text
        for i in keys_1:
            text = text.replace(i, self.ipa[i])
        for i in keys_2:
            text = text.replace(i, self.ipa[i])

        errs = {
            i
            for i in set(text_old)
            if i.strip()
               and i in set(text)
               and i not in self.keepable
        }
        # assert len(errs) == 0, "ERROR: the following characters have no defined mapping: {} \nin\n {}".format(errs, text)
        assert len(errs) == 0, "ERROR: the following characters have no defined mapping: {}".format(errs)

        return text

    def transliterate(self, text, espeak="espeak", is_ipa=False):
        if not is_ipa: 
            text = self.espeak(text, espeak)
            text = map(self.preprocess_text, text)
            text = map(self.convert_text, text)
            text = "\n".join(text)
        else:
            text = self.preprocess_text(text)
            text = self.convert_text(text)
        return text

class MedeivalRunes(Transliterator):
    """
    Special class for medeival runes transliteration--skip all the IPA nonsense
    and convert directly from the raw text, since there's a 1:1 mapping of those
    runes to the original Latin characters.
    """

    def transliterate(self, text, espeak="espeak", is_ipa=False):
        return self.convert_text(text.lower())

class CanadianSyllabics(Transliterator):
    """
    Special class for working with Canadian Aboriginal Syllabics.
    Accumulates phonemes in a buffer, clearing the buffer and ouputting
    the corresponding transliterated text once adding a character results
    in a string that does not map to any valid grapheme.
    
    This also allows a default script to be specified, e.g. "blackfoot"
    for Blackfoot syllabics.  It attempts to do the transliteration
    using that script first, falling back to the general syllabics
    if it doesn't find a valid character.
    """
    
    def convert_text(self, text, is_ipa=False, script="GENERAL"):
        # Run the cleaner on the text
        for i in sorted(self.cleaner, key=len, reverse=True):
            text = text.replace(i, self.cleaner[i])
        
        out = ""
        buffer = ""
        MAXLEN = max(len(i) for i in self.ipa.keys())
        for i in text:
            buffer += i
            if buffer not in self.ipa:
                out += self.ipa[buffer[:-1]]
                buffer = ""
            if len(buffer) > MAXLEN:
                raise ValueError("buffer size has grown too large.  Current contents: {}".format(buffer))
        
        return out

def main():
    TRANSLITERATORS = {
        i:Transliterator(IPAS[i], CLEANERS[i], KEEPABLES[i])
        for i in IPAS
    }

    # Overwrite the Medeival Runes one
    TRANSLITERATORS["medeival_runes"] = MedeivalRunes(
        IPAS["medeival_runes"], CLEANERS["medeival_runes"], KEEPABLES["medeival_runes"],
    )

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--script",
        "-s",
        type=str,
        metavar="script",
        choices=list(IPAS.keys()),
        help="The script into which to transliterate. Valid options are: {}" \
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

    # Make a deep copy so we can zip back up later for auto LaTeX formatting
    text = deepcopy(orig)
    text_final = TRANSLITERATORS[args.script].transliterate(text, args.espeak, args.ipa)

    # for outputting stuff to a .tex file--uses some macros I've defined,
    # so this probably won't work and isn't needed for you.
    text_final ="\\begin{longtable}{p{7.5cm} p{7.5cm}}\n\tENGLISH & TIFINAGH\\\\\n\n" \
        + "\n\n".join(
            "\t{{{}}}\n\t&\n\t{{{}}} \\\\".format(i.strip(),j.strip()) 
            for i,j in zip(orig.split('\n')[:-1], text_final.split('\n')[:-1])
        ) \
        + "\n\\end{longtable}"
        
    if args.outfile:
        with open(args.outfile, "w", encoding="utf8") as F:
            F.write(text_final)
    else:
        print(text_final)

    return text_final, args.outfile


if __name__ == "__main__":
    T = main()
    # text, outfile = main()
