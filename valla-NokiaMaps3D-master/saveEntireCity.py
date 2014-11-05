"""
_____/\\\\\\\\\\__________/\\\____________                                             
 ___/\\\///////\\\________\/\\\____________                                            
  __\///______/\\\_________\/\\\____________                                           
   _________/\\\//__________\/\\\____________                                          
    ________\////\\\____/\\\\\\\\\____________                                         
     ___________\//\\\__/\\\////\\\____________                                        
      __/\\\______/\\\__\/\\\__\/\\\____________                                       
       _\///\\\\\\\\\/___\//\\\\\\\/\\___________                                      
        ___\/////////______\///////\//____________                                     
_______________________________________________________________                        
 _______________________________________________________________                       
  ______________________________________/\\\\\\\\\_______________                      
   ____/\\\\\__/\\\\\____/\\\\\\\\\_____/\\\/////\\\__/\\\\\\\\\\_                     
    __/\\\///\\\\\///\\\_\////////\\\___\/\\\\\\\\\\__\/\\\//////__                    
     _\/\\\_\//\\\__\/\\\___/\\\\\\\\\\__\/\\\//////___\/\\\\\\\\\\_                   
      _\/\\\__\/\\\__\/\\\__/\\\/////\\\__\/\\\_________\////////\\\_                  
       _\/\\\__\/\\\__\/\\\_\//\\\\\\\\/\\_\/\\\__________/\\\\\\\\\\_                 
        _\///___\///___\///___\////////\//__\///__________\//////////__                
______________________________________________________________________________         
 ______________________________________________________________________________        
  ______________________/\\\____________________________________________________       
   ____/\\\\\__/\\\\\___\///___/\\/\\\\\\____/\\\____/\\\__/\\\\\\\\\\___________      
    __/\\\///\\\\\///\\\__/\\\_\/\\\////\\\__\/\\\___\/\\\_\/\\\//////____________     
     _\/\\\_\//\\\__\/\\\_\/\\\_\/\\\__\//\\\_\/\\\___\/\\\_\/\\\\\\\\\\___________    
      _\/\\\__\/\\\__\/\\\_\/\\\_\/\\\___\/\\\_\/\\\___\/\\\_\////////\\\___________   
       _\/\\\__\/\\\__\/\\\_\/\\\_\/\\\___\/\\\_\//\\\\\\\\\___/\\\\\\\\\\___________  
        _\///___\///___\///__\///__\///____\///___\/////////___\//////////____________ 
_____/\\\\\\\\\\__________/\\\__                                                       
 ___/\\\///////\\\________\/\\\__                                                      
  __\///______/\\\_________\/\\\__                                                     
   _________/\\\//__________\/\\\__                                                    
    ________\////\\\____/\\\\\\\\\__                                                   
     ___________\//\\\__/\\\////\\\__                                                  
      __/\\\______/\\\__\/\\\__\/\\\__                                                 
       _\///\\\\\\\\\/___\//\\\\\\\/\\_                                                
        ___\/////////______\///////\//__                                               


http://www.3d-maps-minus-3d.com/


This script attempts to save whole city from here.com's 3d mode
Since only cities are modeled in 3d so far (2014), they are a little bit like 'islands' - surrounded by tiles with no data
This script finds those edhes, and proceeds to download all the tiles.
- IT TAKES FOREVER, AND DOWNLOADS LOTS OF IMAGES so proceed with care


The core code is all by Michal Migurski
he wrote about it here: http://mike.teczno.com/notes/webgl-nokia-maps-II.html
and his original code is here: https://github.com/migurski/NokiaWebGL
"""


from sys import argv, stderr
from math import log, pow, pi, ceil
from urlparse import urljoin
from urllib import urlopen
from struct import unpack
import os
import os.path
from ModestMaps.Geo import Location, MercatorProjection, deriveTransformation
from ModestMaps.Providers import IMapProvider
from ModestMaps.Core import Coordinate


def fromNokia(x, y, zoom):
    """ Return column, row, zoom for Nokia x, y, z.
    """
    row = int(pow(2, zoom) - y - 1)
    col = x
    return col, row, zoom


def toNokia(col, row, zoom):
    """ Return x, y, z for Nokia tile column, row, zoom.
    """
    x = col
    y = int(pow(2, zoom) - row - 1)
    return x, y, zoom


def coordinatePath(coord):
    """
    """
    x, y, z = toNokia(int(coord.column), int(coord.row), int(coord.zoom))
    #
    # maximum number of digits in row or column at this zoom
    # and a zero-padded string format for integers.
    #
    len = ceil(log(2 ** z) / log(10))
    fmt = '%%0%dd' % len

    row, col = fmt % y, fmt % x

    if len == 4:
        dir = '%s%s/%s%s' % (row[0:2], col[0:2], row[2:3], col[2:3])
    elif len == 5:
        dir = '%s%s/%s%s' % (row[0:2], col[0:2], row[2:4], col[2:4])
    elif len == 6:
        dir = '%s%s/%s%s/%s%s' % (row[0:2], col[0:2], row[2:4], col[2:4], row[4:5], col[4:5])
    else:
        raise BadZoom('len = %d unsupported' % len)

    return '%(z)d/%(dir)s/map_%(z)d_%(y)d_%(x)d' % locals()

