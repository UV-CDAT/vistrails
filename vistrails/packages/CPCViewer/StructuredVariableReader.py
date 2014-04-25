'''
Created on Nov 21, 2011

@author: tpmaxwel
'''
from __future__ import with_statement
from __future__ import division

_TRY_PYSIDE = True

try:
    if not _TRY_PYSIDE:
        raise ImportError()
    import PySide.QtCore as _QtCore
    QtCore = _QtCore
    import PySide.QtGui as _QtGui
    QtGui = _QtGui
    USES_PYSIDE = True
except ImportError:
    import sip
    try: sip.setapi('QString', 2)
    except: pass
    try: sip.setapi('QVariant', 2)
    except: pass
    import PyQt4.QtCore as _QtCore
    QtCore = _QtCore
    import PyQt4.QtGui as _QtGui
    QtGui = _QtGui
    USES_PYSIDE = False
    
import vtk, sys, os, copy, time, traceback
import cdms2, cdtime, cdutil, MV2, cPickle 
from packages.CPCViewer.DV3DPlot import  PlotType, getClassName
from StringIO import StringIO
import numpy as np
PortDataVersion = 0

def getStringDataArray( name, values = [] ):
    array = vtk.vtkStringArray()
    array.SetName( name )
    for value in values:
        array.InsertNextValue( value )
    return array

def getMaxScalarValue( scalar_dtype ):
    if scalar_dtype == np.ushort:
        return 65535.0
    if scalar_dtype == np.ubyte:
        return 255.0 
    if scalar_dtype == np.float32:
        f = np.finfo(np.float32) 
        return f.max
    if scalar_dtype == np.float64:
        f = np.finfo(np.float64) 
        return f.max
    return None

class CDMSDataType:
    Volume = 1
    Slice = 2
    Vector = 3
    Hoffmuller = 4
    ChartData = 5
    VariableSpace = 6
    Points = 7
    
    @classmethod
    def getName( cls, type ):
        if type == cls.Volume: return "volume"
        if type == cls.Points: return "points"
        if type == cls.Vector: return "vector"
        
def getItem( output, index = 0 ): 
    if not ( isinstance(output,list) or isinstance(output,tuple) ): return  output
    return output[ index ] 

def encodeToString( obj ):
    rv = None
    try:
        buffer = StringIO()
        pickler = cPickle.Pickler( buffer )
        pickler.dump( obj )
        rv = buffer.getvalue()
        buffer.close()
    except Exception, err:
        print>>sys.stderr, "Error pickling object %s: %s" % ( str(obj), str(err) )
    return rv

def decodeFromString( string_value, default_value=None ):
    obj = default_value
    try:
        buffer = StringIO( string_value )
        pickler = cPickle.Unpickler( buffer )
        obj = pickler.load()
        buffer.close()
    except Exception, err:
        print>>sys.stderr, "Error unpickling string %s: %s" % ( string_value, str(err) )
    return obj

def addr( obj ): 
    return '0' if (obj == None) else obj.GetAddressAsString( obj.__class__.__name__ )

def getRangeBounds( type_str ):
    if type_str == 'UShort':
        return [ 0, 65535, 1 ]
    if type_str == 'UByte':
        return [ 0, 255, 1 ] 
    if type_str == 'Float':
        f = np.finfo(float) 
        return [ -f.max, f.max, 1 ]
    return None

def getNewVtkDataArray( scalar_dtype ):
    if scalar_dtype == np.ushort:
        return vtk.vtkUnsignedShortArray() 
    if scalar_dtype == np.ubyte:
        return vtk.vtkUnsignedCharArray() 
    if scalar_dtype == np.float32:
        return vtk.vtkFloatArray() 
    if scalar_dtype == np.float64:
        return vtk.vtkDoubleArray() 
    return None

def getDatatypeString( scalar_dtype ):
    if scalar_dtype == np.ushort:
        return 'UShort' 
    if scalar_dtype == np.ubyte:
        return 'UByte' 
    if scalar_dtype == np.float32:
        return 'Float' 
    if scalar_dtype == np.float64:
        return 'Double' 
    return None

class OutputRecManager: 
    
    sep = ';#:|!'   
            
    def __init__( self, serializedData = None ): 
        self.outputRecs = {}
        if serializedData <> None:
            self.deserialize( serializedData )
            
    def deleteOutput( self, dsid, outputName ):
        orecMap =  self.outputRecs.get( dsid, None )
        if orecMap: del orecMap[outputName] 

    def addOutputRec( self, dsid, orec ): 
        orecMap =  self.outputRecs.setdefault( dsid, {} )
        orecMap[ orec.name ] = orec

    def getOutputRec( self, dsid, outputName ):
        orecMap =  self.outputRecs.get( dsid, None )
        return orecMap[ outputName ] if orecMap else None

    def getOutputRecNames( self, dsid  ): 
        orecMap =  self.outputRecs.get( dsid, None )
        return orecMap.keys() if orecMap else []

    def getOutputRecs( self, dsid ):
        orecMap =  self.outputRecs.get( dsid, None )
        return orecMap.values() if orecMap else []
    
class OutputRec:
    
    def __init__(self, name, **args ): 
        self.name = name
        self.varComboList = args.get( "varComboList", [] )
        self.levelsCombo = args.get( "levelsCombo", None )
        self.level = args.get( "level", None )
        self.varTable = args.get( "varTable", None )
        self.varList = args.get( "varList", None )
        self.varSelections = args.get( "varSelections", [] )
        self.type = args.get( "type", None )
        self.ndim = args.get( "ndim", 3 )
        self.updateSelections() 

    def getVarList(self):
        vlist = []
        for vrec in self.varList:
            vlist.append( str( getItem( vrec ) ) )
        return vlist
    
    def getSelectedVariableList(self):
        return [ str( varCombo.currentText() ) for varCombo in self.varComboList ]

    def getSelectedLevel(self):
        return str( self.levelsCombo.currentText() ) if self.levelsCombo else None
    
    def updateSelections(self):
        self.varSelections = []
        for varCombo in self.varComboList:
            varSelection = str( varCombo.currentText() ) 
            self.varSelections.append( [ varSelection, "" ] )

       
def getFloatStr( val ):
    if ( type(val) == type(' ') ): return val
    return "%.1f" % val

def extractMetadata( fieldData ):
    mdList = []
    inputVarList = []
    varlist = fieldData.GetAbstractArray( 'varlist' ) 
    if varlist == None:   # module.getFieldData() 
        print>>sys.stderr, " Can't get Metadata!" 
    else: 
        nvar = varlist.GetNumberOfValues()
        for vid in range(nvar):
            varName = str( varlist.GetValue(vid) )
            inputVarList.append( varName )
            dataVector = fieldData.GetAbstractArray( 'metadata:%s' % varName ) 
            if dataVector == None:  
                print>>sys.stderr, " Can't get Metadata for var %s!" % varName 
            else: 
                metadata = {}
                nval = dataVector.GetNumberOfValues()
                for id in range(nval):
                    enc_mdata = str( dataVector.GetValue(id) )
                    md = decodeFromString( enc_mdata )
                    metadata.update( md )
                mdList.append( metadata )
        for md in mdList: md['inputVarList'] = inputVarList
    return mdList 
            
def freeImageData( image_data ):
    from packages.vtDV3D.vtUtilities import memoryLogger
    memoryLogger.log("start freeImageData")
    pointData = image_data.GetPointData()
    for aIndex in range( pointData.GetNumberOfArrays() ):
 #       array = pointData.GetArray( aIndex )
        pointData.RemoveArray( aIndex )
