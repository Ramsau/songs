from songs import Song
import shutil


def write_songs():
    shutil.copyfile("web_src/script.js", "web/script.js")
    website_in = open("web_src/index.html", "r", encoding='utf-8')
    website = open("web/index.html", "w", encoding='utf-8')
    songs = Song.ingest_all(numbering="numbers")

    for line in website_in:
        if line == "<% Index %>\n":
            for song in songs:
                song.write_website_header(website)
        elif line == "<% Songs %>\n":
            for song in songs:
                song.write_website(website)
        else:
            website.write(line)



if __name__ == '__main__':
    write_songs()