class BadZoom (Exception):
    pass


class Provider (IMapProvider):

    def __init__(self):
        t = deriveTransformation(-pi, pi, 0, 0, pi, pi, 1, 0, -pi, -pi, 0, 1)
        self.projection = MercatorProjection(0, t)

    def getTileData(self, coord):
        """
        """
        server = 'bcde'[int(coord.row + coord.column + coord.zoom) % 4]
        path = coordinatePath(coord)

        url = 'http://%(server)s.maps3d.svc.nokia.com/data4/%(path)s.n3m' % locals()

        #
        # Open the data and count the textures.
        #
        try:
            data = urlopen(url).read()
            (textures, ) = unpack('<i', data[4:8])
            print >> stderr, 'url:', url
            #print >> stderr, 'textures:', textures

            #
            # Pick out the filenames of the JPEG textures,
            # stored as ASCII strings deeper in the file.
            #

            off = 12 + textures * 8
            bitmap_blocks = [unpack('<ii', data[off + 8:off + 16]) for off in range(off, off + textures * 16, 16)]
            imagename_blocks = [(start + 1, unpack('<B', data[start:start + 1])[0]) for (index, start) in bitmap_blocks]
            image_names = [data[start:start + length] for (start, length) in imagename_blocks]
            image_urls = [urljoin(url, name) for name in image_names]

            #print >> stderr, 'bitmap blocks:', bitmap_blocks
            #print >> stderr, 'image urls:', image_urls

            #
            # Output JPEGs locally.
            #
            name = path.split('/')

            count = 0
            for texture in range(textures):
                if image_urls[count].endswith('.jpg'):
                    #jpg = open('tile_sets/out_%s_%d.jpg' % (name[4], texture), 'w')
                    #recreate the original folder structure
                    directory_ar = path.split('/');
                    directory = 'data/'
                    for index in range(len(directory_ar)-1):
                        directory =  directory + directory_ar[index] + '/';
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    jpg = open('data/%(path)s_%(count)s.jpg'% locals(), 'w')
                    jpg.write(urlopen(image_urls[texture]).read())
                    count += 1

            return True;

        except:
            print >> stderr, ' 404'
            return False;

if __name__ == '__main__':

    p = Provider()

    if len(argv) == 1:
        lat, lon = 33.997956, -118.486562
        zoom = 19

    elif len(argv) == 4:
        lat, lon = map(float, argv[1:3])
        zoom = int(argv[3])

    else:
        raise Exception('oops')

    #
    #SET THE INITIAL TILE HERE
    #it can be any tile within a city... the script will iterate through until it finds the edges
    #
    #tile urls look like this:
    #http://c.maps3d.svc.nokia.com/data4//13/5124/11/map_d_b_a_0.jpg
    #http://c.maps3d.svc.nokia.com/data4//13/5124/11/map_13_5119_2411_0.jpg
    #http://d.maps3d .svc.nokia.com/data4//13/5124/11/map_13_5110_2410_0.jpg
    #
    a = 77197
    b = 163624
    d = 18

    #this is all stuff to make the script 'walk' around the tiles until it finds the edges
    grid = 10
    i = 38
    j = -121
    diri = 1
    dirj = -1
    maxi = 8
    mini = -8
    foundrow = False
    reachedEnd = False

    while (not reachedEnd):
        y, x, z = fromNokia(a+i, b+j, d)
        c = Coordinate(x, y, z)

        loc = Location(lat, lon)
        coord = p.locationCoordinate(loc).zoomTo(c.zoom)

        print >> stderr, 'i:', i,'->',a+i,' j:', j,'->',b+j,

        if p.getTileData(c):
            i += diri
            maxi = max(maxi,i)
            mini = min(mini,i)
            foundrow = True
        else: 
            if (i<maxi and i>mini):
                i += diri

            #if you get to the end of a row
            elif(i==maxi or i==mini):
                #if no tiles were found in row
                print >> stderr, 'foundrow:',foundrow
                if (foundrow == False):
                    #restart and switch direction
                    if (diri == 1):
                        diri = -1
                        i = -1
                        if (dirj == 1):
                            j = 0
                        else:
                            j = -1
                    elif (dirj == 1):
                        dirj = -1
                        j = -1
                        diri = 1
                        i = 0
                    else:
                        reachedEnd = True
                else:
                    foundrow = False
                    i = 0
                    j += dirj

