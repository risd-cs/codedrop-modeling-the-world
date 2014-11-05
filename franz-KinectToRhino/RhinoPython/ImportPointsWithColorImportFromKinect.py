# Import points from a text file
import rhinoscriptsyntax as rs



def ImportPoints():
    #prompt the user for a file to import
    filter = "Text file (*.txt)|*.txt|All Files (*.*)|*.*||"
    filename = rs.OpenFileName("Open Point File", filter)
    if not filename: return
    
    #read each line from the file
    file = open(filename, "r")
    contents = file.readlines()
    

    rs.AddLayer("3d Scan")
    rs.AddLayer("3d Scan - white")
    rs.AddLayer("3d Scan - crvs")

    last = [0,0,0]


    for text in contents:
        items = text.strip("()\r\n").split(",")

        

        if (len(items)==6):

            x = float(items[0])
            y = float(items[1])
            z = float(items[2])

            r = float(items[3])
            g = float(items[4])
            b = float(items[5])

            if (x+y+z!=0):

                if (r+g+b < 440):

                    pt = rs.AddPoints([x,z,y])
                    rs.ObjectColor(pt, [r,g,b])
                    rs.ObjectLayer(pt, "3d Scan")

                    #line / crv
                    print(rs.VectorLength(rs.VectorCreate([x,z,y], last)))
                    if (rs.VectorLength(rs.VectorCreate([x,z,y], last)) <= 20):
                        pt = rs.AddLine([x,z,y], last)
                        rs.ObjectLayer(pt, "3d Scan - crvs")
                        print("add crv")

                    
                    

                else:
                    pt = rs.AddPoints([x,z,y])
                    rs.ObjectColor(pt, [r,g,b])
                    rs.ObjectLayer(pt, "3d Scan - white")

                last = [x,z,y]

            

        else:
            print ("INCOMPLETE.str line: "+str(items))
    file.close()
    
    



##########################################################################
# Check to see if this file is being executed as the "main" python
# script instead of being used as a module by some other python script
# This allows us to use the module which ever way we want.
if( __name__ == "__main__" ):
    ImportPoints()