import arcpy
import os, sys
arcpy.env.addOutputsToMap = 0  ## avoid add the newly created layers to the MXD file
WorkPath=os.getcwd()
##arcpy.env.workspace="C:\\Projects\\PathValidation\\Shpfiles"
arcpy.env.workspace=WorkPath+"\\Shpfiles"
arcpy.env.overwriteOutput = True
InOrigin="OriginLocation_SP.shp"
OutOrigin="OriginLocation_SP_Buff.shp"
InDestination="DestinationLocation_SP.shp"
OutDestination="DestinationLocation_SP_Buff.shp"
InStops="Stops_Route36_EWB_RV.shp"
OutStops="Stops_Route36_EWB_RV_Buff.shp"
Transit="BUSROUTES.shp"
BSize=0.50


## Buffer Analaysis
BParameter=str(BSize)+" MILES"
Buffer=arcpy.Buffer_analysis(InStops,OutStops,BParameter)
Buffer=arcpy.Buffer_analysis(InOrigin,OutOrigin,BParameter)
Buffer=arcpy.Buffer_analysis(InDestination,OutDestination,BParameter)

## Intersection Analaysis
inFeatures1=[OutStops,Transit]
inFeatures2=[OutOrigin,Transit]
inFeatures3=[OutDestination,Transit]
intersectOutput1="Stop_Route_Int.Shp"
intersectOutput2="Origin_Route_Int.Shp"
intersectOutput3="Destination_Route_Int.Shp"

arcpy.Intersect_analysis(inFeatures1, intersectOutput1,"ALL","","line")
arcpy.Intersect_analysis(inFeatures2, intersectOutput2,"ALL","","line")
arcpy.Intersect_analysis(inFeatures3, intersectOutput3,"ALL","","line")


## Disolve the feature, so that we can save the lookup time

outFeatureClass1 = "Stop_Route_Int_Disolve.shp"
outFeatureClass2 = "Origin_Route_Int_Dissolve.shp"
outFeatureClass3 = "Destination_Route_Int_Dissolve"
dissolveFields1 = ["STOP_ID", "VAR_ROUTE"]
dissolveFields2 = ["UID", "VAR_ROUTE"]
dissolveFields3 = ["UID", "VAR_ROUTE"]
 
## Execute Dissolve using UID and Route as Dissolve Fields
arcpy.Dissolve_management(intersectOutput1, outFeatureClass1, dissolveFields1, "","", "")
arcpy.Dissolve_management(intersectOutput2, outFeatureClass2, dissolveFields2, "","", "")
arcpy.Dissolve_management(intersectOutput3, outFeatureClass3, dissolveFields3, "","", "")


## the following is to Add a field to Two Fields to the OriginLocation_SP and Loop through it "ERRCODE,0,1", And "Notes"

# Set local variables
inFeatures = "FinalOBADCheck.Shp"
fieldName1 = "ERRCODE"
fieldPrecision = 9
fieldName2 = "ErrDscr"
fieldLength = 30
 
# Execute AddField twice for two new fields
#arcpy.AddField_management(inFeatures, fieldName1, "LONG", fieldPrecision, "", "",
#                          "", "NULLABLE")
#arcpy.AddField_management(inFeatures, fieldName2, "TEXT", "", "", fieldLength)


# Start looking through the FinalOBADCheck.shp to update its two columns
import math
fc="FinalOBADCheck.shp"
fcStop="Stop_Route_Int_Disolve.shp"
fcOrigin="Origin_Route_Int_Dissolve.shp"
fcDestination="Destination_Route_Int_Dissolve.shp"


## Temporary Processing Step for the FinalOBADCheck.SHP, Change 19 Broward to 18 Broward
TempStr="19 Broward"
TempStr1="18 Broward"
rows=arcpy.da.UpdateCursor(fc ,["UID","BAUse","Category","OnSTOP","OffSTOP","ON_PX","ON_PY","OFF_PX","OFF_PY","O_PX","O_PY","D_PX","D_PY","FRoute1","FRoute2","TRoute1","TRoute2","ERRCODE","ErrDscr"])
                            #     0      1       2          3        4         5        6       7        8      9       10    11     12      13        14        15         16        17       18
