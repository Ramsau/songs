from songs import Song


def write_songs():
    website = open("web/index.html", "w")
    songs = Song.ingest_all(numbering="numbers")


    website.write('''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style type="text/css">
        html {
            font-family: "Arial";
            font-size: 30pt;
        }
        span.line-segment {
            display: inline-flex;
            flex-direction: column;
        }
        
        span.text {
          white-space: pre;
        }
        
        span.text:empty::before {
            content: " ";
        }
        
        span.chord {
            margin-right: 0.5em;
        }
        
        div.line {
            display: flex;
            align-items: end;
        }
        
        a {
            color: black;
        }
        
        .song-title {
            margin-top: 50pt;
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
