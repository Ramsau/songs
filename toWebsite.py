from songs import Song


def write_songs():
    website = open("web/Liedermappe.html", "w")
    songs = Song.ingest_all(numbering="numbers")


    website.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <ref rel="stylesheet" href="/songs/web/Liedermappe.css">
    <style type="text/css">
        span.line-segment {
            display: inline-flex;
            flex-direction: column;
        }
        
        
        div.line {
            display: flex;
            align-items: end;
        }
    </style>
</head>
<body>
<h1 id="Index">Index</h1>
''')

    for song in songs:
        song.write_website_header(website)

    for song in songs:
        song.write_website(website)

    website.write('''</body>
</html>''')

if __name__ == '__main__':
    write_songs()
