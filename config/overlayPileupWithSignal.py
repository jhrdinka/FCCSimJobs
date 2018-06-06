import argparse, os
simparser = argparse.ArgumentParser()

simparser.add_argument('--inName', type=str, help='Name of the input file', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents',  type=int, help='Number of simulation events to run', required=True)
simparser.add_argument("--pileup", type=int, help="Number of pileup-events", default=0)
simparser.add_argument('--inPileupFileNames',type=str, nargs = "+", help='Name of the pileup input file',required=True)

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = simargs.numEvents
input_name = simargs.inName
output_name = simargs.outName
puEvents = simargs.pileup

print "number of events = ", num_events
print "input name: ", input_name
print "output name: ", output_name

input_pileup_name = []
input_pileup_name = simargs.inPileupFileNames
print 'add %i pileup events '%(puEvents)
print "Pileup input file names: ", input_pileup_name

pileupFilenames = input_pileup_name
import random
random.shuffle(pileupFilenames)

from Gaudi.Configuration import *

# Names of cells collections
ecalBarrelCellsName = "ECalBarrelCells"
ecalEndcapCellsName = "ECalEndcapCells"
ecalFwdCellsName = "ECalFwdCells"
hcalBarrelCellsName = "HCalBarrelCells"
hcalExtBarrelCellsName = "HCalExtBarrelCells"
hcalEndcapCellsName = "HCalEndcapCells"
hcalFwdCellsName = "HCalFwdCells"
# Readouts
ecalBarrelReadoutName = "ECalBarrelPhiEta"
ecalEndcapReadoutName = "EMECPhiEta"
ecalFwdReadoutName = "EMFwdPhiEta"
hcalBarrelReadoutName = "HCalBarrelReadout"
hcalExtBarrelReadoutName = "HCalExtBarrelReadout"
hcalEndcapReadoutName = "HECPhiEta"
hcalFwdReadoutName = "HFwdPhiEta"
tailCatcherReadoutName = "Muons_Readout"

##############################################################################################################
#######                                        INPUT                                             #############
##############################################################################################################

# reads HepMC text file and write the HepMC::GenEvent to the data service
from Configurables import ApplicationMgr, FCCDataSvc, PodioInput, PodioOutput
podioevent = FCCDataSvc("EventDataSvc", input=input_name)

podioinput = PodioInput("PodioReader", collections = ["GenParticles", "GenVertices",
                         "ECalBarrelCells", "ECalEndcapCells", "ECalFwdCells",
                         "HCalBarrelCells", "HCalExtBarrelCells", "HCalEndcapCells", "HCalFwdCells"], OutputLevel = DEBUG)

##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################
path_to_detector = "/cvmfs/fcc.cern.ch/sw/releases/0.9.1/x86_64-slc6-gcc62-opt/linux-scientificcernslc6-x86_64/gcc-6.2.0/fccsw-0.9.1-c5dqdyv4gt5smfxxwoluqj2pjrdqvjuj"
detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  path_to_detector+'/Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
                  path_to_detector+'/Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_withCryostat.xml',
                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml',
                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalExtendedBarrel_TileCal.xml',
                  path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Endcaps_coneCryo.xml',
                  path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Forward_coneCryo.xml',
                  path_to_detector+'/Detector/DetFCChhTailCatcher/compact/FCChh_TailCatcher.xml',
                  path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Solenoids.xml',
                  path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Shielding.xml']

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use, OutputLevel = WARNING)

##############################################################################################################
#######                                       ADD PILEUP EVENTS                              #############
##############################################################################################################

# edm data from simulation: hits and positioned hits
from Configurables import PileupCaloHitMergeTool
ecalbarrelmergetool = PileupCaloHitMergeTool("ECalBarrelHitMerge")
#ecalbarrelmergetool.noPositionedHits = True
ecalbarrelmergetool.pileupHitsBranch = "mergedECalBarrelCells"
ecalbarrelmergetool.signalHits = "ECalBarrelCells"
ecalbarrelmergetool.mergedHits = "pileupECalBarrelCells"

# edm data from simulation: hits and positioned hits
ecalendcapmergetool = PileupCaloHitMergeTool("ECalEndcapHitMerge")
ecalendcapmergetool.pileupHitsBranch = "mergedECalEndcapCells"
ecalendcapmergetool.signalHits = "ECalEndcapCells"
ecalendcapmergetool.mergedHits = "pileupECalEndcapCells"

# edm data from simulation: hits and positioned hits
ecalfwdmergetool = PileupCaloHitMergeTool("ECalFwdHitMerge")
# branchnames for the pileup
ecalfwdmergetool.pileupHitsBranch = "mergedECalFwdCells"
ecalfwdmergetool.signalHits = "ECalFwdCells"
ecalfwdmergetool.mergedHits = "pileupECalFwdCells"

# edm data from simulation: hits and positioned hits
hcalbarrelmergetool = PileupCaloHitMergeTool("HCalBarrelHitMerge")
#hcalbarrelmergetool.noPositionedHits = True
hcalbarrelmergetool.pileupHitsBranch = "mergedHCalBarrelCells"
hcalbarrelmergetool.signalHits = "HCalBarrelCells"
hcalbarrelmergetool.mergedHits = "pileupHCalBarrelCells"

 # edm data from simulation: hits and positioned hits