#        if array:
#            name = pointData.GetArrayName(aIndex)            
#            print "---- freeImageData-> Removing array %s: %s" % ( name, array.__class__.__name__ )  
    fieldData = image_data.GetFieldData()
    for aIndex in range( fieldData.GetNumberOfArrays() ): 
        aname = fieldData.GetArrayName(aIndex)
        array = fieldData.GetArray( aname )
        if array:
            array.Initialize()
            fieldData.RemoveArray( aname )
    image_data.ReleaseData()
    memoryLogger.log("finished freeImageData")
    
class DataCache():
    
    def __init__(self):
        self.data = {}
        self.cells = set()

class CachedImageData():
    
    def __init__(self, image_data, cell_coords ):
        self.data = image_data
        self.cells = set()
        self.cells.add( cell_coords )

def getRoiSize( roi ):
    if roi == None: return 0
    return abs((roi[2]-roi[0])*(roi[3]-roi[1]))

def getTitle( dsid, name, attributes, showUnits=False ):
       long_name = attributes.get( 'long_name', attributes.get( 'standard_name', name ) )
       if not showUnits: return "%s:%s" % ( dsid, long_name )
       units = attributes.get( 'units', 'unitless' )
       return  "%s:%s (%s)" % ( dsid, long_name, units )
   
def isDesignated( axis ):
    return ( axis.isLatitude() or axis.isLongitude() or axis.isLevel() or axis.isTime() )

def matchesAxisType( axis, axis_attr, axis_aliases ):
    matches = False
    aname = axis.id.lower()
    axis_attribute = axis.attributes.get('axis',None)
    if axis_attribute and ( axis_attribute.lower() in axis_attr ):
        matches = True
    else:
        for axis_alias in axis_aliases:
            if ( aname.find( axis_alias ) >= 0): 
                matches = True
                break
    return matches

class AxisType:
    NONE = 0
    Time = 1
    Longitude = 2
    Latitude = 3
    Level = 4
    lev_aliases = [ 'bottom', 'top', 'zdim' ]
    lev_axis_attr = [ 'z' ]
    lat_aliases = [ 'north', 'south', 'ydim' ]
    lat_axis_attr = [ 'y' ]
    lon_aliases = [ 'east', 'west', 'xdim' ]
    lon_axis_attr = [ 'x' ]

def getAxisType( axis ):
    if axis.isLevel() or matchesAxisType( axis, AxisType.lev_axis_attr, AxisType.lev_aliases ):
        return AxisType.Level      
    elif axis.isLatitude() or matchesAxisType( axis, AxisType.lat_axis_attr, AxisType.lat_aliases ):
        return AxisType.Latitude                   
    elif axis.isLongitude() or matchesAxisType( axis, AxisType.lon_axis_attr, AxisType.lon_aliases ):
        return AxisType.Longitude     
    elif axis.isTime():
        return AxisType.Time
    else: return  AxisType.NONE    

def designateAxisType( self, axis ):
    if not isDesignated( axis ):
        if matchesAxisType( axis, AxisType.lev_axis_attr, AxisType.lev_aliases ):
            axis.designateLevel() 
            return AxisType.Level         
        elif matchesAxisType( axis, AxisType.lat_axis_attr, AxisType.lat_aliases ):
            axis.designateLatitude() 
            return AxisType.Latitude                    
        elif matchesAxisType( axis, AxisType.lon_axis_attr, AxisType.lon_aliases ):
            axis.designateLongitude()
            return AxisType.Longitude    
    return getAxisType( axis )


class InputSpecs:
    
    def __init__( self, **args ):
        self.units = ''
        self.scalarRange = None
        self.seriesScalarRange = None
        self.rangeBounds = None
        self.referenceTimeUnits = None
        self.metadata = None
        self._input = None
        self.fieldData = None
        self.datasetId = None
        self.clipper = None
        self.dtype = None
        
    def isFloat(self):
        return self.dtype == "Float"

#     def selectInputArray( self, raw_input, plotIndex ):
#         self.updateMetadata( plotIndex )
#         old_point_data = raw_input.GetPointData()  
#         nArrays = old_point_data.GetNumberOfArrays() 
#         if nArrays == 1: return raw_input  
#         image_data = vtk.vtkImageData()
#         image_data.ShallowCopy( raw_input )
#         new_point_data = image_data.GetPointData()        
#         array_index = plotIndex if plotIndex < nArrays else 0
#         inputVarList = self.metadata.get( 'inputVarList', [] )
#         if array_index < len( inputVarList ):
#             aname = inputVarList[ array_index ] 
#             new_point_data.SetActiveScalars( aname )
# #            print "Selecting scalars array %s for input %d" % ( aname, array_index )
#         else:
#             print>>sys.stderr, "Error, can't find scalars array for input %d" % array_index
# #        print "Selecting %s (array-%d) for plot index %d" % ( aname, array_index, plotIndex)
#         return image_data
 
    def initializeInput( self, imageData, fieldData, plotIndex=0 ): 
        self._input =  imageData 
        self.fieldData = fieldData                          
        self.updateMetadata( plotIndex )
        
    def input( self ):
        if self.clipper:
            input = self.clipper.GetOutput()
            input.Update()
            return input
        return self._input
        
    def clipInput( self, extent ):
        self.clipper = vtk.vtkImageClip()
        self.clipper.AddInput( self._input )
        self.clipper.SetOutputWholeExtent( extent )

    def getWorldCoords( self, image_coords ):
        plotType = self.metadata[ 'plotType' ]                   
        world_coords = None
        try:
            if plotType == 'zyt':
                lat = self.metadata[ 'lat' ]
                lon = self.metadata[ 'lon' ]
                timeAxis = self.metadata[ 'time' ]
                tval = timeAxis[ image_coords[2] ]
                relTimeValue = cdtime.reltime( float( tval ), timeAxis.units ) 
                timeValue = str( relTimeValue.tocomp() )          
                world_coords = [ getFloatStr(lon[ image_coords[0] ]), getFloatStr(lat[ image_coords[1] ]), timeValue ]   
            else:         
                lat = self.metadata[ 'lat' ]
                lon = self.metadata[ 'lon' ]
                lev = self.metadata[ 'lev' ]
                world_coords = [ getFloatStr(lon[ image_coords[0] ]), getFloatStr(lat[ image_coords[1] ]), getFloatStr(lev[ image_coords[2] ]) ]   
        except:
            gridSpacing = self.input().GetSpacing()
            gridOrigin = self.input().GetOrigin()
            world_coords = [ getFloatStr(gridOrigin[i] + image_coords[i]*gridSpacing[i]) for i in range(3) ]
        return world_coords

    def getWorldCoordsAsFloat( self, image_coords ):
        plotType = self.metadata[ 'plotType' ]                   
        world_coords = None
        try:
            if plotType == 'zyt':
                lat = self.metadata[ 'lat' ]
                lon = self.metadata[ 'lon' ]
                timeAxis = self.metadata[ 'time' ]
                tval = timeAxis[ image_coords[2] ]
                relTimeValue = cdtime.reltime( float( tval ), timeAxis.units ) 
                timeValue = str( relTimeValue.tocomp() )          
                world_coords = [ lon[ image_coords[0] ], lat[ image_coords[1] ], timeValue ]   
            else:         
                lat = self.metadata[ 'lat' ]
                lon = self.metadata[ 'lon' ]
                lev = self.metadata[ 'lev' ]
                world_coords = [ lon[ image_coords[0] ], lat[ image_coords[1] ], lev[ image_coords[2] ] ]   
        except:
            gridSpacing = self.input().GetSpacing()
            gridOrigin = self.input().GetOrigin()
            world_coords = [ gridOrigin[i] + image_coords[i]*gridSpacing[i] for i in range(3) ]
        return world_coords
    
    def getWorldCoord( self, image_coord, iAxis, latLonGrid  ):
        plotType = self.metadata[ 'plotType' ] 
        if plotType == 'zyt':                  
            axisNames = [ 'Longitude', 'Latitude', 'Time' ] if latLonGrid else [ 'X', 'Y', 'Time' ]
        else:
            axisNames =  [ 'Longitude', 'Latitude', 'Level' ] if latLonGrid else [ 'X', 'Y', 'Level' ]
        try:
            axes = [ 'lon', 'lat', 'time' ] if plotType == 'zyt'  else [ 'lon', 'lat', 'lev' ]
            world_coord = self.metadata[ axes[iAxis] ][ image_coord ]
            if ( plotType == 'zyt') and  ( iAxis == 2 ):
                timeAxis = self.metadata[ 'time' ]     
                timeValue = cdtime.reltime( float( world_coord ), timeAxis.units ) 
                world_coord = str( timeValue.tocomp() )          
            return axisNames[iAxis], getFloatStr( world_coord )
        except:
            if (plotType == 'zyx') or (iAxis < 2):
                gridSpacing = self.input().GetSpacing()
                gridOrigin = self.input().GetOrigin()
                return axes[iAxis], getFloatStr( gridOrigin[iAxis] + image_coord*gridSpacing[iAxis] ) 
            return axes[iAxis], ""

    def getRangeBounds( self ):
        if self.dtype == "Float": 
            return self.scalarRange
        return self.rangeBounds  
        
    def getDataRangeBounds(self):
        if self.dtype == "Float":
            return self.scalarRange
        if self.rangeBounds:
            srange = self.getDataValues( self.rangeBounds[0:2] ) 
            if ( len( self.rangeBounds ) > 2 ): srange.append( self.rangeBounds[2] ) 
            else:                               srange.append( 0 )
        else: srange = [ 0, 0, 0 ]
        return srange
    
    def getScalarRange(self): 
        return self.scalarRange
    
    def raiseModuleError( self, msg ):
        print>>sys.stderr, msg
        raise Exception( msg )

    def getDataValue( self, image_value):
        if self.isFloat(): return image_value
        if not self.scalarRange: 
            self.raiseModuleError( "ERROR: no variable selected in dataset input to module %s" % getClassName( self ) )
        valueRange = self.scalarRange
        sval = ( float(image_value) - self.rangeBounds[0] ) / ( self.rangeBounds[1] - self.rangeBounds[0] )
        dataValue = valueRange[0] + sval * ( valueRange[1] - valueRange[0] ) 
