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

This script downloads tiles from here.com's 3d maps
go to the website above, find a tile, copy and past its name below

The core code is all by Michal Migurski
he wrote about it here: http://mike.teczno.com/notes/webgl-nokia-maps-II.html
and his original code is here: https://github.com/migurski/NokiaWebGL

I've just added a loop to grab multiple tiles
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


def makeNokiaDirs(path):
    #jpg = open('tile_sets/%s_%d.jpg' % (name[4], texture), 'w')
    #recreate the original folder structure
    directory_ar = path.split('/');
    directory = ''
    for index in range(len(directory_ar)-1):
        directory =  directory + directory_ar[index] + '/';
    if not os.path.exists(directory):
        os.makedirs(directory)

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


def coordinateHeights(tile_coord):
    """
    """
    lut_coord = tile_coord.zoomTo(13).container()  # height lookup tables exist only at z13
    server = 'bcde'[int(lut_coord.row + lut_coord.column + lut_coord.zoom) % 4]
    path = coordinatePath(lut_coord)

    url = 'http://%(server)s.maps3d.svc.nokia.com/data4/%(path)s.lut' % locals()
    #print "lut url %s" % (url)
    data = urlopen(url).read()
    zoom = tile_coord.zoom - lut_coord.zoom

    #
    # Skip to the beginning of the correct zoom level in the mipmap
    #

    dim = 2**zoom, 2**zoom
    off = sum([0] + [4**i for i in range(zoom)])

    #
    # Skip to the correct row in the mipmap zoom level, but use the "col"
    # value because the data is actually stored on its side, west-up.
    #

    col = tile_coord.column - lut_coord.zoomTo(tile_coord.zoom).column
    # off += int(col - 1) * 2**zoom
    off += int(col) * 2 ** zoom

    #
    # Skip to the correct column in the mipmap zoom level, but use the "row"
    # value because the data is actually stored on its side, west-up.
    #

    row = tile_coord.row - lut_coord.zoomTo(tile_coord.zoom).row
    # off += 2**zoom - int(row) - 1
    off += 2 ** zoom - int(row) - 1

    #
    # Read bottom and top heights in meters.
    #

    bottom, top = unpack('<HH', data[off * 4: off * 4 + 4])

    print "type: %s" % (type(top))

    return bottom, top


def extract_vertices(data, count, bottom, top):
    """
    """
    xyz_data, uv_data = data[:count * 12], data[count * 12:]

    xyz_values = [unpack('<fff', xyz_data[off:off + 12]) for off in range(0, count * 12, 12)]
    uv_values = [unpack('<ff', uv_data[off:off + 8]) for off in range(0, count * 8, 8)]

    scale = (top - bottom) / 2 ** 16
    vertices = [(x / 256, y / 256, (bottom + scale * z) / 256, u, v) for ((z, x, y), (u, v)) in zip(xyz_values, uv_values)]
    # vertices = [(x/256, y/256, (z)/256, u, v) for ((z, x, y), (u, v)) in zip(xyz_values, uv_values)]

    return vertices


def extract_faces(data, count):
    """
    """
    triangles = [unpack('<HHH', data[off:off + 6]) for off in range(0, count * 6, 6)]

    return triangles


class BadZoom (Exception):
    pass


