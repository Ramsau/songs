import fpdf
from typing import List
import os
from defs import *
import re


class TextPiece:
    is_chord: bool
    text: str

    def __init__(self, text, is_chord):
        self.is_chord = is_chord
        self.text = text

    def __str__(self):
        return ("[%s]" if self.is_chord else "%s") % self.text


class Line:
    text_pieces: List[TextPiece]

    def __init__(self, text: str):
        self.text_pieces = []
        current_is_chord = False
        for piece in text.split(CHORD_START):
            subpieces = piece.split(CHORD_END)
            for subpiece in subpieces:
                self.text_pieces.append(TextPiece(subpiece, current_is_chord))

                current_is_chord = not current_is_chord

    def __str__(self):
        return self.get_text()

    def get_text(self):
        return "".join([_.text if not _.is_chord else ''
                        for _ in self.text_pieces])

    def has_chords(self):
        for piece in self.text_pieces:
            if piece.is_chord:
                return True
        return False

    def write_pdf(self, p: fpdf.FPDF):
        if self.has_chords():
            x_last_word = p.x
            for piece in self.text_pieces:
                if piece.is_chord:
                    p.write(LINE_SPACING, piece.text)
                else:
                    x_last_word += p.get_string_width(piece.text)
                    p.set_x(max(p.x + p.get_string_width("_"), x_last_word))

            p.write(LINE_SPACING, "\n")
            p.write(CHORD_PADDING, "\n")

        p.write(LINE_SPACING,
                self.get_text() + "\n")

    def pdf_height(self) -> float:
        height = LINE_SPACING
        if self.has_chords():
            height += LINE_SPACING + CHORD_PADDING

        return height


class Verse:
    description: str
    lines: List[Line] = []

    def __init__(self, description: str, text: str):
        self.description = description

        # for textline in text.split("\n"):
        #     if textline:
        #         self.lines.append(Line(textline))
        self.lines = []
        for textline in text.split("\n"):
            if textline:
                self.lines.append(Line(textline))

    def __str__(self):
        return self.description

    def write_pdf(self, p: fpdf.FPDF):
        if self.description != NOTE_NAME:
            p.set_font("Arial", size=FONT_SIZE, style="B")
            p.write(LINE_SPACING + VERSE_PADDING * 2, txt=self.description + "\n")
            p.set_y(p.y - 4)

            p.set_font("Arial", size=FONT_SIZE)
        else:
            p.set_font("Arial", size=FONT_SIZE_NOTE)

        for line in self.lines:
            line.write_pdf(p)

    def pdf_height(self) -> float:
        height = LINE_SPACING + VERSE_PADDING
        for line in self.lines:
            height += line.pdf_height()

        return height


class Song:
    title: str
    verses: List[Verse] = []
    first_letter: str = None
    number: int = None
    page_number: int = None

    def __init__(self, title: str, text: str, first_letter: str, number: int):
        self.title = title
        self.first_letter = first_letter
        self.number = number

        raw_verses = text.split(VERSE_START)
        # discard info before first verse
        raw_verses = raw_verses[1:]

        self.verses = []
        for raw_verse in raw_verses:
            if not raw_verse:
                continue
            parts = raw_verse.split(VERSE_END + '\n', 1)
            assert(len(parts) == 2)
            self.verses.append(Verse(parts[0], parts[1]))

    @classmethod
    def from_file(cls, path: str, number: int):
        file = open(path)
        text = file.read()
        text = text.split('\n\n\n')[0]\
            .replace('’', "'")
        text = re.sub(r" +- +", "", text)
        text = re.sub(r" +", " ", text)

        file.close()
        # get filename, remove extension
        title = ".".join(os.path.basename(path).split(".")[:-1])

        first_letter = title[:1].upper()
        if not first_letter.isalpha():
            first_letter = '#'

        return Song(title, text, first_letter, number)

    def __str__(self):
        return self.title

    def write_pdf(self, p: fpdf.FPDF, even_pages=EVEN_PAGES):
        # setup new page
        p.add_page()

        # skip a page to keep songs on one double-page
        if even_pages and p.page_no() != self.page_number:
            p.currentSongId = ''
            p.add_page()

        p.currentSongId = self.first_letter + str(self.number)

        p.set_font("Arial", size=FONT_SIZE_TITLE, style="B")

        # write title
        p.write(10, txt=("%s%d. " % (self.first_letter, self.number) if self.number else "") + self.title + "\n")

        # write verses
        for verse in self.verses:
            if (p.y + verse.pdf_height() > p.h - p.b_margin):
                p.add_page()

            verse.write_pdf(p)

    def pdf_height(self) -> float:
        height = FONT_SIZE_TITLE

        for verse in self.verses:
            height += verse.pdf_height()

        return height

    def pdf_pages(self, page_height, top_margin) -> int:
        test_pdf = CustomPdf(format=PAGE_FORMAT, block_footers=True)
        self.write_pdf(test_pdf, even_pages=False)
        return test_pdf.page_no()