#        print " GetDataValue(%.3G): valueRange = %s " % ( sval, str( valueRange ) )
        return dataValue
                
    def getDataValues( self, image_value_list ):
        if self.isFloat(): return image_value_list
        if not self.scalarRange: 
            self.raiseModuleError( "ERROR: no variable selected in dataset input to module %s" % getClassName( self ) )
        valueRange = self.scalarRange
        dr = ( self.rangeBounds[1] - self.rangeBounds[0] )
        data_values = []
        for image_value in image_value_list:
            sval = 0.0 if ( dr == 0.0 ) else ( image_value - self.rangeBounds[0] ) / dr
            dataValue = valueRange[0] + sval * ( valueRange[1] - valueRange[0] ) 
            data_values.append( dataValue )
        return data_values

    def getImageValue( self, data_value ):
        if not self.scalarRange: 
            self.raiseModuleError( "ERROR: no variable selected in dataset input to module %s" % getClassName( self ) )
        valueRange = self.scalarRange
        dv = ( valueRange[1] - valueRange[0] )
        sval = 0.0 if ( dv == 0.0 ) else ( data_value - valueRange[0] ) / dv 
        imageValue = self.rangeBounds[0] + sval * ( self.rangeBounds[1] - self.rangeBounds[0] ) 
        return imageValue

    def getImageValues( self, data_value_list ):
        if self.isFloat(): return data_value_list
        if not self.scalarRange: 
            self.raiseModuleError( "ERROR: no variable selected in dataset input to module %s" % getClassName( self ) )
        valueRange = self.scalarRange
        dv = ( valueRange[1] - valueRange[0] )
        imageValues = []
        for data_value in data_value_list:
            sval = 0.0 if ( dv == 0.0 ) else ( data_value - valueRange[0] ) / dv
            imageValue = self.rangeBounds[0] + sval * ( self.rangeBounds[1] - self.rangeBounds[0] ) 
            imageValues.append( imageValue )
#        print "\n *****************  GetImageValues: data_values = %s, range = %s, imageValues = %s **************** \n" % ( str(data_value_list), str(self.scalarRange), str(imageValues) )
        return imageValues

    def scaleToImage( self, data_value ):
        if self.isFloat(): return data_value
        if not self.scalarRange: 
            self.raiseModuleError( "ERROR: no variable selected in dataset input to module %s" % getClassName( self ) )
        dv = ( self.scalarRange[1] - self.scalarRange[0] )
        sval = 0.0 if ( dv == 0.0 ) else data_value / dv
        imageScaledValue =  sval * ( self.rangeBounds[1] - self.rangeBounds[0] ) 
        return imageScaledValue

    def getMetadata( self, key = None ):
        return self.metadata.get( key, None ) if ( key and self.metadata )  else self.metadata
  
    def getFieldData( self ):
        if self.fieldData == None:
            print>>sys.stderr, ' Uninitialized field data being accessed in ispec[%x]  ' % id(self)  
            self.initializeMetadata()
        return self.fieldData  
    
    def updateMetadata( self, plotIndex ):
        if self.metadata == None:
            scalars = None
             
#            arr_names = [] 
#            na = self.fieldData.GetNumberOfArrays()
#            for iF in range( na ):
#                arr_names.append( self.fieldData.GetArrayName(iF) )
#            print " updateMetadata: getFieldData, arrays = ", str( arr_names ) ; sys.stdout.flush()
            
            if self.fieldData == None:
                print>>sys.stderr,  ' NULL field data in updateMetadata: ispec[%x]  ' % id(self)  
                self.initializeMetadata() 
    
            self.metadata = self.computeMetadata( plotIndex )
            
            if self.metadata <> None:
                self.rangeBounds = None              
                self.datasetId = self.metadata.get( 'datasetId', None )                
                tval = self.metadata.get( 'timeValue', 0.0 )
                self.referenceTimeUnits = self.metadata.get( 'timeUnits', None )
                self.timeValue = cdtime.reltime( float( tval ), self.referenceTimeUnits )               
                self.dtype =  self.metadata.get( 'datatype', None )
                scalars =  self.metadata.get( 'scalars', None )
                self.rangeBounds = getRangeBounds( self.dtype )
                title = self.metadata.get( 'title', None )
                if title:
                    targs = title.split(':')
                    if len( targs ) == 1:
                        self.titleBuffer = "\n%s" % ( title )
                    elif len( targs ) > 1:
                        self.titleBuffer = "%s\n%s" % ( targs[1], targs[0] )
                else: self.titleBuffer = "" 
                attributes = self.metadata.get( 'attributes' , None )
                if attributes:
                    self.units = attributes.get( 'units' , '' )
                    srange = attributes.get( 'range', None )
                    if srange: 
        #                print "\n ***************** ScalarRange = %s, md[%d], var_md[%d] *****************  \n" % ( str(range), id(metadata), id(var_md) )
                        self.scalarRange = list( srange )
                        self.scalarRange.append( 1 )
                        if not self.seriesScalarRange:
                            self.seriesScalarRange = list(srange)
                        else:
                            if self.seriesScalarRange[0] > srange[0]:
                                self.seriesScalarRange[0] = srange[0] 
                            if self.seriesScalarRange[1] < srange[1]:
                                self.seriesScalarRange[1] = srange[1] 

    def getUnits(self):
        return self.units
    
    def getLayerList(self):
        layerList = []
        pointData = self.input().GetPointData()
        for iA in range( pointData.GetNumberOfArrays() ):
            array_name = pointData.GetArrayName(iA)
            if array_name: layerList.append( array_name )
        return layerList
    
    def computeMetadata( self, plotIndex=0 ):
        if not self.fieldData: self.initializeMetadata() 
        if self.fieldData:
            mdList = extractMetadata( self.fieldData )
            if plotIndex < len(mdList):
                return mdList[ plotIndex ]
            else:
                try: return mdList[ 0 ]
                except: pass               
        print>>sys.stderr, "[%s]: Error, Metadata for input %d not found in ispec[%x]  "  % ( self.__class__.__name__,  plotIndex, id(self) )
        return {}
        
    def addMetadataObserver( self, caller, event ):
        fd = caller.GetOutput().GetFieldData()
        fd.ShallowCopy( self.fieldData )
        pass

    def initializeMetadata( self ):
        try:
            self.fieldData = vtk.vtkDataSetAttributes()
            mdarray = getStringDataArray( 'metadata' )
            self.fieldData.AddArray( mdarray )
