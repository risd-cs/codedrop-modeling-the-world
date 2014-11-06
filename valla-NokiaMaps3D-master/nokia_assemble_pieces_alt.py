import Rhino
from Rhino.FileIO import FileReadOptions
import scriptcontext
import rhinoscriptsyntax as rs
import os
import math


def importFiles(filePathList):
    '''Import a list of files'''
    # opt = FileReadOptions()
    # opt.ImportMode = True
    for f in filePathList:
        print 'Importing %s' % f
        loaded = scriptcontext.doc.ReadFile(f, opt)
        return loaded


def importFile(filePath):
    '''import one file.'''
    print 'Importing %s' % filePath
    loaded = scriptcontext.doc.ReadFile(filePath, opt)
    return loaded


def extrudeMesh(obj):
    if rs.IsMesh(obj):
        borders = rs.DuplicateMeshBorder(obj)
        curves = rs.ExplodeCurves(borders, True)

        for curve in curves:
            sp = rs.CurveStartPoint(curve)
            ep = rs.CurveEndPoint(curve)

            cplane = rs.ViewCPlane()
            xform = rs.XformPlanarProjection(cplane)
            curve2 = rs.TransformObjects(curve, xform, True)

            sp2 = rs.CurveStartPoint(curve2)
            ep2 = rs.CurveEndPoint(curve2)
            rs.DeleteObjects(curve2)

            vertices = []
            vertices.append(sp)
            vertices.append(ep)
            vertices.append(ep2)
            vertices.append(sp2)
            # vertices = (sp,ep,ep2,sp2)
            if len(vertices) == 4:
                fv = []
                fv.append((0, 1, 2, 3))
                try:
                    rs.AddMesh(vertices, fv)
                except:
                    pass

        rs.DeleteObjects(borders)
        rs.DeleteObjects(curves)
        rs.Command('-_SelAll')
        rs.Command('-Join')


def loadMoveFile(filename, x, y):
    print filename

    loaded = False
    loop_exit = 0
    while not loaded and loop_exit < 10:
        loaded = importFile(folder + filename)
        loop_exit += 1

    rs.Command('-_SelAll')
    objects = rs.SelectedObjects()

    if len(objects) > 0:
        rs.Command('-_Move 0,0,0 0,0,%d' % (modz))
        if extrude_mesh:
            #collapse the mesh
            rs.Command('-CollapseMeshFacesByArea SelectFacesGreaterThan=0 Enter SelectFacesLessThan=50 Enter Enter')
            rs.Command('-_SelAll')
            rs.Command('-CollapseMeshFacesByArea SelectFacesGreaterThan=0 Enter SelectFacesLessThan=50 Enter Enter')

            #explode the mesh
            rs.Command('-_SelAll')
            rs.Command('-Weld 180 Enter Enter')
            rs.Command('-_SelAll')
            # rs.Command('-Explode')

            #loop through meshes, delete small ones and extrude large ones
            rs.Command('-_SelAll')
            meshes = rs.SelectedObjects()

            for mesh in meshes:
                if rs.MeshFaceCount(mesh) < 8:
                    rs.DeleteObject(mesh)
                else:
                    extrudeMesh(mesh)
            rs.Command('-_SelAll')

        rs.Command('-_Move 0,0,0 %d,%d,0' % (x, y))
        rs.Command('-_Lock')


#general options
folder = "/Users/clementvalla/projects/1301_every_surface/work/scripts/19/3315/0386/76/"
spacing = 256

#how many meshes to import?
maxIn = 0  # make this 0 to import all obj files in folder
count = 0

#options when importing all files
grid = 16
modz = 5

#options to import different parts as a block
import_in_blocks = True
globx = 0
globy = 0
single_level = True
level = 0

#options for reducing the mesh and cleaning the edges
extrude_mesh = False

#options for rhino file importing : leave as is
opt = FileReadOptions()
opt.ImportMode = True

print folder
print len(os.listdir(folder))
for filename in os.listdir(folder):
    if filename.endswith('.obj'):

        #import file based on the file name
        if import_in_blocks:
            coords = filename.split('.')
            coords = coords[0].split('_')
            #map_19_327273_154391_0.obj

            if globx == 0:
                print coords[3]
                globx = int(coords[3])

            if globy == 0:
                globy = int(coords[2])

            thisx = int(coords[3])
            thisy = int(coords[2])

            thisz = 0
            if len(coords)>=5:
                thisz = int(coords[4][:1])

            if not (single_level and not thisz == level):
                mx = (thisx - globx) * spacing
                my = (thisy - globy) * spacing
                zmx = thisz % 2 * 256
                zmy = math.floor(thisz / 2) * 256

                loadMoveFile(filename, mx + zmx, my + zmy)

        #import files one by one
        else:
            loadMoveFile(filename, spacing * (count % grid), spacing * math.floor(count / grid))

        count += 1

        if maxIn > 0 and count >= maxIn:
            break
