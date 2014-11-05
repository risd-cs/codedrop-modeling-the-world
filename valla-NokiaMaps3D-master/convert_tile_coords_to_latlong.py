from math import log, pow, pi, ceil

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

class Provider (IMapProvider):
    
    def __init__(self):
        t = deriveTransformation(-pi, pi, 0, 0, pi, pi, 1, 0, -pi, -pi, 0, 1)
        self.projection = MercatorProjection(0, t)


if __name__ == '__main__':

	p = Provider()

	# if len(argv) == 1:
 #        lat, lon = 33.997956, -118.486562
 #        zoom = 19

 #    elif len(argv) == 4:
 #        lat, lon = map(float, argv[1:3])
 #        zoom = int(argv[3])

	# 19_327161_154373
	# 40.714623,-74.006605
	x = 154373
	y = 327161
	z = 19
	x2,y2,z2 = fromNokia(x,y,z)
	c = Coordinate(y2,x2,z2)
	loc = p.coordinateLocation(c)
	print "%f, %f " % (loc.lat,loc.lon)