#            diagnosticWriter.log( self, ' initialize field data in ispec[%x]  ' % id(self) )  
        except Exception, err:
            print>>sys.stderr, "Error initializing metadata"

    def addMetadata( self, metadata ):
        dataVector = self.fieldData.GetAbstractArray( 'metadata' ) 
        if dataVector == None:
            cname = getClassName( self ) 
            if cname <> "InputSpecs": print " Can't get Metadata for class %s " % cname
        else:
            enc_mdata = encodeToString( metadata )
            dataVector.InsertNextValue( enc_mdata  )
                   
class StructuredDataReader:
    
    dataCache = {}
    imageDataCache = {}

    def __init__(self, init_specs, **args):
        self.datasetId = init_specs[1]
        self.fileSpecs = init_specs[1]
        self.varSpecs = init_specs[3]
        self.gridSpecs = init_specs[4]
        self.referenceTimeUnits = None
        self.parameters = {}
        self.currentTime = 0
        self.currentLevel = None
        self.timeIndex = 0
        self.timeValue = None
        self.useTimeIndex = False
        self.timeAxis = None
        self.fieldData = None
        self.df = cdms2.open( self.fileSpecs ) 
        self.var =  self.df( self.varSpecs )
        self.outputType = args.get( 'output_type', CDMSDataType.Volume )
# #        memoryLogger.log("Init CDMSDataReader")
#         if self.outputType == CDMSDataType.Hoffmuller:
#             self.addUVCDATConfigGuiFunction( 'chooseLevel', LevelConfigurationDialog, 'L', label='Choose Level' ) 
            
    def getTimeAxis(self):
        return self.timeAxis
       
    def getCachedImageData( self, data_id ):
        return self.imageDataCache.get( data_id, None )

    def setCachedImageData( self, data_id, image_data ):
        self.imageDataCache[data_id] = image_data

    @classmethod
    def clearCache( cls, cell_coords ):
        from packages.vtDV3D.vtUtilities import memoryLogger
        memoryLogger.log("start VolumeRader.clearCache")
        for dataCacheItems in cls.dataCache.items():
            dataCacheKey = dataCacheItems[0]
            dataCacheObj = dataCacheItems[1]
            if cell_coords in dataCacheObj.cells:
                dataCacheObj.cells.remove( cell_coords )
                if len( dataCacheObj.cells ) == 0:
                    varDataMap = dataCacheObj.data.get('varData', None )
                    if varDataMap:
                        newDataArray = varDataMap.get( 'newDataArray', None  )
                        try:
                            varDataMap['newDataArray' ] = None
                            del newDataArray
                        except Exception, err:
                            print>>sys.stderr, "Error releasing variable data: ", str(err)
                    dataCacheObj.data['varData'] = None
                    del cls.dataCache[ dataCacheKey ]
                    print "Removing Cached data: ", str( dataCacheKey )
        memoryLogger.log(" finished clearing data cache ")
        for imageDataItem in cls.imageDataCache.items():
            freeImageData( imageDataItem[1] )
        memoryLogger.log("finished clearing image cache")
        
    def getCachedData( self, varDataId, cell_coords ):
        dataCacheObj = self.dataCache.setdefault( varDataId, DataCache() )
        data = dataCacheObj.data.get( 'varData', None )
        if data: dataCacheObj.cells.add( cell_coords )
        return data

    def setCachedData(self, varDataId, cell_coords, varDataMap ):
        dataCacheObj = self.dataCache.setdefault( varDataId, DataCache() )
        dataCacheObj.data[ 'varData' ] = varDataMap
        dataCacheObj.cells.add( cell_coords )
                
    def getParameterDisplay( self, parmName, parmValue ):
        if parmName == 'timestep':
#            timestep = self.getTimeIndex( int( parmValue[0] ) )
            timestep = int( parmValue[0] )
            try:    return str( self.timeLabels[ timestep ] ), 10
            except: pass
        return None, 1

    def addCDMSVariable( self, cdms_var, index ):
        varname = cdms_var.id
        self.cdmsDataset.addTransientVariable( varname, cdms_var )
        self.cdmsDataset.setVariableRecord( "VariableName%d" % index, '*'.join( [ self.datasetId, varname ] ) )
        return cdms_var
    
    def designateAxes(self,var):
        lev_aliases = [ 'bottom', 'top', 'zdim', 'level' ]
        lev_axis_attr = [ 'z' ]
        lat_aliases = [ 'north', 'south', 'ydim' ]
        lat_axis_attr = [ 'y' ]
        lon_aliases = [ 'east', 'west', 'xdim' ]
        lon_axis_attr = [ 'x' ]
        latLonGrid = True
        for axis in var.getAxisList():
            if not isDesignated( axis ):
                if matchesAxisType( axis, lev_axis_attr, lev_aliases ):
                    axis.designateLevel()
                    print " --> Designating axis %s as a Level axis " % axis.id            
                elif matchesAxisType( axis, lat_axis_attr, lat_aliases ):
                    axis.designateLatitude()
                    print " --> Designating axis %s as a Latitude axis " % axis.id 
                    latLonGrid = False                     
                elif matchesAxisType( axis, lon_axis_attr, lon_aliases ):
                    axis.designateLongitude()
                    print " --> Designating axis %s as a Longitude axis " % axis.id 
                    latLonGrid = False 
            elif ( axis.isLatitude() or axis.isLongitude() ):
                if ( axis.id.lower()[0] == 'x' ) or ( axis.id.lower()[0] == 'y' ):
                    latLonGrid = False 
        return latLonGrid
    
    def setParameter( self, key , value ):
        self.parameters[key] = value

    def getParameter( self, key ):
        return self.parameters.get(key, None )

    def setupTimeAxis( self, var, **args ):
        self.nTimesteps = 1
        self.timeRange = [ 0, self.nTimesteps, 0.0, 0.0 ]
        self.timeAxis = var.getTime()
        if self.timeAxis:
            self.nTimesteps = len( self.timeAxis ) if self.timeAxis else 1
            try:
                if self.referenceTimeUnits == None: self.referenceTimeUnits = self.timeAxis.units
                comp_time_values = self.timeAxis.asComponentTime()
                t0 = comp_time_values[0].torel(self.referenceTimeUnits).value
                if (t0 < 0):
                    self.referenceTimeUnits = self.timeAxis.units
                    t0 = comp_time_values[0].torel(self.referenceTimeUnits).value
                dt = 0.0
                if self.nTimesteps > 1:
                    t1 = comp_time_values[-1].torel(self.referenceTimeUnits).value
                    dt = (t1-t0)/(self.nTimesteps-1)
                    self.timeRange = [ 0, self.nTimesteps, t0, dt ]
            except:
                values = self.timeAxis.getValue()
                t0 = values[0] if len(values) > 0 else 0
                t1 = values[-1] if len(values) > 1 else t0
                dt = ( values[1] - values[0] )/( len(values) - 1 ) if len(values) > 1 else 0
                self.timeRange = [ 0, self.nTimesteps, t0, dt ]
        self.setParameter( "timeRange" , self.timeRange )
        self.cdmsDataset.timeRange = self.timeRange
        self.cdmsDataset.referenceTimeUnits = self.referenceTimeUnits
        self.timeLabels = self.cdmsDataset.getTimeValues()
        timeData = args.get( 'timeData', [ self.cdmsDataset.timeRange[2], 0, False ] )
        if timeData:
            self.timeValue = cdtime.reltime( float(timeData[0]), self.referenceTimeUnits )
            self.timeIndex = timeData[1]
            self.useTimeIndex = timeData[2]
        else:
            self.timeValue = cdtime.reltime( t0, self.referenceTimeUnits )
            self.timeIndex = 0
            self.useTimeIndex = False