class Provider (IMapProvider):

    def __init__(self):
        t = deriveTransformation(-pi, pi, 0, 0, pi, pi, 1, 0, -pi, -pi, 0, 1)
        self.projection = MercatorProjection(0, t)

    def getTileData(self, coord, whole, getModels, getTextures):
        """
        """
        server = 'bcde'[int(coord.row + coord.column + coord.zoom) % 4]
        path = coordinatePath(coord)

        url = 'http://%(server)s.maps3d.svc.nokia.com/data4/%(path)s.n3m' % locals()

        #
        # Lookup the bottom and top of the tile data in meters, and convert
        # that to a scale value for the raw z-axis based on current latitude.
        #

        lat_span = abs(self.coordinateLocation(coord).lat - self.coordinateLocation(coord.down()).lat)
        meter_span = 6378137 * pi * lat_span / 180.0

        bottom, top = coordinateHeights(coord)
        print >> stderr, 'bottom, top:', bottom, top

        bottom, top = bottom * 2 ** 16 / meter_span, top * 2 ** 16 / meter_span

        print >> stderr, 'bottom, top:', bottom, top

        #
        # Open the data and count the textures.
        #

        data = urlopen(url).read()
        (textures, ) = unpack('<i', data[4:8])

        print >> stderr, 'textures:', textures

        #
        # Pick out the vertices for the geometry,
        # as lists of (x, y, z, u, v) coordinates.
        #

        off = 12
        vertex_blocks = [unpack('<ii', data[off:off + 8]) for off in range(off, off + textures * 8, 8)]
        vertex_data = [extract_vertices(data[start:], count, bottom, top) for (start, count) in vertex_blocks]

        print >> stderr, 'vertex blocks:', vertex_blocks

        for i in range(textures):
            print >> stderr, 'vertices', i, '-', len(vertex_data[i]),
            print >> stderr, map(min, zip(*vertex_data[i])), 'to', map(max, zip(*vertex_data[i]))

        #
        # Pick out the faces for each texture as triples of vertex indexes.
        #

        off = 12 + textures * 8
        face_blocks = [unpack('<ii', data[off:off+8]) for off in range(off, off + textures * 16, 16)]
        face_data = [extract_faces(data[start:], count) for (start, count) in face_blocks]

        print >> stderr, 'face blocks:', face_blocks

        for i in range(textures):
            print >> stderr, 'faces', i, '-', len(face_data[i]),
            print >> stderr, map(min, zip(*face_data[i])), 'to', map(max, zip(*face_data[i]))

        #
        # Pick out the filenames of the JPEG textures,
        # stored as ASCII strings deeper in the file.
        #

        off = 12 + textures * 8
        bitmap_blocks = [unpack('<ii', data[off + 8:off + 16]) for off in range(off, off + textures * 16, 16)]
        imagename_blocks = [(start + 1, unpack('<B', data[start:start + 1])[0]) for (index, start) in bitmap_blocks]
        image_names = [data[start:start + length] for (start, length) in imagename_blocks]
        image_urls = [urljoin(url, name) for name in image_names]

        print >> stderr, 'bitmap blocks:', bitmap_blocks
        print >> stderr, 'image urls:', image_urls

        #
        # Output .obj files and JPEGs locally.
        #

        if getModels:
            makeNokiaDirs(path)
            if whole:
                #saves a blank model

                obj = open('%(path)s.obj'% locals(), 'w')
                count = 0

                for texture in range(textures):

                    local_count = 0

                    for (x, y, z, u, v) in vertex_data[texture]:
                        print >> obj, 'v %.1f %.1f %.1f' % (x, y, z)
                        local_count += 1

                    for (x, y, z, u, v) in vertex_data[texture]:
                        print >> obj, 'vt %.6f %.6f' % (u, v)

                    for (v0, v1, v2) in face_data[texture]:
                        print >> obj, 'f %d/%d %d/%d %d/%d' % (v0+1+count, v0+1+count, v1+1+count, v1+1+count, v2+1+count, v2+1+count)

                    count += local_count

            else:
                for texture in range(textures):
                    obj = open('%(path)s_%(texture)s.obj'% locals(), 'w')

                    for (x, y, z, u, v) in vertex_data[texture]:
                        print >> obj, 'v %.1f %.1f %.1f' % (x, y, z)

                    for (x, y, z, u, v) in vertex_data[texture]:
                        print >> obj, 'vt %.6f %.6f' % (u, v)

                    for (v0, v1, v2) in face_data[texture]:
                        print >> obj, 'f %d/%d %d/%d %d/%d' % (v0+1, v0+1, v1+1, v1+1, v2+1, v2+1)

        if getTextures:
            for texture in range(textures):
                makeNokiaDirs(path)
                jpg = open('%(path)s.jpg'% locals(), 'w')
                jpg.write(urlopen(image_urls[texture]).read())

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
    #set starting tile - top left corner of grid
    #map_d_b_a_0.jpg
    #miami map_19_300993_145406_0.jpg
    #nyc map_19_327253_154393_0.jpg
    #set the zoom level to 19 to get highest quality data
    #script only works with zoom set to 19... should probably fix this
    #
    d = 19 #19 is the maximum zoom - this script only works with that zoom level 
    b = 327253
    a = 154393
    
    grid = 4 #grid size
    saveTextures = True #save the texture maps?
    saveModels = True #save the 3d models?
    mergedTiles = True #merge the individual 3d models into a single 3d tile

    #get the tiles
    for i in range(grid):
        for j in range(grid):
        #19_314808_89608_0_15x15
            y, x, z = fromNokia(a+i, b+j, 19)
            c = Coordinate(x, y, z)

            loc = Location(lat, lon)
            coord = p.locationCoordinate(loc).zoomTo(c.zoom)

            p.getTileData(c, mergedTiles, saveModels, saveTextures)
