import argparse
simparser = argparse.ArgumentParser()

simparser.add_argument('--inName', type=str, help='Name of the input file', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents',  type=int, help='Number of simulation events to run', required=True)

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = simargs.numEvents
input_name = simargs.inName
output_name = simargs.outName
print "number of events = ", num_events
print "input name: ", input_name
print "output name: ", output_name

from Gaudi.Configuration import *
##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################

path_to_detector = '/afs/cern.ch/work/c/cneubuse/public/TopoClusters/FCCSW/'
from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput

detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  path_to_detector+'/Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
                  path_to_detector+'/Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_withCryostat.xml',
                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml',
#                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalExtendedBarrel_TileCal.xml',
                  path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Endcaps_coneCryo.xml',
                  path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Forward_coneCryo.xml',
                  path_to_detector+'/Detector/DetFCChhTailCatcher/compact/FCChh_TailCatcher.xml',
                  path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Solenoids.xml',
                  path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Shielding.xml']

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use, OutputLevel = WARNING)

# ECAL readouts
ecalBarrelReadoutName = "ECalBarrelEta"
ecalBarrelReadoutNamePhiEta = "ECalBarrelPhiEta"
ecalEndcapReadoutName = "EMECPhiEtaReco"
ecalFwdReadoutName = "EMFwdPhiEtaReco"
# HCAL readouts
hcalBarrelReadoutName = "BarHCal_Readout"
hcalBarrelReadoutVolume = "HCalBarrelReadout"
hcalExtBarrelReadoutName = "ExtBarHCal_Readout"
hcalExtBarrelReadoutVolume = "HCalExtBarrel"
hcalEndcapReadoutName = "HECPhiEtaReco"
hcalFwdReadoutName = "HFwdPhiEtaReco"
# Tail Catcher readout
tailCatcherReadoutName = "Muons_Readout"

# Pileup in ECal Barrel
# HCal Barrel
# active material identifier name
hcalIdentifierName = ["module", "row", "layer"]
# active material volume name
hcalVolumeName = ["moduleVolume", "wedgeVolume", "layerVolume"]
# ECAL bitfield names & values
hcalFieldNames=["system"]
hcalFieldValues=[8]

##############################################################################################################
#######                                        INPUT                                             #############
##############################################################################################################
# reads HepMC text file and write the HepMC::GenEvent to the data service
from Configurables import ApplicationMgr, FCCDataSvc, PodioInput, PodioOutput
podioevent = FCCDataSvc("EventDataSvc", input=input_name)

podioinput = PodioInput("PodioReader", collections = ["ECalBarrelCells", "HCalBarrelCells", "HCalExtBarrelCells", "ECalEndcapCells", "HCalEndcapCells", "ECalFwdCells", "HCalFwdCells", "TailCatcherCells"], OutputLevel = DEBUG)

##############################################################################################################
#######                                       RECALIBRATE ECAL                                   #############
##############################################################################################################                                                                                                                              
from Configurables import CalibrateInLayersTool, CreateCaloCells
recalibEcalBarrel = CalibrateInLayersTool("RecalibrateEcalBarrel",
                                          samplingFraction = [0.299654475899/0.12125] + [0.148166996525/0.14283] + [0.163005489744/0.16354] + [0.176907220821/0.17662] + [0.189980731321/0.18867] + [0.202201963561/0.19890] + [0.214090761907/0.20637] + [0.224706564289/0.20802],
                                          readoutName = ecalBarrelReadoutName,
                                          layerFieldName = "layer")
recreateEcalBarrelCells = CreateCaloCells("redoEcalBarrelCells",
                                          doCellCalibration=True,
                                          calibTool=recalibEcalBarrel,
                                          addCellNoise=False, filterCellNoise=False)
recreateEcalBarrelCells.hits.Path="ECalBarrelCells"
recreateEcalBarrelCells.cells.Path="ECalBarrelCellsRedo"

##############################################################################################################
#######                                       CELL POSITIONS                                     #############
#############################################################################################################
#Configure tools for calo cell positions
from Configurables import CellPositionsECalBarrelTool, CellPositionsHCalBarrelTool, CellPositionsHCalBarrelNoSegTool, CellPositionsCaloDiscsTool, CellPositionsTailCatcherTool 
ECalBcells = CellPositionsECalBarrelTool("CellPositionsECalBarrel", 
                                         readoutName = ecalBarrelReadoutNamePhiEta, 
                                         OutputLevel = INFO)
EMECcells = CellPositionsCaloDiscsTool("CellPositionsEMEC", 
                                       readoutName = ecalEndcapReadoutName, 
                                       OutputLevel = INFO)