#            print "Set Time [mid = %d]: %s, NTS: %d, Range: %s, Index: %d (use: %s)" % ( self.moduleID, str(self.timeValue), self.nTimesteps, str(self.timeRange), self.timeIndex, str(self.useTimeIndex) )
#            print "Time Step Labels: %s" % str( self.timeLabels )
           
    def execute(self, **args ):
        import api
        from packages.vtDV3D.CDMS_DatasetReaders import CDMSDataset
        cdms_vars = [ self.var ]
        iVar = 1
        cdms_var = cdms_vars.pop(0)
        self.cdmsDataset = CDMSDataset()
        var = self.addCDMSVariable( cdms_var, iVar )
        self.newDataset = False
#            if self.newDataset: ModuleStore.archiveCdmsDataset( dsetId, self.cdmsDataset )
        self.newLayerConfiguration = self.newDataset
        self.cdmsDataset.latLonGrid = self.designateAxes(var)
        self.setupTimeAxis( var, **args )
        intersectedRoi = self.cdmsDataset.gridBounds
        intersectedRoi = self.getIntersectedRoi( cdms_var, intersectedRoi )
        while( len(cdms_vars) ):
            cdms_var2 = cdms_vars.pop(0)
            if cdms_var2: 
                iVar = iVar+1
                self.addCDMSVariable( cdms_var2, iVar )
                intersectedRoi = self.getIntersectedRoi( cdms_var2, intersectedRoi )
              
#         for iVarInputIndex in range( 2,5 ):
#             cdms_var2 = self.getInputValue( "variable%d" % iVarInputIndex  ) 
#             if cdms_var2: 
#                 iVar = iVar+1
#                 self.addCDMSVariable( cdms_var2, iVar )
#                 intersectedRoi = self.getIntersectedRoi( cdms_var2, intersectedRoi )
                
        if hasattr(cdms_var,'url'): self.generateOutput( roi=intersectedRoi, url=cdms_var.url )
        else:                       self.generateOutput( roi=intersectedRoi )
 
            
    def getParameterId(self):
        return self.datasetId
            
    def getPortData( self, **args ):
        return self.getInputValue( "portData", **args )  

    def generateVariableOutput( self, cdms_var ): 
        print str(cdms_var.var)
        self.set3DOutput( name=cdms_var.name,  output=cdms_var.var )

    def refreshVersion(self):
        portData = self.getPortData()
        if portData:
            portDataVersion = portData[1] + 1
            serializedPortData = portData[0]
            self.persistParameter( 'portData', [ serializedPortData, portDataVersion ] )
        
    def getOutputRecord( self, ndim = -1 ):
        portData = self.getPortData()
        if portData:
            oRecMgr = OutputRecManager( portData[0]  )
            orecs = oRecMgr.getOutputRecs( self.datasetId ) if oRecMgr else None
            if not orecs: raise Exception( 'No Variable selected for dataset %s.' % self.datasetId )             
            for orec in orecs:
                if (ndim < 0 ) or (orec.ndim == ndim): return orec
        return None
             
    def generateOutput( self, **args ): 
        oRecMgr = None 
        varRecs = self.cdmsDataset.getVarRecValues()
        cell_coords = [ 0, 0 ]
        if len( varRecs ):
#            print " VolumeReader->generateOutput, varSpecs: ", str(varRecs)
            oRecMgr = OutputRecManager() 
#            varCombo = QComboBox()
#            for var in varRecs: varCombo.addItem( str(var) ) 
            otype = 'volume'
            orec = OutputRec( otype, ndim=3, varList=varRecs )   
            oRecMgr.addOutputRec( self.datasetId, orec ) 
        else:
            portData = self.getPortData()
            if portData:
#                print " VolumeReader->generateOutput, portData: ", portData
                oRecMgr = OutputRecManager( portData[0]  )
        orecs = oRecMgr.getOutputRecs( self.datasetId ) if oRecMgr else None
        if not orecs: raise Exception( 'No Variable selected for dataset %s.' % self.datasetId ) 
        self.output_names = [] 
        self.outputSpecs = []           
        for orec in orecs:
            cachedImageDataName = self.getImageData( orec, **args ) 
            self.output_names.append( cachedImageDataName )
            ispec = InputSpecs()
            ispec.initializeInput( self.getCachedImageData( cachedImageDataName ), self.getFieldData() )
            self.outputSpecs.append( ispec )