for row in rows:
    if(row[1]=="Used" and row[2]!=1):
        FRoute1=row[13]
        FRoute2=row[14]
        TRoute1=row[15]
        TRoute2=row[16]
        if(TempStr in FRoute1):
            row[13]=TempStr1
        if(TempStr in FRoute2):
            row[14]=TempStr1
        if(TempStr in TRoute1):
            row[15]=TempStr1
        if(TempStr in TRoute2):
            row[16]=TempStr1
        rows.updateRow(row)
del row
del rows
        
rows=arcpy.da.UpdateCursor(fc ,["UID","BAUse","Category","OnSTOP","OffSTOP","ON_PX","ON_PY","OFF_PX","OFF_PY","O_PX","O_PY","D_PX","D_PY","FRoute1","FRoute2","TRoute1","TRoute2","ERRCODE","ErrDscr"])
                            #     0      1       2          3        4         5        6       7        8      9       10    11     12      13        14        15         16        17       18
 ## Case 1: if "Category"=1, then only calculate the Origin to Boarding and Destination to Alighting Distance, if the distance is greater than 0.25 mile then discard it and ErrCode=1
for row in rows:
    row[17]=0
    row[18]=""
    rows.updateRow(row)
    if(row[1]!="Used"):                                            ## Failed passing BA Location
        row[17]=1
        row[18]="BALoc"
        rows.updateRow(row)
    if(row[1]=="Used" and row[2]==1):                              ## Case 1: No Transfer
        DistOn=math.sqrt((row[9]-row[5])**2+(row[10]-row[6])**2)
        DistOff=math.sqrt((row[11]-row[7])**2+(row[12]-row[8])**2)
        ErrNote=""
        if(DistOn>BSize):
            row[17]=1
            ErrNote=ErrNote+"OLoc "
            row[18]=ErrNote
        if(DistOff>BSize):
            row[17]=1
            ErrNote=ErrNote+"DLoc "
            row[18]=ErrNote
        rows.updateRow(row)
##rows=arcpy.da.UpdateCursor(fc ,["UID","BAUse","Category","OnSTOP","OffSTOP","ON_PX","ON_PY","OFF_PX","OFF_PY","O_PX","O_PY","D_PX","D_PY","FRoute1","FRoute2","TRoute1","TRoute2","ERRCODE","ErrDscr"])
                             #     0      1       2          3        4         5        6       7        8      9       10    11     12      13        14        15         16        17       18
    if(row[1]=="Used" and row[2]==2):                             ## Case 2: 1 Transfer at Access and 0 Transfer at Egress
        ErrNote=""
        UID=row[0]
        FRoute1=row[13]
        ONStop=row[3]
        FRIndx=0
        OnStpIndx=0
        DestIndx=0
        rows1=arcpy.da.SearchCursor(fcOrigin ,["UID","VAR_ROUTE"])
        for row1 in rows1:
            if(row1[0]==UID and row1[1].strip() in FRoute1):
                FRIndx=1
                break
        rows2=arcpy.da.SearchCursor(fcStop ,["STOP_ID","VAR_ROUTE"])
        for row2 in rows2:
            if(row2[0]==ONStop and row2[1].strip() in FRoute1):
                OnStpIndx=1
                break
        DistOff=math.sqrt((row[11]-row[7])**2+(row[12]-row[8])**2)

        if(DistOff<=BSize):
            DestIndx=1
        if(FRIndx==0):
            row[17]=1
            ErrNote=ErrNote+"FMd1 "
        if(OnStpIndx==0):
            row[17]=1
            ErrNote=ErrNote+"OnStp "
        if(DestIndx==0):
            row[17]=1
            ErrNote=ErrNote+"DLoc "
        row[18]=ErrNote
        rows.updateRow(row)
        del row1
        del row2
        del rows1
        del rows2
