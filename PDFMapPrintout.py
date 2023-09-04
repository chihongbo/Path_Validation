#### Print out the map
import arcpy
import os,sys
arcpy.env.addOutputsToMap = 0  ## avoid add the newly created layers to the MXD file
WorkPath=os.getcwd()
arcpy.env.workspace=WorkPath+"\\Shpfiles"
ins=["OnLocation","OriginLocation_SP","OffLocation","DestinationLocation_SP"]
lyrStop="Stops_Route36_EWB_RV_Buff"
lyrOrigin="OriginLocation_SP_Buff"
lyrDestination="DestinationLocation_SP_Buff"
lyrXRoute="BUSROUTESXFER"
## select the feature to extract the records with error check
fc="FinalOBADCheck.shp"
##filenameAll="C:/Projects/PathValidation/Shpfiles/Rt36Survey"+"_ETC"+".pdf"
filenameAll=WorkPath+"\\Shpfiles\\Rt36Survey"+"_ETC"+".pdf"
pdfdoc=arcpy.mapping.PDFDocumentCreate(filenameAll)
rows=arcpy.da.SearchCursor(fc ,["UID","BAUse","Category","OnSTOP","OffSTOP","ON_PX","ON_PY","OFF_PX","OFF_PY","O_PX","O_PY","D_PX","D_PY","FRoute1","FRoute2","TRoute1","TRoute2","ERRCODE","ErrDscr"])
                            #     0      1       2          3        4         5        6       7        8      9       10    11     12      13        14        15         16        17       18
for Category in xrange(1, 11):
    for row in rows:
        if((row[2]==Category and (row[2]==10 or row[2]==6 or row[2]==8)) or (row[2]==Category and row[2]<10 and row[17]==1)):  #Based on the Category
            UID=row[0]
            OnStop=row[3]
            OffStop=row[4]
            FRoute1=row[13].replace(" Broward","").strip()
            FRoute2=row[14].replace(" Broward","").strip()
            TRoute1=row[15].replace(" Broward","").strip()
            TRoute2=row[16].replace(" Broward","").strip()
            
            for LyrName in ins:
                arcpy.AddMessage(LyrName)
                lyr=arcpy.mapping.Layer(LyrName)
                lyr.definitionQuery='"UID"='+str(UID)
                arcpy.RefreshActiveView()
                del lyr
            lyr1=arcpy.mapping.Layer(lyrStop)
            lyr2=arcpy.mapping.Layer(lyrOrigin)
            lyr3=arcpy.mapping.Layer(lyrDestination)
            lyr4=arcpy.mapping.Layer(lyrXRoute)
            lyr1.definitionQuery='"STOP_ID"='+str(OnStop)+'or "STOP_ID"='+str(OffStop)
            lyr2.definitionQuery='"UID"='+str(UID)
            lyr3.definitionQuery='"UID"='+str(UID)
            lyr4.definitionQuery='"VAR_ROUTE1"='+"'"+FRoute1+"'"+' or "VAR_ROUTE1"='+"'"+FRoute2+"'"+' or "VAR_ROUTE1"='+"'"+TRoute1+"'"+' or "VAR_ROUTE1"='+"'"+TRoute2+"'"
            
            mxd=arcpy.mapping.MapDocument("CURRENT")
            df=arcpy.mapping.ListDataFrames(mxd)[0]
            lyr1=arcpy.mapping.ListLayers(mxd,"*_Buff",df)[0]
            lyr2=arcpy.mapping.ListLayers(mxd,"*_Buff",df)[1]
            lyr3=arcpy.mapping.ListLayers(mxd,"*_Buff",df)[2]
            extent_object=lyr1.getExtent()
            ext2=lyr2.getExtent()
            ext3=lyr3.getExtent()
            if ext2.XMin<extent_object.XMin:
                extent_object.XMin=ext2.XMin
            if ext2.YMin<extent_object.YMin:
                extent_object.YMin=ext2.YMin
            if ext2.XMax>extent_object.XMax:
                extent_object.XMax=ext2.XMax
            if ext2.YMax>extent_object.YMax:
                extent_object.YMax=ext2.YMax
            if ext3.XMin<extent_object.XMin:
                extent_object.XMin=ext3.XMin
            if ext3.YMin<extent_object.YMin:
                extent_object.YMin=ext3.YMin
            if ext3.XMax>extent_object.XMax:
                extent_object.XMax=ext3.XMax
            if ext3.YMax>extent_object.YMax:
                extent_object.YMax=ext3.YMax
            extent_object.XMin=extent_object.XMin*(1-0.002)
            extent_object.YMin=extent_object.YMin*(1-0.002)
            extent_object.XMax=extent_object.XMax*(1+0.002)
            extent_object.YMax=extent_object.YMax*(1+0.002)
            df.extent=extent_object
            title=arcpy.mapping.ListLayoutElements(mxd,"TEXT_ELEMENT")[0]
            title.text="Route 36 Locations of OBAD UID="+str(UID)+" "+"Category="+str(Category) ## based on Category
            arcpy.RefreshActiveView()
            arcpy.RefreshTOC()
            filename=WorkPath+"\\Shpfiles\\Rt36SurveyUID"+str(UID)+"Category"+str(Category)+".pdf" ## Based on Category
            arcpy.mapping.ExportToPDF(mxd,filename)
            pdfdoc.appendPages(filename)
            os.remove(filename)  ## remove the PDF file
            del mxd   
	del row
    rows.reset()			
del rows
pdfdoc.saveAndClose()
del pdfdoc