ECalFwdcells = CellPositionsCaloDiscsTool("CellPositionsECalFwd", 
                                          readoutName = ecalFwdReadoutName, 
                                          OutputLevel = INFO)
HCalBcellVols = CellPositionsHCalBarrelNoSegTool("CellPositionsHCalBarrelVols", 
                                                 readoutName = hcalBarrelReadoutVolume, 
                                                 OutputLevel = INFO)
HCalExtBcellVols = CellPositionsHCalBarrelNoSegTool("CellPositionsHCalExtBarrel", 
                                                    readoutName = hcalExtBarrelReadoutVolume, 
                                                    OutputLevel = INFO)
HECcells = CellPositionsCaloDiscsTool("CellPositionsHEC", 
                                      readoutName = hcalEndcapReadoutName, 
                                      OutputLevel = INFO)
HCalFwdcells = CellPositionsCaloDiscsTool("CellPositionsHCalFwd", 
                                          readoutName = hcalFwdReadoutName, 
                                          OutputLevel = INFO)

##############################################################################################################
#######                                       REWRITE HCAL READOUT                               #############
#############################################################################################################

from Configurables import RewriteHCalBarrelBitfield
rewriteHcal = RewriteHCalBarrelBitfield("RewriteHCalBitfield", 
                                        oldReadoutName = hcalBarrelReadoutName,
                                        newReadoutName = hcalBarrelReadoutVolume,
                                        # specify if segmentation is removed                                                                                                                                                  
                                        removeIds = ["tile","eta","phi"],
                                        debugPrint = 10,
                                        OutputLevel = INFO)
# clusters are needed, with deposit position and cellID in bits                                                                                                                                                                           
rewriteHcal.inhits.Path = "HCalBarrelCells"
rewriteHcal.outhits.Path = "HCalBarrelCellsVol"

# geometry tool
from Configurables import TubeLayerPhiEtaCaloTool
ecalBarrelGeometry = TubeLayerPhiEtaCaloTool("EcalBarrelGeo",
                                             readoutName = ecalBarrelReadoutNamePhiEta,
                                             activeVolumeName = "LAr_sensitive",
                                             activeFieldName = "layer",
                                             fieldNames = ["system"],
                                             fieldValues = [5],
                                             activeVolumesNumber = 8)

from Configurables import NestedVolumesCaloTool
hcalBarrelGeometry = NestedVolumesCaloTool("HcalBarrelGeo",
                                           activeVolumeName = hcalVolumeName,
                                           activeFieldName = hcalIdentifierName,
                                           readoutName = hcalBarrelReadoutVolume,
                                           fieldNames = hcalFieldNames,
                                           fieldValues = hcalFieldValues,
                                           OutputLevel = INFO)

##############################################################################################################
#######                                       ESTIMATE PILE UP AND WRITE OUT                     #############
#############################################################################################################

# call pileup tool
# prepare TH2 histogram with pileup per abs(eta)
from Configurables import PreparePileup
pileupEcalBarrel = PreparePileup("PreparePileupEcalBarrel",
                                 geometryTool = ecalBarrelGeometry,
                                 positionsTool = ECalBcells,
                                 readoutName = ecalBarrelReadoutNamePhiEta,
                                 layerFieldName = "layer",
                                 histogramName = "ecalBarrelEnergyVsAbsEta",
                                 numLayers = 8,
                                 OutputLevel = DEBUG)
pileupEcalBarrel.hits.Path="ECalBarrelCells"

from Configurables import PreparePileup
pileupHcalBarrel = PreparePileup("PreparePileupHcalBarrel",
                                 geometryTool = hcalBarrelGeometry,
                                 positionsTool = HCalBcellVols,
                                 readoutName = hcalBarrelReadoutVolume,
                                 layerFieldName = "layer",
                                 xAxisMax = 600, # cm in z, binning is 10cm, 5 cells 
                                 histogramName ="hcalBarrelEnergyVsAbsEta",
                                 numLayers = 10,
                                 OutputLevel = DEBUG)
pileupHcalBarrel.hits.Path="HCalBarrelCellsVol"

THistSvc().Output = ["rec DATAFILE='"+str(output_name)+"' TYP='ROOT' OPT='RECREATE'"]
THistSvc().PrintAll=True
THistSvc().AutoSave=True
THistSvc().AutoFlush=True
THistSvc().OutputLevel=INFO

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
podioinput.AuditExecute = True

ApplicationMgr(
    TopAlg = [podioinput,
              rewriteHcal,
              pileupEcalBarrel,
              pileupHcalBarrel,
              ],
    EvtSel = 'NONE',
    EvtMax = num_events,
    ExtSvc = [podioevent, geoservice],
 )
