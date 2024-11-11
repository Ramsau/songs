from defs import *
from songs import Song, CustomPdf


def write_songs():
    p = CustomPdf(format=PAGE_FORMAT)
    songs = Song.ingest_all()

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
    logo_aspect = 1.956852792
    p.image('2A_original_quer_transparent.png',
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
