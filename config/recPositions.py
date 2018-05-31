import argparse
simparser = argparse.ArgumentParser()

simparser.add_argument('--inName', type=str, help='Name of the input file', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents',  type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('--prefixCollections', type=str, help='Prefix added to the collection names', default="")
simparser.add_argument("--addMuons", action='store_true', help="Add tail catcher cells", default = False)

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = simargs.numEvents
input_name = simargs.inName
output_name = simargs.outName
prefix = simargs.prefixCollections
addMuons = simargs.addMuons
print "number of events = ", num_events
print "input name: ", input_name
print "output name: ", output_name
print "prefix added to the collections' name: ", prefix

from Gaudi.Configuration import *
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

# ECAL readouts
ecalBarrelReadoutName = "ECalBarrelPhiEta"
ecalEndcapReadoutName = "EMECPhiEtaReco"
ecalFwdReadoutName = "EMFwdPhiEta"
# HCAL readouts
hcalBarrelReadoutName = "HCalBarrelReadout"
hcalExtBarrelReadoutName = "HCalExtBarrelReadout"
hcalEndcapReadoutName = "HECPhiEtaReco"
hcalFwdReadoutName = "HFwdPhiEta"
# Tail Catcher readout
tailCatcherReadoutName = "Muons_Readout"
##############################################################################################################
#######                                        INPUT                                             #############
##############################################################################################################
# reads HepMC text file and write the HepMC::GenEvent to the data service
from Configurables import ApplicationMgr, FCCDataSvc, PodioInput, PodioOutput
podioevent = FCCDataSvc("EventDataSvc", input=input_name)

coll_names_read = [prefix+"ECalBarrelCells", prefix+"HCalBarrelCells", prefix+"HCalExtBarrelCells", prefix+"ECalEndcapCells", prefix+"HCalEndcapCells", prefix+"ECalFwdCells", prefix+"HCalFwdCells", prefix+"GenParticles", prefix+"GenVertices"]
if addMuons:
    coll_names_read += ["TailCatcherCells"]
podioinput = PodioInput("PodioReader", collections = coll_names_read, OutputLevel = DEBUG)

##############################################################################################################
#######                                       RECALIBRATE ECAL                                   #############
##############################################################################################################

from Configurables import RewriteBitfield
rewriteECalEC = RewriteBitfield("RewriteECalEC",
                                # old bitfield (readout)
                                oldReadoutName = "EMECPhiEta",
                                # specify which fields are going to be deleted
                                removeIds = ["sublayer"],
                                # new bitfield (readout), with new segmentation
                                newReadoutName = ecalEndcapReadoutName,
                                debugPrint = 10,
                                OutputLevel = DEBUG)
# clusters are needed, with deposit position and cellID in bits
rewriteECalEC.inhits.Path = prefix+"ECalEndcapCells"
rewriteECalEC.outhits.Path = "newECalEndcapCells"

rewriteHCalEC = RewriteBitfield("RewriteHCalEC",
                                # old bitfield (readout)
                                oldReadoutName = "HECPhiEta",
                                # specify which fields are going to be deleted
                                removeIds = ["sublayer"],
                                # new bitfield (readout), with new segmentation
                                newReadoutName = hcalEndcapReadoutName,
                                debugPrint = 10,
                                OutputLevel = DEBUG)
# clusters are needed, with deposit position and cellID in bits
rewriteHCalEC.inhits.Path = prefix+"HCalEndcapCells"
rewriteHCalEC.outhits.Path = "newHCalEndcapCells"

##############################################################################################################
#######                                       CELL POSITIONS                                     #############
##############################################################################################################

#Configure tools for calo cell positions
from Configurables import CellPositionsECalBarrelTool, CellPositionsHCalBarrelNoSegTool, CellPositionsCaloDiscsTool, CellPositionsCaloDiscsTool
ECalBcells = CellPositionsECalBarrelTool("CellPositionsECalBarrel",
                                    readoutName = ecalBarrelReadoutName,
                                    OutputLevel = INFO)
EMECcells = CellPositionsCaloDiscsTool("CellPositionsEMEC",
                                    readoutName = ecalEndcapReadoutName,
                                    OutputLevel = DEBUG)
ECalFwdcells = CellPositionsCaloDiscsTool("CellPositionsECalFwd",
                                        readoutName = ecalFwdReadoutName,
                                        OutputLevel = INFO)
HCalBcells = CellPositionsHCalBarrelNoSegTool("CellPositionsHCalBarrel",
                                              readoutName = hcalBarrelReadoutName,
                                              OutputLevel = INFO)
HCalExtBcells = CellPositionsHCalBarrelNoSegTool("CellPositionsHCalExtBarrel",
                                                 readoutName = hcalExtBarrelReadoutName,
                                                 OutputLevel = INFO)
HECcells = CellPositionsCaloDiscsTool("CellPositionsHEC",
                                   readoutName = hcalEndcapReadoutName,
                                   OutputLevel = INFO)
HCalFwdcells = CellPositionsCaloDiscsTool("CellPositionsHCalFwd",
                                        readoutName = hcalFwdReadoutName,
                                        OutputLevel = INFO)
if addMuons:
    from Configurables import CellPositionsTailCatcherTool
    TailCatchercells = CellPositionsTailCatcherTool("CellPositionsTailCatcher",
                                                    readoutName = tailCatcherReadoutName,
                                                    centralRadius = 901.5,
                                                    OutputLevel = INFO)

# cell positions
from Configurables import CreateCellPositions
positionsEcalBarrel = CreateCellPositions("positionsEcalBarrel",
                                          positionsTool=ECalBcells,
                                          hits = prefix+"ECalBarrelCells",
                                          positionedHits = "ECalBarrelCellPositions",
                                          OutputLevel = INFO)
positionsHcalBarrel = CreateCellPositions("positionsHcalBarrel",
                                          positionsTool=HCalBcells,
                                          hits = prefix+"HCalBarrelCells",
                                          positionedHits = "HCalBarrelCellPositions",
                                          OutputLevel = INFO)
positionsHcalExtBarrel = CreateCellPositions("positionsHcalExtBarrel",
                                          positionsTool=HCalExtBcells,
                                          hits = prefix+"HCalExtBarrelCells",
                                          positionedHits = "HCalExtBarrelCellPositions",
                                          OutputLevel = INFO)
positionsEcalEndcap = CreateCellPositions("positionsEcalEndcap",
                                          positionsTool=EMECcells,
                                          hits = "newECalEndcapCells",
                                          positionedHits = "ECalEndcapCellPositions",
                                          OutputLevel = INFO)
positionsHcalEndcap = CreateCellPositions("positionsHcalEndcap",
                                          positionsTool=HECcells,
                                          hits = "newHCalEndcapCells",
                                          positionedHits = "HCalEndcapCellPositions",
                                          OutputLevel = INFO)
positionsEcalFwd = CreateCellPositions("positionsEcalFwd",
                                          positionsTool=ECalFwdcells,
                                          hits = prefix+"ECalFwdCells",
                                          positionedHits = "ECalFwdCellPositions",
                                          OutputLevel = INFO)
positionsHcalFwd = CreateCellPositions("positionsHcalFwd",
                                          positionsTool=HCalFwdcells,
                                          hits = prefix+"HCalFwdCells",
                                          positionedHits = "HCalFwdCellPositions",
                                          OutputLevel = INFO)
if addMuons:
    positionsTailCatcher = CreateCellPositions("positionsTailCatcher",
                                               positionsTool=TailCatchercells,
                                               hits = "TailCatcherCells",
                                               positionedHits = "TailCatcherCellPositions",
                                               OutputLevel = INFO)

# PODIO algorithm
out = PodioOutput("out", OutputLevel=DEBUG)
out.outputCommands = ["keep *","drop "+prefix+"ECalBarrelCells","drop "+prefix+"ECalEndcapCells","drop "+prefix+"ECalFwdCells","drop "+prefix+"HCalBarrelCells", "drop "+prefix+"HCalExtBarrelCells", "drop "+prefix+"HCalEndcapCells", "drop "+prefix+"HCalFwdCells"]
if addMuons:
    out.outputCommands += ["drop TailCatcherCells"]
out.filename = "edm.root"

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
podioinput.AuditExecute = True
positionsEcalBarrel.AuditExecute = True
positionsEcalEndcap.AuditExecute = True
positionsEcalFwd.AuditExecute = True
positionsHcalBarrel.AuditExecute = True
positionsHcalExtBarrel.AuditExecute = True
positionsHcalEndcap.AuditExecute = True
positionsHcalFwd.AuditExecute = True
if addMuons:
    positionsTailCatcher.AuditExecute = True
out.AuditExecute = True

list_of_algorithms = [podioinput,
                      rewriteECalEC,
                      rewriteHCalEC,
                      positionsEcalBarrel,
                      positionsEcalEndcap,
                      positionsEcalFwd,
                      positionsHcalBarrel,
                      positionsHcalExtBarrel,
                      positionsHcalEndcap,
                      positionsHcalFwd]
if addMuons:
    list_of_algorithms += [positionsTailCatcher]
list_of_algorithms += [out]

ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax   = num_events,
    ExtSvc = [geoservice, podioevent, audsvc],
)
