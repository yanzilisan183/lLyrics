# Parser for NeteaseCloudMusic(music.163.com)

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

import urllib.request
from urllib.parse import quote
import json
import string

import Util


class Parser(object):
    def __init__(self, artist, title, *, duration=0, location=""):
        self.artist = artist
        self.title = title
        self.duration = duration
        self.lyrics = ""

    def parse(self):
        self.lyrics = ""
        # remove punctuation from artist/title
        clean_artist = Util.remove_punctuation(self.artist)
        clean_title = Util.remove_punctuation(self.title)
        # 查找曲目
        t_url = "https://music.163.com/api/search/get/web?csrf_token=hlpretag=&hlposttag=&s=" +\
                clean_title.replace(' ','+') + "&type=1&offset=0&total=true&limit=30"
        t_header = {
                     "Host": "music.163.com",
                     "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp," +\
                               "image/png,image/svg+xml,*/*;q=0.8",
                     "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                     "DNT": "1",
                     "Connection": "keep-alive",
                     "Upgrade-Insecure-Requests": "1",
                     "Sec-Fetch-Dest": "document",
                     "Sec-Fetch-Mode": "navigate",
                     "Sec-Fetch-Site": "cross-site",
                     "Priority": "u=0, i",
                     "Pragma": "no-cache",
                     "Cache-Control": "no-cache"
                    }
        print("call music.163.com API(1): " + t_url)
        try:
            request = urllib.request.Request(quote(t_url, safe=':/?=&+_'), headers=t_header)
            response = urllib.request.urlopen(request, None, 3)
            resp = response.read()
        except Exception as e:
            print("could not connect to music.163.com API")
            return ""
        resp = Util.bytes_to_string(resp)
        if resp == "":
            return ""
        resp = json.loads(resp)
        if len(resp) == 0:
            return ""
        # 分析返回结果，提取歌词
        for songitem in resp["result"]["songs"]:
            t_title = self.replace_str(songitem["name"].lower())
            t_artist = ""
            for artistitem in songitem["artists"]:
                t_artist += "," + self.replace_str(artistitem["name"].lower())
            if t_artist != "":
                t_artist = t_artist[1:]
            t_second = int(songitem["duration"] / 1000)
            t_music_id = str(songitem["id"])
            t_arr = t_artist.split(',')
            t_arr.sort()
            t_artist_sorted = ','.join(t_arr)
            m_artist = self.replace_str(self.artist.lower())
            m_title = self.replace_str(self.title.lower())
            t_arr = m_artist.split(',')
            t_arr.sort()
            m_artist_sorted = ','.join(t_arr)
            t_diff = abs(self.duration - t_second)
            t_info_matched = "no"
            t_swap_matched = "no"
            if t_title == m_title and t_artist == m_artist and t_diff < 5:
                # 信息一致,时差小于5,认为是匹配的
                t_info_matched = "yes"
            elif t_title == m_artist and t_artist == m_title and t_diff < 1:
                # 发现交叉配配,设置标记
                t_info_matched = "yes"
                t_swap_matched = "yes"
            if t_title != '' and m_title != '' and (t_title in m_title or m_title in t_title) and \
               t_artist_sorted == m_artist_sorted and t_diff < 1:
                # 标题有后缀,在艺术家(排序后)及时长完全一致情况下认为是匹配的
                t_info_matched = "yes"
                t_swap_matched = "yes"

            if t_info_matched == "yes":
                # 提取歌曲信息及歌词
                t_url = "http://music.163.com/api/song/lyric?os=pc&id=" + t_music_id + "&lv=-1&kv=-1&tv=-1"
                t_header = {
                             "Host": "music.163.com",
                             "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 " +\
                                           "Firefox/128.0",
                             "Accept": "*/*",
                             "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                             "DNT": "1",
                             "Connection": "keep-alive",
                             "Sec-Fetch-Dest": "empty",
                             "Sec-Fetch-Mode": "cors",
                             "Sec-Fetch-Site": "same-site",
                             "Priority": "u=0",
                             "Pragma": "no-cache",
                             "Cache-Control": "no-cache",
                             "TE": "trailers"
                            }
                print("call music.163.com API(2): " + t_url)
                try:
                    request = urllib.request.Request(t_url, headers=t_header)
                    response = urllib.request.urlopen(request, None, 3)
                    resp = response.read()
                except Exception as e:
                    print("could not connect to music.163.com API")
                    return ""
                resp = Util.bytes_to_string(resp)
                if resp == "":
                    return ""
                resp = json.loads(resp)
                if len(resp) == 0:
                    return ""
                elif resp["lrc"] and resp["lrc"]["lyric"] and resp["lrc"]["lyric"] != "":
                    self.lyrics = string.capwords(resp["lrc"]["lyric"], "\n").strip()
                    return self.lyrics
                elif resp["lrc"] and resp["lrc"]["lyric"] and resp["lrc"]["lyric"] != "":
                    self.lyrics = string.capwords(resp["lrc"]["lyric"], "\n").strip()
                    return self.lyrics
        return self.lyrics

    def replace_str(self, string):
        # 将影响匹配的符号进行统一替换
        t_var = string
        t_var = t_var.replace(' ', '')
        t_var = t_var.replace('　', '')
        t_var = t_var.replace('！', '')
        t_var = t_var.replace('\!', '')
        t_var = t_var.replace('：', '')
        t_var = t_var.replace(':', '')
        t_var = t_var.replace('_', '')
        t_var = t_var.replace('@', '')
        t_var = t_var.replace('&', ',')
        t_var = t_var.replace('、', ',')
        t_var = t_var.replace('＆', ',')
        t_var = t_var.replace('[', '（')
        t_var = t_var.replace(']', '）')
        t_var = t_var.replace('(', '（')
        t_var = t_var.replace(')', '）')
        return t_var