##rows=arcpy.da.UpdateCursor(fc ,["UID","BAUse","Category","OnSTOP","OffSTOP","ON_PX","ON_PY","OFF_PX","OFF_PY","O_PX","O_PY","D_PX","D_PY","FRoute1","FRoute2","TRoute1","TRoute2","ERRCODE","ErrDscr"])
                              #     0      1       2          3        4         5        6       7        8      9       10    11     12      13        14        15         16        17       18
    if(row[1]=="Used" and row[2]==3):                             ## Case 3: 0 Transfer at Access and 1 Transfer at Egress
        ErrNote=""
        UID=row[0]
        TRoute1=row[15]
        OFFStop=row[4]
        TRIndx=0
        OffStpIndx=0
        OriginIndx=0
        rows1=arcpy.da.SearchCursor(fcDestination ,["UID","VAR_ROUTE"])  ## Check destination buffer
        for row1 in rows1:
            if(row1[0]==UID and row1[1].strip() in TRoute1):
                TRIndx=1
                break
        rows2=arcpy.da.SearchCursor(fcStop ,["STOP_ID","VAR_ROUTE"])   ## Check OffStop buffer 
        for row2 in rows2:
            if(row2[0]==OFFStop and row2[1].strip() in TRoute1):
                OffStpIndx=1
                break
        DistOn=math.sqrt((row[9]-row[5])**2+(row[10]-row[6])**2)

     
        if(DistOn<=BSize):
            OriginIndx=1
        if(TRIndx==0):
            row[17]=1
            ErrNote=ErrNote+"TMd1 "
        if(OffStpIndx==0):
            row[17]=1
            ErrNote=ErrNote+"OffStp "
        if(OriginIndx==0):
            row[17]=1
            ErrNote=ErrNote+"OLoc "
        row[18]=ErrNote
        rows.updateRow(row)
        del row1
        del row2
        del rows1
        del rows2

##rows=arcpy.da.UpdateCursor(fc ,["UID","BAUse","Category","OnSTOP","OffSTOP","ON_PX","ON_PY","OFF_PX","OFF_PY","O_PX","O_PY","D_PX","D_PY","FRoute1","FRoute2","TRoute1","TRoute2","ERRCODE","ErrDscr"])
                              #     0      1       2          3        4         5        6       7        8      9       10    11     12      13        14        15         16        17       18

    if(row[1]=="Used" and row[2]==4):                             ## Case 4 2 Transfer at Access and 0 Transfer at Egress
        ErrNote=""
        UID=row[0]
        FRoute1=row[13]
        FRoute2=row[14]
        ONStop=row[3]
        DestinationIndx=0
        rows1=arcpy.da.SearchCursor(fcOrigin ,["UID","VAR_ROUTE"])
        for row1 in rows1:
            if(row1[0]==UID and row1[1].strip() in FRoute2):
                FRIndx=1
                break
        rows2=arcpy.da.SearchCursor(fcStop ,["STOP_ID","VAR_ROUTE"])
        for row2 in rows2:
            if(row2[0]==ONStop and row2[1].strip() in FRoute1):
                OnStpIndx=1
                break
        DistOff=math.sqrt((row[11]-row[7])**2+(row[12]-row[8])**2)
 
        if(DistOff<=BSize):
            DestinationIndx=1
        if(FRIndx==0):
            row[17]=1
            ErrNote=ErrNote+"FMd2 "
        if(OnStpIndx==0):
            row[17]=1
            ErrNote=ErrNote+"FMd1 "
        if(DestinationIndx==0):
            row[17]=1
            ErrNote=ErrNote+"DLoc "
        row[18]=ErrNote
        rows.updateRow(row)
        del row1
        del row2
        del rows1
        del rows2

