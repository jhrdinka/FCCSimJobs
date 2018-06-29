import argparse
simparser = argparse.ArgumentParser()
simparser.add_argument('--inName', type=str, nargs = "+", help='Name of the input file', required=True)
simparser.add_argument('--inSignalName', type=str, help='Name of the input file with signal')
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents', type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('--pileup', type=int, help='Pileup', default = 1)
simparser.add_argument('--detectorPath', type=str, help='Path to detectors', default = "/cvmfs/fcc.cern.ch/sw/releases/0.9.1/x86_64-slc6-gcc62-opt/linux-scientificcernslc6-x86_64/gcc-6.2.0/fccsw-0.9.1-c5dqdyv4gt5smfxxwoluqj2pjrdqvjuj")
simparser.add_argument('--mergeSimParticles', action='store_true', help='Set this flag to allow simulated particles to be merged as well')
simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = simargs.numEvents
path_to_detector = simargs.detectorPath
print "detectors are taken from: ", path_to_detector
input_name = simargs.inName
if simargs.inSignalName:
    input_signal_name = simargs.inSignalName
    print "input signal name: ", input_signal_name
output_name = simargs.outName
print "input pileup name: ", input_name
print "output name: ", output_name
print "=================================="

from Gaudi.Configuration import *

from Configurables import FCCDataSvc

# list of names of files with pileup event data -- to be overlaid
pileupFilenames = input_name
# the file containing the signal events
if simargs.inSignalName:
    signalFilename = input_signal_name
    noSignal = False
    # the collections to be read from the signal event
    signalCollections = ["TrackerHits","TrackerPositionedHits","TrackerDigiPostPoint","SimParticles"]
    # Data service
    podioevent = FCCDataSvc("EventDataSvc", input=signalFilename)
    # use PodioInput for Signal
    from Configurables import PodioInput
    podioinput = PodioInput("PodioReader", collections=signalCollections, OutputLevel=DEBUG)
    list_of_algorithms = [podioinput]
else:
    signalFilename = ""
    noSignal = True
    podioevent = FCCDataSvc("EventDataSvc")
    list_of_algorithms = []



##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################
path_to_detector = "/cvmfs/fcc.cern.ch/sw/releases/0.9.1/x86_64-slc6-gcc62-opt/linux-scientificcernslc6-x86_64/gcc-6.2.0/fccsw-0.9.1-c5dqdyv4gt5smfxxwoluqj2pjrdqvjuj"
detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  path_to_detector+'/Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml']

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use, OutputLevel = WARNING)

inputPUPositionedHits = "TrackerPositionedHits"
inputPUDigiTrackHits = "TrackerDigiPostPoint"
inputPUSimParticles = "SimParticles"

outputPositionedHits = "puTrackerPositionedHits"
outputDigiTrackHits  = "puTrackerDigiPostPoint"
outputSimParticles   = "puSimParticles"

if simargs.inSignalName:
    inputPUPositionedHits = "puTrackerPositionedHits"
    inputPUDigiTrackHits = "puTrackerDigiPostPoint"
    inputPUSimParticles = "puSimParticles"
    
    outputPositionedHits = "overlaidPositionedTrackHits"
    outputDigiTrackHits  = "overlaidTrackerDigiPostPoint"
    outputSimParticles   = "overlaidSimParticles"

# edm data from simulation: hits and positioned hits
from Configurables import PileupDigiTrackHitMergeTool
trackhitsmergetool = PileupDigiTrackHitMergeTool("DigiTrackHitsMerger")
# branchnames for the pileup
trackhitsmergetool.pileupHitsBranch = inputPUPositionedHits
trackhitsmergetool.pileupDigiHitsBranch = inputPUDigiTrackHits
trackhitsmergetool.pileupParticleBranch = inputPUSimParticles
# branchnames for the signal
trackhitsmergetool.signalPositionedHits = "TrackerPositionedHits"
trackhitsmergetool.signalDigiHits = "TrackerDigiPostPoint"
trackhitsmergetool.signalParticles = "SimParticles"
# branchnames for the output
trackhitsmergetool.mergedPositionedHits = outputPositionedHits
trackhitsmergetool.mergedDigiHits = outputDigiTrackHits
trackhitsmergetool.mergedParticles = outputSimParticles
if simargs.mergeSimParticles:
    trackhitsmergetool.mergeParticles = TRUE

# use the pileuptool to specify the number of pileup
from Configurables import ConstPileUp
pileuptool = ConstPileUp("MyPileupTool", numPileUpEvents=simargs.pileup)

# algorithm for the overlay
from Configurables import PileupOverlayAlg
overlay = PileupOverlayAlg()
overlay.pileupFilenames = pileupFilenames
overlay.randomizePileup =  True
overlay.doShuffleInputFiles = True
overlay.mergeTools = ["PileupDigiTrackHitMergeTool/DigiTrackHitsMerger"]
overlay.PileUpTool = pileuptool
overlay.noSignal = noSignal

# PODIO algorithm
from Configurables import PodioOutput
out = PodioOutput("out")
out.outputCommands = ["drop *", "keep "+ outputPositionedHits, "keep "+ outputDigiTrackHits, "keep " + outputSimParticles]
out.filename = output_name

list_of_algorithms += [overlay,
                       out
                       ]

# ApplicationMgr
from Configurables import ApplicationMgr
ApplicationMgr( TopAlg=list_of_algorithms,
                EvtSel='NONE',
                EvtMax=num_events,
                ExtSvc=[geoservice, podioevent]
 )
