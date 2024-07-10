# -*- coding: utf-8 -*-
# Parser for LocalSameFolder
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
import pprint   # by san

from html.parser import HTMLParser

import Util


class Parser(object):
    def __init__(self, artist, title, location):
        self.artist = artist
        self.title = title
        self.location = location
        self.lyrics = ""

    def parse(self):
        if self.location.find("file:///") != 0:
            return ""
        lrc_location = re.sub(r"\.[^\.]*$", ".lrc", self.location)
        if lrc_location == self.location:
            return ""
        self.artist = self.artist.replace("+", "and")
        clean_artist = Util.remove_punctuation(self.artist)
        clean_title = Util.remove_punctuation(self.title)

        try:
            resp = urllib.request.urlopen(Util.add_request_header(lrc_location), None, 3).read()
        except:
            print("could not open local lrc file.")
            return ""
        self.lyrics = Util.bytes_to_string(resp)
        self.lyrics = string.capwords(self.lyrics, "\n").strip()

        return self.lyrics

