#!/usr/bin/env python
#------------------------------------------------------------------------------
#% Programmed by ncelik                                        *****
#% *****     2014(TPAO)                                             *****
#% *****     Latest update as of 27/01/2016                         *****
#% *****                                                            *****
#% *****                                                            *****
#% *****                                                            *****
#% **********************************************************************
#------------------------------------------------------------------------------
## This Script clips all layers in current mxd
import arcpy,os


def clipLayerswExtent():
    
    #Input Parameters
    #--------------------------------------------------------------------------   
    arcpy.env.overwriteOutput = True ## Enables overwriting
    clipMethod=arcpy.GetParameterAsText(0) ## Drawing an areo or giving Extent
    drawingArea=arcpy.GetParameterAsText(1)
    removeOtherLayersAfterClip=arcpy.GetParameterAsText(2)
    extent=[]
    extent.append(arcpy.GetParameterAsText(3))  ##user initialized MinX
    extent.append(arcpy.GetParameterAsText(4))  ##user initialized MinY
    extent.append(arcpy.GetParameterAsText(5))  ##user initialized MaxX
    extent.append(arcpy.GetParameterAsText(6))  ##user initialized MaxY
    if extent[0]>extent[2]:
            arcpy.AddError("Min X degeri Max X değerinden buyuk")
            raise ValueError("Min X degeri Max X değerinden buyuk")
    if extent[1]>extent[3]:
            arcpy.AddError("Min Y degeri Max Y değerinden buyuk")
            raise ValueError("Min Y degeri Max Y değerinden buyuk")
    arcpy.AddMessage(str(extent))
    extentCoordinateIsNotSameAsDataFrame=arcpy.GetParameterAsText(7)
    extentCoordinate=arcpy.GetParameterAsText(8)
    arcpy.AddMessage("Drawing Area defined as : "+ str(drawingArea))
    arcpy.AddMessage("Extent Area defined as : "+ str(extent))
    
    
    #Determines Workspace Path From "Current".mxd path 
    #--------------------------------------------------------------------------     
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
    mdxpath=mxd.filePath
    arcpy.env.workspace=os.path.split(mdxpath)[0]
    #Defines CS of Polygon          
    CoordinateSystem=df.spatialReference  ## Gets data frame coordinate system
    
    #Copy users initiated drawingArea to shp file 
    #--------------------------------------------------------------------------
    arcpy.CopyFeatures_management(drawingArea,"drawingArea.shp")
    #arcpy.CopyFeatures_management(extent,"extent.shp")
      

    #Creates Polygon Array from given extent values 
    #--------------------------------------------------------------------------
    arcpy.AddMessage(extent)
    array = arcpy.Array()
    #LowerLeft=(extent[0],extent[1])
    #LowerRigth=(extent[2],extent[1])
    #TopLeft=(extent[0],extent[3])
    #TopRight=(extent[2],extent[3])    
    if extent[0]!='':
        #extent=extent.split()
        pnt0 = arcpy.Point(float(extent[0]),float(extent[1]))
        array.add(pnt0)
        pnt1 = arcpy.Point(float(extent[2]),float(extent[1]))
        array.add(pnt1)
        pnt2 = arcpy.Point(float(extent[2]),float(extent[3]))
        array.add(pnt2)
        pnt3= arcpy.Point(float(extent[0]),float(extent[3]))
        array.add(pnt3)
        array.add(array.getObject(0))
        extentpoly=arcpy.Polygon(array)
        
        
        if extentCoordinateIsNotSameAsDataFrame=="true" :
            arcpy.DefineProjection_management(extentpoly,CoordinateSystem)
            arcpy.CopyFeatures_management(extentpoly,"extent.shp")
    
        else:
            arcpy.DefineProjection_management(extentpoly,extentCoordinate)
            arcpy.CopyFeatures_management(extentpoly,"extent.shp")

    #List Layers and clips base on the choice
    #--------------------------------------------------------------------------
       
    ###List Layers
    #Kuyu= arcpy.mapping.ListLayers(mxd, "Kuyu", df)[0]
    #    arcpy.Clip_analysis("Kuyu", drawingArea, "kuyuclip.shp")
    layerList=arcpy.mapping.ListLayers(mxd)
    
    for layer in layerList:
        if str(layer)=="New Group Layer" :
            arcpy.mapping.RemoveLayer(df,layer)
            continue
    
        arcpy.AddMessage(layer)
        if arcpy.Describe(layer).spatialReference.name!=CoordinateSystem:                
                arcpy.AddMessage("Katman Koordinatlari Data Frame Koordinatindan farkli")
                arcpy.AddMessage(arcpy.Describe(layer).spatialReference.name)
                arcpy.AddMessage(CoordinateSystem.name)
                #arcpy.Project_management(extent, CoordinateSystem)    
    
                ###ADD here projecting the extent values to  the layer coordinate
        arcpy.AddMessage(clipMethod)
        if clipMethod=="Area_Extent":
    
             arcpy.Clip_analysis(layer, extentpoly, str(layer)+"_clip.shp")
             try :
                 arcpy.Delete_management(drawingArea)
             except:
                pass
             arcpy.MakeFeatureLayer_management(str(layer)+"_clip.shp", str(layer)+"_clip")
             lyr= arcpy.mapping.Layer(str(layer)+"_clip")
             arcpy.ApplySymbologyFromLayer_management (lyr, layer)
             lyr.definitionQuery=layer.definitionQuery
             lyr.labelClasses[0].expression=layer.labelClasses[0].expression
             #    cliplayername=str(layer)+"_clip"
             #    arcpy.AddMessage(cliplayername)
             lyr.showLabels = True
             arcpy.RefreshActiveView()
             arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
             if removeOtherLayersAfterClip=="true":
                arcpy.mapping.RemoveLayer(df, layer)
    
    
        else:
            arcpy.Clip_analysis(layer, drawingArea, str(layer)+"_clip.shp")
            try:
                arcpy.Delete_management(extentpoly)
            except:
                pass
            arcpy.MakeFeatureLayer_management(str(layer)+"_clip.shp", str(layer)+"_clip")
            lyr= arcpy.mapping.Layer(str(layer)+"_clip")
            arcpy.ApplySymbologyFromLayer_management (lyr, layer)
            lyr.definitionQuery=layer.definitionQuery
            lyr.labelClasses[0].expression=layer.labelClasses[0].expression
            #    cliplayername=str(layer)+"_clip"
            #    arcpy.AddMessage(cliplayername)
            lyr.showLabels = True
            arcpy.RefreshActiveView()
            arcpy.mapping.AddLayer(df,lyr,"BOTTOM")
            if removeOtherLayersAfterClip=="true":
                arcpy.mapping.RemoveLayer(df, layer)

if __name__ == '__main__':
    clipLayerswExtent()