#                 if cachedImageDataName: 
#                     cachedImageData = self.getCachedImageData( cachedImageDataName )            
#                     if   orec.ndim >= 3: self.set3DOutput( name=orec.name,  output=cachedImageData )
#                     elif orec.ndim == 2: self.set2DOutput( name=orec.name,  output=cachedImageData )
        self.currentTime = self.getTimestep()

    def output( self, iIndex=0 ):
        cachedImageDataName = self.output_names[ iIndex ]
        cachedImageData = self.getCachedImageData( cachedImageDataName ) 
        return cachedImageData

    def outputSpec( self, iIndex=0 ):
        return self.outputSpecs[ iIndex ]
    
    def nOutputs(self):
        return len( self.outputSpecs )
     
    def getTimestep( self ):
        dt = self.timeRange[3]
        return 0 if dt <= 0.0 else int( round( ( self.timeValue.value - self.timeRange[2] ) / dt ) )

    def setCurrentLevel(self, level ): 
        self.currentLevel = level

    def getFileMetadata( self, orec, **args ):
        varList = orec.varList
        if len( varList ) == 0: return False
        varDataIds = []
        intersectedRoi = args.get('roi', None )
        url = args.get('url', None )
        if intersectedRoi: self.cdmsDataset.setRoi( intersectedRoi )
        dsid = None
        fieldData = self.getFieldData()
        if fieldData:
            na = fieldData.GetNumberOfArrays()
            for ia in range(na):
                aname = fieldData.GetArrayName(ia)
                if (aname <> None) and aname.startswith('metadata'):
                    fieldData.RemoveArray(aname)
        vars = []
        for varRec in varList:
            range_min, range_max, scale, shift  = 0.0, 0.0, 1.0, 0.0   
            imageDataName = getItem( varRec )
            varNameComponents = imageDataName.split('*')
            if len( varNameComponents ) == 1:
                dsid = self.cdmsDataset.getReferenceDsetId() 
                varName = varNameComponents[0]
            else:
                dsid = varNameComponents[0]
                varName = varNameComponents[1]
            ds = self.cdmsDataset[ dsid ]
            if ds:
                var = ds.getVariable( varName )
                self.setupTimeAxis( var, **args )
            portName = orec.name
            selectedLevel = orec.getSelectedLevel() if ( self.currentLevel == None ) else self.currentLevel
            ndim = 3 if ( orec.ndim == 4 ) else orec.ndim
            default_dtype = np.float
            scalar_dtype = args.get( "dtype", default_dtype )
            self._max_scalar_value = getMaxScalarValue( scalar_dtype )
            self._range = [ 0.0, self._max_scalar_value ]  
            datatype = getDatatypeString( scalar_dtype )
            if (self.outputType == CDMSDataType.Hoffmuller):
                if ( selectedLevel == None ):
                    varDataIdIndex = 0
                else:
                    varDataIdIndex = selectedLevel  
                                      
            iTimestep = self.timeIndex if ( varName <> '__zeros__' ) else 0
            varDataIdIndex = iTimestep  
            roiStr = ":".join( [ ( "%.1f" % self.cdmsDataset.gridBounds[i] ) for i in range(4) ] ) if self.cdmsDataset.gridBounds else ""
            varDataId = '%s;%s;%d;%s;%s' % ( dsid, varName, self.outputType, str(varDataIdIndex), roiStr )
            vmd = {}         
            vmd[ 'dsid' ] = dsid 
            vmd[ 'file' ] = url if url else dsid              
            vmd[ 'varName' ] = varName                 
            vmd[ 'outputType' ] = self.outputType                 
            vmd[ 'varDataIdIndex' ] = varDataIdIndex
            vmd['datatype'] = datatype
            vmd['timeIndex']= iTimestep
            vmd['timeValue']= self.timeValue.value
            vmd['latLonGrid']= self.cdmsDataset.latLonGrid
            vmd['timeUnits' ] = self.referenceTimeUnits 
            vmd[ 'bounds' ] = self.cdmsDataset.gridBounds          
            enc_mdata = encodeToString( vmd ) 
            if enc_mdata and fieldData: 
                fieldData.AddArray( getStringDataArray( 'metadata:%s' % varName,   [ enc_mdata ]  ) ) 
                vars.append( varName )                   
        fieldData.AddArray( getStringDataArray( 'varlist',  vars  ) )                       

    def getFieldData( self ):
        if self.fieldData == None:
            self.initializeMetadata()
        return self.fieldData  

    def initializeMetadata( self ):
        try:
            self.fieldData = vtk.vtkDataSetAttributes()
            mdarray = getStringDataArray( 'metadata' )
            self.fieldData.AddArray( mdarray )
        except Exception, err:
            print>>sys.stderr, "Error initializing metadata"

    def addMetadata( self, metadata ):
        dataVector = self.fieldData.GetAbstractArray( 'metadata' ) 
        enc_mdata = encodeToString( metadata )
        dataVector.InsertNextValue( enc_mdata  )
               
    def getImageData( self, orec, **args ):
        """
        This method converts cdat data into vtkImageData objects. The ds object is a CDMSDataset instance which wraps a CDAT CDMS Dataset object. 
        The ds.getVarDataCube method execution extracts a CDMS variable object (varName) and then cuts out a data slice with the correct axis ordering (returning a NumPy masked array).   
        The array is then rescaled, converted to a 1D unsigned short array, and then wrapped as a vtkUnsignedShortArray using the vtkdata.SetVoidArray method call.  
        The vtk data array is then attached as point data to a vtkImageData object, which is returned.
        The CDAT metadata is serialized, wrapped as a vtkStringArray, and then attached as field data to the vtkImageData object.  
        """
        varList = orec.varList
        npts = -1
        if len( varList ) == 0: return False
        varDataIds = []
        intersectedRoi = args.get('roi', None )
        if intersectedRoi: self.cdmsDataset.setRoi( intersectedRoi )
        exampleVarDataSpecs = None
        dsid = None
        if (self.outputType == CDMSDataType.Vector ) and len(varList) < 3:
            if len(varList) == 2: 
                imageDataName = getItem( varList[0] )
                dsid = imageDataName.split('*')[0]
                varList.append( '*'.join( [ dsid, '__zeros__' ] ) )
            else: 
                print>>sys.stderr, "Not enough components for vector plot: %d" % len(varList)
#        print " Get Image Data: varList = %s " % str( varList )
        for varRec in varList:
            range_min, range_max, scale, shift  = 0.0, 0.0, 1.0, 0.0   
            imageDataName = getItem( varRec )
            varNameComponents = imageDataName.split('*')
            if len( varNameComponents ) == 1:
                dsid = self.cdmsDataset.getReferenceDsetId() 
                varName = varNameComponents[0]
            else:
                dsid = varNameComponents[0]
                varName = varNameComponents[1]
            ds = self.cdmsDataset[ dsid ]
            if ds:
                var = ds.getVariable( varName )
                self.setupTimeAxis( var, **args )
            portName = orec.name
            selectedLevel = orec.getSelectedLevel() if ( self.currentLevel == None ) else self.currentLevel
            ndim = 3 if ( orec.ndim == 4 ) else orec.ndim
            default_dtype = np.float32
            scalar_dtype = args.get( "dtype", default_dtype )
            self._max_scalar_value = getMaxScalarValue( scalar_dtype )
            self._range = [ 0.0, self._max_scalar_value ]  
            datatype = getDatatypeString( scalar_dtype )
            if (self.outputType == CDMSDataType.Hoffmuller):
                if ( selectedLevel == None ):
                    varDataIdIndex = 0
                else:
                    varDataIdIndex = selectedLevel  
                                      
            iTimestep = self.timeIndex if ( varName <> '__zeros__' ) else 0
            varDataIdIndex = iTimestep  
            cell_coords = (0,0)
            roiStr = ":".join( [ ( "%.1f" % self.cdmsDataset.gridBounds[i] ) for i in range(4) ] ) if self.cdmsDataset.gridBounds else ""
            varDataId = '%s;%s;%d;%s;%s' % ( dsid, varName, self.outputType, str(varDataIdIndex), roiStr )
            varDataIds.append( varDataId )
            varDataSpecs = self.getCachedData( varDataId, cell_coords ) 
            flatArray = None
            if varDataSpecs == None:
                if varName == '__zeros__':
                    assert( npts > 0 )
                    newDataArray = np.zeros( npts, dtype=scalar_dtype ) 
                    varDataSpecs = copy.deepcopy( exampleVarDataSpecs )
                    varDataSpecs['newDataArray'] = newDataArray.ravel('F')  
                    self.setCachedData( varName, cell_coords, varDataSpecs ) 
                else: 
                    tval = None if (self.outputType == CDMSDataType.Hoffmuller) else [ self.timeValue, iTimestep, self.useTimeIndex ] 
                    varDataMasked = self.cdmsDataset.getVarDataCube( dsid, varName, tval, selectedLevel, cell=cell_coords )
                    if varDataMasked.id <> 'NULL':
                        varDataSpecs = self.getGridSpecs( varDataMasked, self.cdmsDataset.gridBounds, self.cdmsDataset.zscale, self.outputType, ds )
                        if (exampleVarDataSpecs == None) and (varDataSpecs <> None): exampleVarDataSpecs = varDataSpecs
                        range_min = varDataMasked.min()
                        if type( range_min ).__name__ == "MaskedConstant": range_min = 0.0
                        range_max = varDataMasked.max()
                        if type( range_max ).__name__ == 'MaskedConstant': range_max = 0.0
                        var_md = copy.copy( varDataMasked.attributes )
                                                          
                        if ( scalar_dtype == np.float32 ) or ( scalar_dtype == np.float64 ):
                            varData = varDataMasked.filled( 1.0e-15 * range_min ).astype(scalar_dtype).ravel('F')
                        else:
                            shift = -range_min
                            scale = ( self._max_scalar_value ) / ( range_max - range_min ) if  ( range_max > range_min ) else 1.0        
                            varData = ( ( varDataMasked + shift ) * scale ).astype(scalar_dtype).filled( 0 ).ravel('F')                          
                        del varDataMasked                          
                        
                        array_size = varData.size
                        if npts == -1:  npts = array_size
                        else: assert( npts == array_size )
                            
                        var_md[ 'range' ] = ( range_min, range_max )
                        var_md[ 'scale' ] = ( shift, scale )   
                        varDataSpecs['newDataArray'] = varData 
