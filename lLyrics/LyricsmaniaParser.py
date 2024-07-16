# Parser for lyricsmania.com (fix at 13:42 2024-07-16 by LI YunFei <yanzilisan183@sina.com>)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib.request, urllib.error, urllib.parse
import string

import Util


class Parser(object):
    def __init__(self, artist, title):
        self.artist = artist
        self.title = title
        self.lyrics = ""

    def parse(self):
        # remove unwanted characters from artist and title strings
        clean_artist = self.artist.replace("+", "and")
        clean_artist = Util.remove_punctuation(clean_artist)
        clean_artist = clean_artist.replace(" ", "_")

        clean_title = self.title
        clean_title = Util.remove_punctuation(clean_title)
        clean_title = clean_title.replace(" ", "_")

        # create lyrics Url
        url = "http://www.lyricsmania.com/" + clean_title + "_lyrics_" + clean_artist + ".html"
        print("lyricsmania Url " + url)
        try:
            resp = urllib.request.urlopen(url, None, 3).read()
        except:
            print("could not connect to lyricsmania.com")
            return ""

        resp = Util.bytes_to_string(resp)
        self.lyrics = self.get_lyrics(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()

        return self.lyrics

    def get_lyrics(self, resp):
        # cut HTML source to relevant part
        start_keywords = ["<div class=\"lyrics-body\">\n", "class=\"play-video\"></a>\n</div>"]
        finded_keyword = False
        for keyword in start_keywords:
            start = resp.find(keyword)
            if start > -1:
                finded_keyword = True
                resp = resp[(start + len(keyword)):]
        if finded_keyword == False:
            print("lyrics start not found")
            return ""
        
        end = resp.find("</div>")
        if end == -1:
            print("lyrics end not found ")
            return ""
        resp = resp[:end]

        # replace unwanted parts
        resp = resp.replace("\n", "")
        resp = resp.replace("<br>", "\n")
        resp = resp.replace("<br/>", "\n")
        resp = resp.replace("<br />", "\n")
        resp = resp.replace("\n\n", "\n")
        resp = resp.replace("<div class=\"p402_premium\">", "")
        resp = resp.replace("<div class=\"fb-quotable\">", "")
        print(resp)

        resp = "\n".join(line.strip() for line in resp.split("\n"))

        return resp
