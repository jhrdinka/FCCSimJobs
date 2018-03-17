import argparse, os
simparser = argparse.ArgumentParser()

simparser.add_argument('--inNames', nargs='+', help='Names of the input files', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents',  type=int, help='Number of simulation events to run', required=True)

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = simargs.numEvents
All_pileupfilenames = simargs.inNames
output_name = simargs.outName

newList = []
for ifile in All_pileupfilenames:
    infile = ifile.replace(',','')
    newList.append(infile)
    
print "number of events = ", num_events
print "input file names: ", newList
print "output name: ", output_name

from Gaudi.Configuration import *
##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################

path_to_detector = '/afs/cern.ch/work/c/cneubuse/public/TopoClusters/FCCSW/'
#'/afs/cern.ch/work/h/helsens/public/FCCsoft/FCCSW-0.8.3/'
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
hcalBarrelReadoutName = "BarHCal_Readout_phieta"
hcalBarrelReadoutVolume = "HCalBarrelReadout"
hcalExtBarrelReadoutName = "ExtBarHCal_Readout"
hcalExtBarrelReadoutVolume = "HCalExtBarrelReadout"
hcalEndcapReadoutName = "HECPhiEta"
hcalFwdReadoutName = "HFwdPhiEta"
tailCatcherReadoutName = "Muons_Readout"

##############################################################################################################
#######                                        INPUT                                             #############
##############################################################################################################

# reads HepMC text file and write the HepMC::GenEvent to the data service
from Configurables import ApplicationMgr, FCCDataSvc, PodioInput, PodioOutput
podioevent = FCCDataSvc("EventDataSvc")

podioinput = PodioInput("PodioReader", collections = ["ECalBarrelCells", "HCalBarrelCells", "HCalExtBarrelCells", "ECalEndcapCells", "HCalEndcapCells", "ECalFwdCells", "HCalFwdCells", "TailCatcherCells"], OutputLevel = DEBUG)

pileupFilenames = [f for f in newList if 'converted' not in f]
import random
random.shuffle(pileupFilenames)

from Configurables import PileupParticlesMergeTool
particlemergetool = PileupParticlesMergeTool("MyPileupParticlesMergeTool")
# branchnames for the pileup
particlemergetool.genParticlesBranch = "GenParticles"
particlemergetool.genVerticesBranch = "GenVertices"
# branchnames for the signal
particlemergetool.signalGenVertices.Path = "GenVertices"
particlemergetool.signalGenParticles.Path = "GenParticles"
# branchnames for the output
particlemergetool.mergedGenParticles.Path = "overlaidGenParticles"
particlemergetool.mergedGenVertices.Path = "overlaidGenVertices"

# edm data from simulation: hits and positioned hits for the EM Calo
from Configurables import PileupCaloCellMergeTool
ECalhitsmergetool = PileupCaloCellMergeTool("MyECalHitMergeTool")
# branchnames for the pileup
ECalhitsmergetool.pileupHitsBranch = ecalBarrelCellsName
# branchnames for the signal
ECalhitsmergetool.signalHits = ecalBarrelCellsName
# branchnames for the output
ECalhitsmergetool.mergedHits = "overlaidECalBarrelCells"

HCalhitsmergetool = PileupCaloCellMergeTool("MyHCalHitMergeTool")
# branchnames for the pileup
HCalhitsmergetool.pileupHitsBranch = hcalBarrelCellsName
# branchnames for the signal
HCalhitsmergetool.signalHits = hcalBarrelCellsName
# branchnames for the output
HCalhitsmergetool.mergedHits = "overlaidHCalBarrelCells"


# use the pileuptool to specify the number of pileup
from Configurables import ConstPileUp
pileuptool = ConstPileUp("MyPileupTool", numPileUpEvents=10)

# algorithm for the overlay
from Configurables import PileupOverlayAlg
overlay = PileupOverlayAlg()
overlay.pileupFilenames = pileupFilenames
overlay.randomizePileup = False
overlay.noSignal = True
overlay.mergeTools = [
                      "PileupCaloHitMergeTool/MyECalHitMergeTool",
                      "PileupCaloHitMergeTool/MyHCalHitMergeTool"]
overlay.PileUpTool = pileuptool

################################################################
################################################################


out = PodioOutput("out", 
                  OutputLevel=INFO)
out.outputCommands = ["keep *"]
out.filename = "output_pileupOverlay.root"

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
out.AuditExecute = True

ApplicationMgr(
    TopAlg = [
        overlay,
        out
        ],
    EvtSel = 'NONE',
    EvtMax   = int(num_events),
    ExtSvc = [podioevent, geoservice, audsvc],
 )