#                        print " ** Allocated data array for %s, size = %.2f MB " % ( varDataId, (varData.nbytes /(1024.0*1024.0) ) )                    
                        md =  varDataSpecs['md']                 
                        md['datatype'] = datatype
                        md['timeValue']= self.timeValue.value
                        md['latLonGrid']= self.cdmsDataset.latLonGrid
                        md['timeUnits' ] = self.referenceTimeUnits
                        md[ 'attributes' ] = var_md
                        md[ 'plotType' ] = 'zyt' if (self.outputType == CDMSDataType.Hoffmuller) else 'xyz'
                                        
                self.setCachedData( varDataId, cell_coords, varDataSpecs )  
        
        if not varDataSpecs: return None            

        cachedImageDataName = '-'.join( varDataIds )
        image_data = self.getCachedImageData( cachedImageDataName ) 
        if not image_data:
#            print 'Building Image for cache: %s ' % cachedImageDataName
            image_data = vtk.vtkImageData() 
            outputOrigin = varDataSpecs[ 'outputOrigin' ]
            outputExtent = varDataSpecs[ 'outputExtent' ]
            gridSpacing = varDataSpecs[ 'gridSpacing' ]
            if   scalar_dtype == np.ushort: image_data.SetScalarTypeToUnsignedShort()
            elif scalar_dtype == np.ubyte:  image_data.SetScalarTypeToUnsignedChar()
            elif scalar_dtype == np.float32:  image_data.SetScalarTypeToFloat()
            elif scalar_dtype == np.float64:  image_data.SetScalarTypeToDouble()
            image_data.SetOrigin( outputOrigin[0], outputOrigin[1], outputOrigin[2] )
#            image_data.SetOrigin( 0.0, 0.0, 0.0 )
            if ndim == 3: extent = [ outputExtent[0], outputExtent[1], outputExtent[2], outputExtent[3], outputExtent[4], outputExtent[5] ]   
            elif ndim == 2: extent = [ outputExtent[0], outputExtent[1], outputExtent[2], outputExtent[3], 0, 0 ]   
            image_data.SetExtent( extent )
            image_data.SetWholeExtent( extent )
            image_data.SetSpacing(  gridSpacing[0], gridSpacing[1], gridSpacing[2] )
#            print " ********************* Create Image Data, extent = %s, spacing = %s ********************* " % ( str(extent), str(gridSpacing) )
#            offset = ( -gridSpacing[0]*gridExtent[0], -gridSpacing[1]*gridExtent[2], -gridSpacing[2]*gridExtent[4] )
            self.setCachedImageData( cachedImageDataName, image_data )
                
        nVars = len( varList )
#        npts = image_data.GetNumberOfPoints()
        pointData = image_data.GetPointData()
        for aname in range( pointData.GetNumberOfArrays() ): 
            pointData.RemoveArray( pointData.GetArrayName(aname) )
        fieldData = self.getFieldData()
        if fieldData:
            na = fieldData.GetNumberOfArrays()
            for ia in range(na):
                aname = fieldData.GetArrayName(ia)
                if (aname <> None) and aname.startswith('metadata'):
                    fieldData.RemoveArray(aname)
    #                print 'Remove fieldData Array: %s ' % aname
        extent = image_data.GetExtent()    
        scalars, nTup = None, 0
        vars = [] 
        for varDataId in varDataIds:
            try: 
                varDataSpecs = self.getCachedData( varDataId, cell_coords )   
                newDataArray = varDataSpecs.get( 'newDataArray', None )
                md = varDataSpecs[ 'md' ] 
                varName = varDataId.split(';')[1]
                var_md = md[ 'attributes' ]            
                if newDataArray <> None:
                    vars.append( varName ) 
                    md[ 'valueRange'] = var_md[ 'range' ] 
                    vtkdata = getNewVtkDataArray( scalar_dtype )
                    nTup = newDataArray.size
                    vtkdata.SetNumberOfTuples( nTup )
                    vtkdata.SetNumberOfComponents( 1 )
                    vtkdata.SetVoidArray( newDataArray, newDataArray.size, 1 )
                    vtkdata.SetName( varName )
                    vtkdata.Modified()
                    pointData.AddArray( vtkdata )
#                    print "Add array to PointData: %s " % ( varName  )  
                    if (scalars == None) and (varName <> '__zeros__'):
                        scalars = varName
                        pointData.SetActiveScalars( varName  ) 
                        md[ 'scalars'] = varName 
            except Exception, err:
                print>>sys.stderr, "Error creating variable metadata: %s " % str(err)
                traceback.print_exc()
#         for iArray in range(2):
#             scalars = pointData.GetArray(iArray) 
# #            print "Add array %d to PointData: %s (%s)" % ( iArray, pointData.GetArrayName(iArray), scalars.GetName()  )       
        try:                           
            if (self.outputType == CDMSDataType.Vector ): 
                vtkdata = getNewVtkDataArray( scalar_dtype )
                vtkdata.SetNumberOfComponents( 3 )
                vtkdata.SetNumberOfTuples( nTup )
                iComp = 0
                for varName in vars:
                    fromArray =  pointData.GetArray( varName )
                    fromNTup = fromArray.GetNumberOfTuples()
                    tup0 = fromArray.GetValue(0)
                    toNTup = vtkdata.GetNumberOfTuples()
                    vtkdata.CopyComponent( iComp, fromArray, 0 )
                    if iComp == 0: 
                        md[ 'scalars'] = varName 
                    iComp = iComp + 1                    
                vtkdata.SetName( 'vectors' )
                md[ 'vectors'] = ','.join( vars ) 
                vtkdata.Modified()
                pointData.SetVectors(vtkdata)
                pointData.SetActiveVectors( 'vectors'  )         
            if len( vars )== 0: raise Exception( 'No dataset variables selected for output %s.' % orec.name) 
            for varDataId in varDataIds:
                varDataFields = varDataId.split(';')
                dsid = varDataFields[0] 
                varName = varDataFields[1] 
                if varName <> '__zeros__':
                    varDataSpecs = self.getCachedData( varDataId, cell_coords )
                    vmd = varDataSpecs[ 'md' ] 
                    var_md = md[ 'attributes' ]               