##rows=arcpy.da.UpdateCursor(fc ,["UID","BAUse","Category","OnSTOP","OffSTOP","ON_PX","ON_PY","OFF_PX","OFF_PY","O_PX","O_PY","D_PX","D_PY","FRoute1","FRoute2","TRoute1","TRoute2","ERRCODE","ErrDscr"])
                              #     0      1       2          3        4         5        6       7        8      9       10    11     12      13        14        15         16        17       18
    if(row[1]=="Used" and row[2]==5):                             ## Case 5 0 Transfer at Access and 2 Transfer at Egress
        ErrNote=""
        UID=row[0]
        TRoute1=row[15]
        TRoute2=row[16]
        OFFStop=row[4]
        TRIndx=0
        OffStpIndx=0
        OriginIndx=0
        rows1=arcpy.da.SearchCursor(fcDestination ,["UID","VAR_ROUTE"])
        for row1 in rows1:
            if(row1[0]==UID and row1[1].strip() in TRoute2):
                TRIndx=1
                break
        rows2=arcpy.da.SearchCursor(fcStop ,["STOP_ID","VAR_ROUTE"])
        for row2 in rows2:
            if(row2[0]==OFFStop and row2[1].strip() in TRoute1):
                OffStpIndx=1
                break
        DistOn=math.sqrt((row[9]-row[5])**2+(row[10]-row[6])**2)

       
        if(DistOn<=BSize):
            OriginIndx=1
        if(TRIndx==0):
            row[17]=1
            ErrNote=ErrNote+"TMd2 "
        if(OffStpIndx==0):
            row[17]=1
            ErrNote=ErrNote+"TMd1 "
        if(OriginIndx==0):
            row[17]=1
            ErrNote=ErrNote+"OLoc "
        row[18]=ErrNote
        rows.updateRow(row)
        del row1
        del row2
        del rows1
        del rows2

##rows=arcpy.da.UpdateCursor(fc ,["UID","BAUse","Category","OnSTOP","OffSTOP","ON_PX","ON_PY","OFF_PX","OFF_PY","O_PX","O_PY","D_PX","D_PY","FRoute1","FRoute2","TRoute1","TRoute2","ERRCODE","ErrDscr"])
                              #     0      1       2          3        4         5        6       7        8      9       10    11     12      13        14        15         16        17       18
    if(row[1]=="Used" and row[2]==8):                             ## Case 8 1 Transfer at Access and 1 Transfer at Egress
        ErrNote=""
        UID=row[0]
        FRoute1=row[13]
        TRoute1=row[15]
        ONStop=row[3]
        OFFStop=row[4]
        FRIndx=0
        TRIndx=0
        OnStpIndx=0
        OffStpIndx=0
  
        rows1=arcpy.da.SearchCursor(fcOrigin ,["UID","VAR_ROUTE"])
        for row1 in rows1:
            if(row1[0]==UID and row1[1].strip() in FRoute1):
                FRIndx=1
                break
        rows2=arcpy.da.SearchCursor(fcStop ,["STOP_ID","VAR_ROUTE"])
        for row2 in rows2:
            if(row2[0]==ONStop and row2[1].strip() in FRoute1):
                OnStpIndx=1
                break
        del rows2
        del row2
        rows3=arcpy.da.SearchCursor(fcStop ,["STOP_ID","VAR_ROUTE"])
        for row3 in rows3:
            if(row3[0]==OFFStop and row3[1].strip() in TRoute1):
                OffStpIndx=1
                break
        rows4=arcpy.da.SearchCursor(fcDestination ,["UID","VAR_ROUTE"])
        for row4 in rows4:
            if(row4[0]==UID and row4[1].strip() in TRoute1):
                TRIndx=1
                break

        if(FRIndx==0):
            row[17]=1
            ErrNote=ErrNote+"FMd1 "
        if(TRIndx==0):
            row[17]=1
            ErrNote=ErrNote+"TMd1 "
        if(OnStpIndx==0):
            row[17]=1
            ErrNote=ErrNote+"OnStp "
        if(OffStpIndx==0):
            row[17]=1
            ErrNote=ErrNote+"OffStp "
        row[18]=ErrNote
        rows.updateRow(row)
        del row1
        del rows1
        del row3
        del row4
        del rows3
        del rows4
del row
del rows


