import urllib2
import xml.dom.minidom as minidom

import multiprocessing.pool
import collections

import sys
import os
import math

GIGAPAN_URL = "http://www.gigapan.org"

Tile = collections.namedtuple('Tile', ['url', 'filename', 'number', 'total_tiles'])

# class Tile:
#     def __init__(self, url, filename):
#         self.url = url
#         self.filename = filename

class Gigapan:
    def __init__(self, image_id):
        self.image_id = image_id
        self.kml = None

        self.level = None
        self.num_height_tiles = None
        self.num_width_tiles = None

        self.parse_kml()

    def parse_kml(self):
        response = urllib2.urlopen(GIGAPAN_URL +
                                   "/gigapans/{0}.kml".format(self.image_id))
        self.kml = minidom.parseString(response.read())

        max_height = self.get_node_val('maxHeight')
        max_width = self.get_node_val('maxWidth')
        tile_size = self.get_node_val('tileSize')

        max_level = int(math.ceil(math.log(
            max(math.ceil(max_width / tile_size),
                math.ceil(max_height / tile_size)), 2)))

        self.level = max_level
        self.num_height_tiles = int(math.ceil(max_height / tile_size)) + 1
        self.num_width_tiles = int(math.ceil(max_width / tile_size)) + 1

        total_tiles = self.num_height_tiles * self.num_width_tiles

        print "Max Height: {}".format(max_height)
        print "Max Width : {}".format(max_width)
        print "Max Size  : {}".format(max_height)
        print "Tile Size : {}".format(tile_size)
        print "# of Tiles: {}".format(self.num_height_tiles *
                                      self.num_width_tiles)
        print "Max Level : {}".format(max_level)

    def get_node_val(self, tag_name):
        return int(self.kml.getElementsByTagName(tag_name).item(0)
                   .firstChild.nodeValue)

    def get_tiles(self):
        tiles = []
        number = 0
        for h in range(self.num_height_tiles):
            for w in range(self.num_width_tiles):
                url = GIGAPAN_URL + "/get_ge_tile/{0}/{1}/{2}/{3}"\
                    .format(self.image_id, self.level, h, w)
                filename = str(self.image_id) + "/{0}-{1}.jpg".format(h, w)
                number += 1
                total_tiles = self.num_height_tiles * self.num_width_tiles
                tiles.append(Tile(url, filename, number, total_tiles))

        return tiles


class Downloader:
    def __init__(self, tiles):
        self.tiles = tiles
        self.pool = multiprocessing.Pool(processes=100)

    def download(self):
        # self.pool.map(self.get_tile, self.tiles)
        # for tile in self.tiles:
        #     self.pool.apply(get_tile, args=(tile.url, tile.filename))
        self.pool.map(get_tile, self.tiles)



def main():
    image_id = int(sys.argv[1])

    if not os.path.exists(str(image_id)):
        os.makedirs(str(image_id))

    gigapan = Gigapan(image_id)
    downloader = Downloader(gigapan.get_tiles())
    downloader.download()


def get_tile(tile):
    url = tile.url
    filename = tile.filename
    number = tile.number
    total_tiles = tile.total_tiles
    # print "Url: {0}, Filename: {1}".format(url, filename)
    if not os.path.exists(filename):
        response = urllib2.urlopen(url)
        # w = writing, b = binary mode (since it will be an image)
        tile_file = open(filename, 'wb')
        tile_file.write(response.read())
        tile_file.close()
        print "({0}/{1})".format(number, total_tiles)




if __name__ == '__main__':
    main()