import os

import xmltodict
from typing import Dict, List, OrderedDict

import re
from defs import *


TITLE_TRANS = [
    ("c", "Refrain"),
    ("b", "Bridge"),
    ("v", "Strophe"),
]

class Verse:
    text: str
    descriptor: str

    def __init__(self, descriptor: str, text: str):
        self.text = text
        self.descriptor = descriptor

    def __init__(self, dict: OrderedDict):
        self.descriptor = dict["@name"]
        raw_text = dict["lines"]

        if isinstance(raw_text, OrderedDict):
            self.text = raw_text["#text"]

        # in case of additional lines
        elif isinstance(raw_text, List):
            self.text = ""
            for part in raw_text:
                if isinstance(part, OrderedDict):
                    self.text += part["#text"]
                else:
                    self.text += part
                self.text += "\n"

        elif isinstance(raw_text, str):
            self.text = raw_text

        elif raw_text is None:
            raise ValueError("Verse has no Text")

        else:
            raise NotImplemented("Unable to parse Verse")

        # remove blank lines
        self.text = re.sub("\n\s*\n", "\n", self.text)
        # remove last \n
        if self.text[-1] == "\n":
            self.text = self.text[:-1]


class Song:
    dict: Dict

    def __init__(self, path: str):
        file = open(path, "r")
        text = file.read(-1)
        file.close()

        # remove tags definitions
        text = "".join(re.split("<tags[\s\S]*</tags>", text))

        # replace chord tag
        text = re.sub(
            '<tag name="c">[\s\S]*?</tag>',
            lambda m: CHORD_START + m.string[m.span()[0] + 14:-6 + m.span()[1]] + CHORD_END,
            text
        )

        # remove tags
        text = re.sub(
            '<tag[\s\S]*?</tag>',
            lambda m: m.string[m.span()[0] + 14:-6 + m.span()[1]],
            text
        )

        # replace linebreak
        text = text.replace("<br/>", "\n")

        # replace weird apostrophe
        text = text.replace('’', "'")

        # replace ][ (separator for closely adjacent chords)
        # text = text.replace("][", " ++")

        # parse
        self.dict = xmltodict.parse(text)

    def get_properties(self) -> OrderedDict:
        return self.dict["song"]["properties"]

    def get_authors(self) -> List[str]:
        return self.get_properties()["authors"]["author"]

    def get_verses(self) -> List[Verse]:
        verseDict = self.dict["song"]["lyrics"]["verse"]
        try:
            verseDict[0]
        except KeyError:
            # only one verse: put into list
            verseDict = [verseDict]

        verses = []
        for entry in verseDict:
            try:
                verses.append(Verse(entry))
            except ValueError:
                # don't add empty verse
                pass

        # parse verse names
        verse_names = [v.descriptor for v in verses]
        for i in range(len(verses)):
            for token, translation in TITLE_TRANS:
                if re.match(token + "[0-9]+", verse_names[i]):
                    verse_names[i] = translation

        # number duplicates
        for i in range(len(verses)):
            duplicate = False
            number = 2
            for ii in range(i + 1, len(verses)):
                if verse_names[ii] == verse_names[i]:
                    duplicate = True
                    verse_names[ii] += " " + str(number)
                    number += 1

            if duplicate:
                verse_names[i] += " 1"

        # apply rename
        for i in range(len(verses)):
            verses[i].descriptor = verse_names[i]

        return verses

    def get_title(self) -> str:
        return self.get_properties()["titles"]["title"].replace("/", "_")

    def write(self, path: str):
        file = open(path, "w+")
        for verse in self.get_verses():
            if (verse.descriptor and verse.text):
                file.write(VERSE_START + verse.descriptor + VERSE_END + '\n')
                file.write(verse.text + "\n")
        file.close()


if __name__ == "__main__":
    for path in os.listdir("chorded"):
        song = Song("chorded/" + path)
        song.write("crd/" + song.get_title() + ".txt")