#                    vmd[ 'vars' ] = vars               
                    vmd[ 'title' ] = getTitle( dsid, varName, var_md )                 
                    enc_mdata = encodeToString( vmd ) 
                    if enc_mdata and fieldData: fieldData.AddArray( getStringDataArray( 'metadata:%s' % varName,   [ enc_mdata ]  ) ) 
            if enc_mdata and fieldData: fieldData.AddArray( getStringDataArray( 'varlist',  vars  ) )                       
            image_data.Modified()
        except Exception, err:
            print>>sys.stderr, "Error encoding variable metadata: %s " % str(err)
            traceback.print_exc()
        return cachedImageDataName


    def getAxisValues( self, axis, roi ):
        values = axis.getValue()
        bounds = None
        if roi:
            if   axis.isLongitude():  bounds = [ roi[0], roi[2] ]
            elif axis.isLatitude():   bounds = [ roi[1], roi[3] ] if ( roi[3] > roi[1] ) else [ roi[3], roi[1] ] 
        if bounds:
            if len( values ) < 2: values = bounds
            else:
                if axis.isLongitude() and (values[0] > values[-1]):
                    values[-1] = values[-1] + 360.0 
                value_bounds = [ min(values[0],values[-1]), max(values[0],values[-1]) ]
                mid_value = ( value_bounds[0] + value_bounds[1] ) / 2.0
                mid_bounds = ( bounds[0] + bounds[1] ) / 2.0
                offset = (360.0 if mid_bounds > mid_value else -360.0)
                trans_val = mid_value + offset
                if (trans_val > bounds[0]) and (trans_val < bounds[1]):
                    value_bounds[0] = value_bounds[0] + offset
                    value_bounds[1] = value_bounds[1] + offset           
                bounds[0] = max( [ bounds[0], value_bounds[0] ] )
                bounds[1] = min( [ bounds[1], value_bounds[1] ] )
        return bounds, values

    def getCoordType( self, axis, outputType ):
        iCoord = -2
        if axis.isLongitude(): 
            self.lon = axis
            iCoord  = 0
        if axis.isLatitude(): 
            self.lat = axis
            iCoord  = 1
        if axis.isLevel() or PlotType.isLevelAxis(  axis.id ): 
            self.lev = axis
            iCoord  = 2 if ( outputType <> CDMSDataType.Hoffmuller ) else -1
        if axis.isTime():
            self.time = axis
            iCoord  = 2 if ( outputType == CDMSDataType.Hoffmuller ) else -1
        return iCoord

    def getIntersectedRoi( self, var, current_roi ):   
        try:
            newRoi = [ 0.0 ] * 4
            varname = var.outvar.name if hasattr( var,'outvar') else var.name
            tvar = self.cdmsDataset.getTransientVariable( varname )
            if id( tvar ) == id( None ): return current_roi
            current_roi_size = getRoiSize( current_roi )
            for iCoord in range(2):
                axis = None
                if iCoord == 0: axis = tvar.getLongitude()
                if iCoord == 1: axis = tvar.getLatitude()
                if axis == None: return current_roi
                axisvals = axis.getValue()          
                if ( len( axisvals.shape) > 1 ):
                    return current_roi
                newRoi[ iCoord ] = axisvals[0] # max( current_roi[iCoord], roiBounds[0] ) if current_roi else roiBounds[0]
                newRoi[ 2+iCoord ] = axisvals[-1] # min( current_roi[2+iCoord], roiBounds[1] ) if current_roi else roiBounds[1]
            if ( current_roi_size == 0 ): return newRoi
            new_roi_size = getRoiSize( newRoi )
            return newRoi if ( ( current_roi_size > new_roi_size ) and ( new_roi_size > 0.0 ) ) else current_roi
        except:
            print>>sys.stderr, "Error getting ROI for input variable"
            traceback.print_exc()
            return current_roi
       
    def getGridSpecs( self, var, roi, zscale, outputType, dset ):   
        dims = var.getAxisIds()
        gridOrigin = [ 0.0 ] * 3
        outputOrigin = [ 0.0 ] * 3
        gridBounds = [ 0.0 ] * 6
        gridSpacing = [ 0.0 ] * 3
        gridExtent = [ 0.0 ] * 6
        outputExtent = [ 0.0 ] * 6
        gridShape = [ 0.0 ] * 3
        gridSize = 1
        domain = var.getDomain()
        self.lev = var.getLevel()
        axis_list = var.getAxisList()
        isCurvilinear = False
        for axis in axis_list:
            size = len( axis )
            iCoord = self.getCoordType( axis, outputType )
            roiBounds, values = self.getAxisValues( axis, roi )
            if iCoord >= 0:
                iCoord2 = 2*iCoord
                gridShape[ iCoord ] = size
                gridSize = gridSize * size
                outputExtent[ iCoord2+1 ] = gridExtent[ iCoord2+1 ] = size-1 
                vmax =  max( values[0], values[-1] )                   
                vmin =  min( values[0], values[-1] )                   
                if iCoord < 2:
                    lonOffset = 0.0 #360.0 if ( ( iCoord == 0 ) and ( roiBounds[0] < -180.0 ) ) else 0.0
                    outputOrigin[ iCoord ] = gridOrigin[ iCoord ] = vmin + lonOffset
                    spacing = (vmax - vmin)/(size-1)
                    if roiBounds:
                        if ( roiBounds[1] < 0.0 ) and  ( roiBounds[0] >= 0.0 ): roiBounds[1] = roiBounds[1] + 360.0
                        gridExtent[ iCoord2 ] = int( round( ( roiBounds[0] - vmin )  / spacing ) )                
                        gridExtent[ iCoord2+1 ] = int( round( ( roiBounds[1] - vmin )  / spacing ) )
                        if gridExtent[ iCoord2 ] > gridExtent[ iCoord2+1 ]:
                            geTmp = gridExtent[ iCoord2+1 ]
                            gridExtent[ iCoord2+1 ] = gridExtent[ iCoord2 ] 
                            gridExtent[ iCoord2 ] = geTmp
                        outputExtent[ iCoord2+1 ] = gridExtent[ iCoord2+1 ] - gridExtent[ iCoord2 ]
                        outputOrigin[ iCoord ] = lonOffset + roiBounds[0]
                    roisize = gridExtent[ iCoord2+1 ] - gridExtent[ iCoord2 ] + 1                  
                    gridSpacing[ iCoord ] = spacing
                    gridBounds[ iCoord2 ] = roiBounds[0] if roiBounds else vmin 
                    gridBounds[ iCoord2+1 ] = (roiBounds[0] + roisize*spacing) if roiBounds else vmax
                else:                                             
                    gridSpacing[ iCoord ] = 1.0
#                    gridSpacing[ iCoord ] = zscale
                    gridBounds[ iCoord2 ] = vmin  # 0.0
                    gridBounds[ iCoord2+1 ] = vmax # float( size-1 )
        if gridBounds[ 2 ] > gridBounds[ 3 ]:
            tmp = gridBounds[ 2 ]
            gridBounds[ 2 ] = gridBounds[ 3 ]
            gridBounds[ 3 ] = tmp
        gridSpecs = {}
        md = { 'datasetId' : self.datasetId,  'bounds':gridBounds, 'lat':self.lat, 'lon':self.lon, 'lev':self.lev, 'time': self.timeAxis }
        gridSpecs['gridOrigin'] = gridOrigin
        gridSpecs['outputOrigin'] = outputOrigin
        gridSpecs['gridBounds'] = gridBounds
        gridSpecs['gridSpacing'] = gridSpacing
        gridSpecs['gridExtent'] = gridExtent
        gridSpecs['outputExtent'] = outputExtent
        gridSpecs['gridShape'] = gridShape
        gridSpecs['gridSize'] = gridSize
        gridSpecs['md'] = md
        if dset:  gridSpecs['attributes'] = dset.dataset.attributes
        return gridSpecs   
                 