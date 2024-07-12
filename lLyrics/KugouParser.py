# Parser for Kugou.com

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
import time
import hashlib

import Util


class Parser(object):
    def __init__(self, artist, title, duration):
        self.artist = artist
        self.title = title
        self.duration = duration
        self.lyrics = ""

    def parse(self):
        # remove punctuation from artist/title
        clean_artist = Util.remove_punctuation(self.artist)
        clean_title = Util.remove_punctuation(self.title)
        t_timer  = str(int(time.time()) * 1000)
        t_md5str = "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt" +\
                   "appid=1014" +\
                   "bitrate=0" +\
                   "callback=callback123" +\
                   "clienttime=" + t_timer +\
                   "clientver=1000" +\
                   "dfid=4FHZsU4bHMXq2M8Nj54Khe3A" +\
                   "filter=10" +\
                   "inputtype=0" +\
                   "iscorrection=1" +\
                   "isfuzzy=0" +\
                   "keyword=" + clean_title + " " + clean_artist +\
                   "mid=03f95498d5ee3dacd8b6a38511fbeb01" +\
                   "page=1" +\
                   "pagesize=30" +\
                   "platform=WebFilter" +\
                   "privilege_filter=0" +\
                   "srcappid=2919" +\
                   "token=" +\
                   "userid=0" +\
                   "uuid=03f95498d5ee3dacd8b6a38511fbeb01" +\
                   "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
        md5 = hashlib.md5()  # 创建一个md5对象
        md5.update(t_md5str.encode('utf-8'))  # 使用utf-8编码
        t_signature = md5.hexdigest()
        # 查找曲目
        t_url = "https://complexsearch.kugou.com/v2/search/song?keyword=" + clean_title.replace(' ','+') + "+" + clean_artist.replace(' ','+') + "&callback=callback123&srcappid=2919&clientver=1000&clienttime=" + t_timer + "&mid=03f95498d5ee3dacd8b6a38511fbeb01&uuid=03f95498d5ee3dacd8b6a38511fbeb01&dfid=4FHZsU4bHMXq2M8Nj54Khe3A&page=1&pagesize=30&bitrate=0&isfuzzy=0&inputtype=0&platform=WebFilter&userid=0&iscorrection=1&privilege_filter=0&filter=10&token=&appid=1014&signature=" + t_signature
        t_header = {
                     "Host": "complexsearch.kugou.com",
                     "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
                     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
                     "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                     "DNT": "1",
                     "Connection": "keep-alive",
                     "Cookie": "cct=f4e5bd07;kg_dfid=4FHZsU4bHMXq2M8Nj54Khe3A;kg_dfid_collect=d41d8cd98f00b204e9800998ecf8427e;kg_mid=03f95498d5ee3dacd8b6a38511fbeb01",
                     "Upgrade-Insecure-Requests": "1",
                     "Sec-Fetch-Dest": "document",
                     "Sec-Fetch-Mode": "navigate",
                     "Sec-Fetch-Site": "cross-site",
                     "Priority": "u=0, i",
                     "Pragma": "no-cache",
                     "Cache-Control": "no-cache"
                    }
        print("call kugou.com API(1): " + t_url)
        try:
            request = urllib.request.Request(quote(t_url, safe=':/?=&+_'), headers=t_header)
            response = urllib.request.urlopen(request, None, 3)
            resp = response.read()
        except Exception as e:
            print("could not connect to kugou.com API")
            return ""
        resp = Util.bytes_to_string(resp)
        if resp == "":
            return ""
        elif resp[0:12] != "callback123(":
            return ""
        else:
            resp = resp[12:-2]
        resp = json.loads(resp)
        if len(resp) == 0:
            return ""
        # 分析返回结果，提取歌词
        for songitem in resp["data"]["lists"]:
            t_artist = self.replace_str(songitem["SingerName"].lower())
            t_title = self.replace_str(songitem["SongName"].lower())
            t_second = songitem["Duration"]
            t_music_id = songitem["EMixSongID"]
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
                t_swap_matched = "yes"
            if t_title != '' and m_title != '' and (t_title in m_title or m_title in t_title) and t_artist_sorted == m_artist_sorted and t_diff < 1:
                # 标题有后缀,在艺术家(排序后)及时长完全一致情况下认为是匹配的
                t_info_matched = "yes"
                t_swap_matched = "yes"

            if t_info_matched == "yes":
                t_md5str = "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt" +\
                           "appid=1014" +\
                           "clienttime=" + t_timer +\
                           "clientver=20000" +\
                           "dfid=4FHZsU4bHMXq2M8Nj54Khe3A" +\
                           "encode_album_audio_id=" + t_music_id +\
                           "mid=03f95498d5ee3dacd8b6a38511fbeb01" +\
                           "platid=4" +\
                           "srcappid=2919" +\
                           "token=" +\
                           "userid=0" +\
                           "uuid=03f95498d5ee3dacd8b6a38511fbeb01" +\
                           "NVPh5oo715z5DIWAeQlhMDsWXXQV4hwt"
                md5 = hashlib.md5()  # 重新创建md5对象，防止update方法进行拼接
                md5.update(t_md5str.encode('utf-8'))  # 使用utf-8编码
                t_signature = md5.hexdigest()
                # 提取歌曲信息及歌词
                t_url = "https://wwwapi.kugou.com/play/songinfo?srcappid=2919&clientver=20000&clienttime=" + t_timer + "&mid=03f95498d5ee3dacd8b6a38511fbeb01&uuid=03f95498d5ee3dacd8b6a38511fbeb01&dfid=4FHZsU4bHMXq2M8Nj54Khe3A&appid=1014&platid=4&encode_album_audio_id=" + t_music_id + "&token=&userid=0&signature=" + t_signature
                t_header = {
                             "Host": "wwwapi.kugou.com",
                             "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
                             "Accept": "*/*",
                             "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
                             "Origin": "https://www.kugou.com",
                             "DNT": "1",
                             "Connection": "keep-alive",
                             "Referer": "https://www.kugou.com/",
                             "Sec-Fetch-Dest": "empty",
                             "Sec-Fetch-Mode": "cors",
                             "Sec-Fetch-Site": "same-site",
                             "Priority": "u=0",
                             "Pragma": "no-cache",
                             "Cache-Control": "no-cache",
                             "TE": "trailers"
                            }
                print("call kugou.com API(2): " + t_url)
                try:
                    request = urllib.request.Request(t_url, headers=t_header)
                    response = urllib.request.urlopen(request, None, 3)
                    resp = response.read()
                except Exception as e:
                    print("could not connect to kugou.com API")
                    return ""
                resp = Util.bytes_to_string(resp)
                if resp == "":
                    return ""
                resp = json.loads(resp)
                if len(resp) == 0:
                    return ""

                t_artist = resp["data"]["author_name"].lower()
                t_title = resp["data"]["song_name"].lower()
                if t_title == "":
                    # 对 song_name 为空的情况容错
                    t_title = resp["data"]["audio_name"].lower()
                if t_title != m_title or t_artist != m_artist:
                    # 对多个艺术家进行排序并转小写
                    if t_title != "" and m_title != "" and (t_title in m_title or m_title in t_title) and t_artist_sorted == m_artist_sorted and t_diff < 1:
                        # 标题有后缀,在艺术家(排序后)及时长完全一致情况下认为是匹配的
                        print("验证“" + self.artist + " - " + self.title + "”音乐信息时发现轻微匹配瑕疵（JSON:" + t_artist + " - " + t_title + "），已按匹配处理")
                    elif (t_title == "null" or t_title == "") and (t_artist == "null" or t_artist == "") and t_diff < 1:
                        # 标题和艺术家均为null，但时长一致，认为是匹配的
                        print("验证“" + self.artist + " - " + self.title + "”音乐信息时发现轻微匹配瑕疵（JSON:" + t_artist + " - " + t_title + "），已按匹配处理")
                    else:
                        # print("验证“" + artist + " - " + title + "”音乐信息时发现不匹配（JSON:" + t_artist + " - " + t_title + "），将继续尝试匹配")
                        continue
                if resp["data"]["lyrics"] != "":
                    self.lyrics = string.capwords(resp["data"]["lyrics"], "\n").strip()
                    break
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