class CustomPdf(fpdf.FPDF):
    currentSongId = ''
    page_nr = 1

    def __init__(self, *args, block_footers=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.block_footers = block_footers
        self.l_margin = SIDE_MARGIN
        self.r_margin = SIDE_MARGIN

    def footer(self):
        if self.block_footers:
            return

        if PAGE_FOOTERS == "numbers":
            footer = str(self.page_no())

            # don't add page no on title page
            if self.page_no() <= 1:
                return
        elif PAGE_FOOTERS == "identifiers":
            footer = self.currentSongId
        else:
            return

        prev_style = self.font_style
        prev_family = self.font_family
        prev_size = self.font_size

        self.set_font("Arial", size=FONT_SIZE, style="")
        self.set_y(-15)
        self.set_x(self.w / 2 - self.get_string_width(footer))
        self.write(10, footer)
        self.page_nr += 1

        self.set_font(prev_family, prev_style, prev_size)

def write_songs():
    p = CustomPdf(format=PAGE_FORMAT)
    num = 0
    songs = []
    dir = "crd"

    with open("index.txt") as f:
        names = f.readlines()

    pathlist = [name.replace('\n', '.txt') for name in names if not name.startswith('#')]

    lastLetter = ''
    for path in pathlist:
        first_letter = path[:1].upper()
        if not first_letter.isalpha():
            first_letter = '#'
        if lastLetter == first_letter:
            num += 1
        else:
            num = 1
        lastLetter = first_letter

        new_song = Song.from_file(dir + "/" + path,
                                  number=num)
        songs.append(new_song)

    # figure out song's page numbers
    current_page = INDEX_PAGES + 2
    for song in songs:
        song_pages = song.pdf_pages(p.h - p.b_margin, p.b_margin)
        if EVEN_PAGES and song_pages > 1 and current_page % 2:
            current_page += 1
        song.page_number = current_page
        current_page += song_pages

    # title card
    p.set_font("Arial", size=22, style="B")
    p.add_page()
    image_size = 130
    image_offset = -30
    p.image('baustoi_logo.png',
            (p.w - image_size) / 2,
            (p.h - image_size) / 2 + image_offset,
            image_size, image_size)
    p.set_y((p.h + image_size) / 2 + image_offset - 10)
    p.set_x((p.w - p.get_string_width("Jugendkreis-Liedermappe")) / 2)
    p.write(LINE_SPACING + 2, "Jugendkreis-Liedermappe")
    logo_height = 40
    logo_aspect = 1.1214
    p.image('logo inv.jpg',
            (p.w - logo_height * logo_aspect) / 2,
            (p.h - logo_height + image_size + LINE_SPACING) /2,
            logo_height * logo_aspect, logo_height)


    # index
    p.add_page()
    for song in songs:
        link = p.add_link()
        p.set_link(link, page=song.page_number)

        p.set_font("Arial", size=FONT_SIZE, style="B")
        p.write(LINE_SPACING + 2, "%s%d. " % (song.first_letter, song.number), link=link)
        p.set_font("Arial", size=FONT_SIZE)
        p.write(LINE_SPACING + 2, song.title, link=link)

        if INDEX_SHOW_PAGENR:
            line_start = p.x + 1
            string_width = p.get_string_width(str(song.page_number))
            p.set_x(p.w - string_width - 18)
            p.write(LINE_SPACING + 2, str(song.page_number), link=link)
            p.dashed_line(line_start, p.y + LINE_SPACING, p.x  - string_width, p.y + LINE_SPACING, .1, 2)


        p.write(LINE_SPACING + 2, "\n")

    # songs
    for song in songs:
        song.write_pdf(p)

    p.output("Liedermappe.pdf")


if __name__ == '__main__':
    write_songs()