hcalextbarrelmergetool = PileupCaloHitMergeTool("HCalExtBarrelHitMerge")
hcalextbarrelmergetool.pileupHitsBranch = "mergedHCalExtBarrelCells"
hcalextbarrelmergetool.signalHits = "HCalExtBarrelCells"
hcalextbarrelmergetool.mergedHits = "pileupHCalExtBarrelCells"

# edm data from simulation: hits and positioned hits
hcalfwdmergetool = PileupCaloHitMergeTool("HCalFwdHitMerge")
hcalfwdmergetool.pileupHitsBranch = "mergedHCalFwdCells"
hcalfwdmergetool.signalHits = "HCalFwdCells"
hcalfwdmergetool.mergedHits = "pileupHCalFwdCells"

# edm data from simulation: hits and positioned hits
hcalfwdmergetool = PileupCaloHitMergeTool("HCalEndcapHitMerge")
hcalfwdmergetool.pileupHitsBranch = "mergedHCalEndcapCells"
hcalfwdmergetool.signalHits = "HCalEndcapCells"
hcalfwdmergetool.mergedHits = "pileupHCalEndcapCells"

   
# use the pileuptool to specify the number of pileup
from Configurables import ConstPileUp
pileuptool = ConstPileUp("MyPileupTool", numPileUpEvents=1)

# algorithm for the overlay
from Configurables import PileupOverlayAlg
overlay = PileupOverlayAlg()
overlay.pileupFilenames = pileupFilenames
overlay.randomizePileup = True
overlay.mergeTools = [
                      "PileupCaloHitMergeTool/ECalBarrelHitMerge",
                      "PileupCaloHitMergeTool/ECalEndcapHitMerge",
                      "PileupCaloHitMergeTool/ECalFwdHitMerge",
                      "PileupCaloHitMergeTool/HCalBarrelHitMerge",
                      "PileupCaloHitMergeTool/HCalExtBarrelHitMerge",
                      "PileupCaloHitMergeTool/HCalEndcapHitMerge",
                      "PileupCaloHitMergeTool/HCalFwdHitMerge"
                      ]
overlay.PileUpTool = pileuptool

##############################################################################################################
#######                                       DIGITISATION                                       #############
##############################################################################################################
from Configurables import CreateCaloCells
createEcalBarrelCells = CreateCaloCells("CreateEcalBarrelCells",
                                        doCellCalibration=False,
                                        addCellNoise=False, filterCellNoise=False)
createEcalBarrelCells.hits.Path="pileupECalBarrelCells"
createEcalBarrelCells.cells.Path="addedPUECalBarrelCells"
createEcalEndcapCells = CreateCaloCells("CreateEcalEndcapCells",
                                        doCellCalibration=False,
                                        addCellNoise=False, filterCellNoise=False)
createEcalEndcapCells.hits.Path="pileupECalEndcapCells"
createEcalEndcapCells.cells.Path="addedPUECalEndcapCells"
createEcalFwdCells = CreateCaloCells("CreateEcalFwdCells",
                                     doCellCalibration=False,
                                     addCellNoise=False, filterCellNoise=False)
createEcalFwdCells.hits.Path="pileupECalFwdCells"
createEcalFwdCells.cells.Path="addedPUECalFwdCells"
createHcalBarrelCells = CreateCaloCells("CreateHcalBarrelCells",
                                        doCellCalibration=False,
                                        addCellNoise=False, filterCellNoise=False)
createHcalBarrelCells.hits.Path="pileupHCalBarrelCells"
createHcalBarrelCells.cells.Path="addedPUHCalBarrelCells"
createHcalExtBarrelCells = CreateCaloCells("CreateHcalExtBarrelCells",
                                           doCellCalibration=False,
                                           addCellNoise=False, filterCellNoise=False)
createHcalExtBarrelCells.hits.Path="pileupHCalExtBarrelCells"
createHcalExtBarrelCells.cells.Path="addedPUHCalExtBarrelCells"
createHcalEndcapCells = CreateCaloCells("CreateHcalEndcapCells",
                                        doCellCalibration=False,
                                        addCellNoise=False, filterCellNoise=False)
createHcalEndcapCells.hits.Path="pileupHCalEndcapCells"
createHcalEndcapCells.cells.Path="addedPUHCalEndcapCells"
createHcalFwdCells = CreateCaloCells("CreateHcalFwdCells",
                                     doCellCalibration=False,
                                     addCellNoise=False, filterCellNoise=False)
createHcalFwdCells.hits.Path="pileupHCalFwdCells"
createHcalFwdCells.cells.Path="addedPUHCalFwdCells"

# PODIO algorithm
out = PodioOutput("out", OutputLevel=DEBUG)
out.outputCommands = ["drop *", "keep GenParticles", "keep GenVertices", "keep addedPUECalBarrelCells", "keep addedPUECalEndcapCells", "keep addedPUECalFwdCells", "keep addedPUHCalBarrelCells", "keep addedPUHCalExtBarrelCells", "keep addedPUHCalEndcapCells", "keep addedPUHCalFwdCells"]
out.filename = output_name

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
podioinput.AuditExecute = True
out.AuditExecute = True

list_of_algorithms = [podioinput,
                      overlay,
                      createEcalBarrelCells,
                      createEcalEndcapCells,
                      createEcalFwdCells,
                      createHcalBarrelCells,
                      createHcalExtBarrelCells,
                      createHcalEndcapCells,
                      createHcalFwdCells]
   
list_of_algorithms += [out]

ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax   = num_events,
    ExtSvc = [geoservice, podioevent, audsvc],
    OutputLevel = INFO)
