import argparse
simparser = argparse.ArgumentParser()
simparser.add_argument('--inName', type=str, help='Name of the input file', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents', type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('--detectorPath', type=str, help='Path to detectors', default = "/afs/cern.ch/user/j/jhrdinka/public/FCCSW")
simparser.add_argument('--puOnlyDigi', action='store_true', help='Set this flag to indicate that pile up only hits are digitized. Default: signal only.')
simparser.add_argument('--signalPUDigi', action='store_true', help='Set this flag to indicate that signal overlaid with PU hits are digitized. Default: signal only.')

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = simargs.numEvents
path_to_detector = simargs.detectorPath
print "detectors are taken from: ", path_to_detector
input_name = simargs.inName
output_name = simargs.outName
print "input  name: ", input_name
print "output name: ", output_name
print "=================================="

from Gaudi.Configuration import *

# the name of the input hits
if simargs.puOnlyDigi:
    inputHits = "puTrackerDigiPostPoint"
elif simargs.signalPUDigi:
    inputHits = "overlaidTrackerDigiPostPoint"
else:
    inputHits = "TrackerDigiPostPoint"

# Data service
from Configurables import FCCDataSvc
podioevent = FCCDataSvc("EventDataSvc", input=input_name)
# the input
from Configurables import PodioInput
podioInput = PodioInput("PodioInput", collections=[inputHits])

##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################
detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  path_to_detector+'/Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml']

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use)

# tracking geomery service
from Configurables import TrackingGeoSvc
trkgeoservice = TrackingGeoSvc("TrackingGeometryService")

# the cluster writer
# todo option to turn off cluster writer
from Configurables import ModuleClusterWriter
clusterWriter = ModuleClusterWriter("ClusteWriter")
clusterWriter.filename = output_name
# the digitizer
from Configurables import GeometricTrackerDigitizer
digitizer = GeometricTrackerDigitizer()
digitizer.digiTrackHitAssociation.Path=inputHits
digitizer.trackClusters.Path="trackClusters"
digitizer.clusterTrackHits.Path="clusterTrackHits"
digitizer.analogReadout=FALSE
digitizer.clusterWriter = clusterWriter
digitizer.writeClusterInfo = TRUE
digitizer.commonCorner=TRUE
digitizer.cosThetaLocMin = 0

# PODIO algorithm
#from Configurables import PodioOutput
#out = PodioOutput("out")
#out.outputCommands = ["drop *", "keep trackClusters", "keep clusterTrackHits"]
#out.filename = output_name

# ApplicationMgr
from Configurables import ApplicationMgr
ApplicationMgr( TopAlg=[podioInput,digitizer],
               EvtSel='NONE',
               EvtMax=num_events,
               ExtSvc=[geoservice, trkgeoservice, podioevent]
               )
