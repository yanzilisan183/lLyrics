# -*- coding: utf-8 -*-
# Parser for MediaFile ID3v2 USLT tags.
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
import re
import string
import Util
try:
    import mutagen
except:
    print("Python3 mutagen package not found.\nPlease run `pip install mutagen` first.")
    exit()


class Parser(object):
    def __init__(self, artist, title, *, duration=0, location=""):
        self.artist = artist
        self.title = title
        self.location = location
        self.lyrics = ""

    def parse(self):
        location = self.location
        if location.find("file:///") != 0:
            return ""
        else:
            location = str(urllib.parse.unquote(location))[7:]
            print("Scan local media file: " + location)
        tags = self.read_id3v2_tags(location)
        if tags:
            lyrics = ""
            for key in tags:
                if key[:5] == "USLT:":
                    self.lyrics = str(tags[key])
                    break
        else:
            print("No ID3v2 tags found.")
            return ""

        self.artist = self.artist.replace("+", ",")
        clean_artist = Util.remove_punctuation(self.artist)
        clean_title = Util.remove_punctuation(self.title)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()
        return self.lyrics

    def read_id3v2_tags(self, file_path):
        audio = mutagen.File(file_path, easy=False)
        if audio is not None:
            return audio
        else:
            return None

