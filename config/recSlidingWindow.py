import argparse, math
simparser = argparse.ArgumentParser()

simparser.add_argument('--inName', type=str, help='Name of the input file', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents', type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('--detectorPath', type=str, help='Path to detectors', default = "/cvmfs/fcc.cern.ch/sw/releases/0.9.1/x86_64-slc6-gcc62-opt/linux-scientificcernslc6-x86_64/gcc-6.2.0/fccsw-0.9.1-c5dqdyv4gt5smfxxwoluqj2pjrdqvjuj")

simparser.add_argument("--addElectronicsNoise", action='store_true', help="Add electronics noise (default: false)")
simparser.add_argument('--winEta', type=int, default=7, help='Size of the final cluster in eta')
simparser.add_argument('--winPhi', type=int, default=19, help='Size of the final cluster in phi')
simparser.add_argument('--enThreshold', type=float, default=3., help='Energy threshold of the seeding clusters [GeV]')
simparser.add_argument('--mu', type=int, default=1000, help='Pileup scenario')

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = simargs.numEvents
input_name = simargs.inName
output_name = simargs.outName
noise = simargs.addElectronicsNoise
path_to_detector = simargs.detectorPath
winEta = simargs.winEta
winPhi = simargs.winPhi
winEtaSeed = int(math.floor(winEta*2./4.))
winPhiSeed = int(math.floor(winPhi*2./4.))
winEtaPos = int(math.floor(winEta*2./4.))
winPhiPos = int(math.floor(winPhi*2./4.))
winEtaDup = int(math.floor(winEta*3./4.))
winPhiDup = int(math.floor(winPhi*2./4.))

## make sure that window size is odd
if winEtaSeed %2 == 0:
    winEtaSeed = winEtaSeed +1
if winPhiSeed %2 == 0:
    winPhiSeed = winPhiSeed +1
if winEtaPos %2 == 0:
    winEtaPos = winEtaPos +1 
if winPhiPos %2 == 0:
    winPhiPos = winPhiPos +1 
if winEtaDup %2 == 0:
    winEtaDup = winEtaDup +1 
if winPhiDup %2 == 0:
    winPhiDup = winPhiDup +1 

enThreshold = simargs.enThreshold
pileup = simargs.mu
print "number of events = ", num_events
print "input name: ", input_name
print "output name: ", output_name
print "electronic noise in ECAL: ", noise
print "detectors are taken from: ", path_to_detector
print "seed cluster eta size: ", winEtaSeed
print "seed cluster phi size: ", winPhiSeed
print "pos cluster eta size: ", winEtaPos
print "pos cluster phi size: ", winPhiPos
print "dup cluster eta size: ", winEtaDup
print "dup cluster phi size: ", winPhiDup
print "final cluster eta size: ", winEta
print "final cluster phi size: ", winPhi
print "energy threshold for seeding cluster [GeV]: ", enThreshold
print "pileup scenario: <mu> = ", pileup

from Gaudi.Configuration import *
##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################
detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  path_to_detector+'/Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
                  path_to_detector+'/Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_withCryostat.xml',
                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml',
                  path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Endcaps_coneCryo.xml',
                  path_to_detector+'/Detector/DetFCChhCalDiscs/compact/Forward_coneCryo.xml',
                  path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Solenoids.xml',
                  path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_Shielding.xml']

if not noise:
    detectors_to_use += [path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalExtendedBarrel_TileCal.xml']

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use)

# ECAL readouts
ecalBarrelReadoutName = "ECalBarrelEta"
ecalBarrelReadoutNamePhiEta = "ECalBarrelPhiEta"
ecalEndcapReadoutName = "EMECPhiEta"
ecalFwdReadoutName = "EMFwdPhiEta"
ecalBarrelNoisePath = "/afs/cern.ch/user/a/azaborow/public/FCCSW/elecNoise_ecalBarrel_50Ohm_traces2_2shieldWidth_noise.root"
ecalEndcapNoisePath = "/afs/cern.ch/user/n/novaj/public/elecNoise_emec_6layers.root"
ecalBarrelPileupNoisePath = "/afs/cern.ch/user/a/azaborow/public/FCCSW/elecNoise_pileup_cluster.root"
ecalBarrelNoiseHistName = "h_elecNoise_fcc_"
ecalBarrelPileupHistName = "h_pileup_layer"
ecalEndcapNoiseHistName = "h_elecNoise_fcc_"
# HCAL readouts
hcalBarrelReadoutName = "HCalBarrelReadout"
hcalExtBarrelReadoutName = "HCalExtBarrelReadout"
hcalEndcapReadoutName = "HECPhiEta"
hcalFwdReadoutName = "HFwdPhiEta"
##############################################################################################################
#######                                           INPUT                                          #############
##############################################################################################################
# reads HepMC text file and write the HepMC::GenEvent to the data service
from Configurables import PodioInput, FCCDataSvc
podioevent = FCCDataSvc("EventDataSvc", input=input_name)
podioinput = PodioInput("in", collections = ["GenVertices",
                                             "GenParticles",
                                             "ECalBarrelCells",
                                             "ECalEndcapCells",
                                             "ECalFwdCells",
                                             # "HCalBarrelCells",
                                             # "HCalExtBarrelCells",
                                             "HCalEndcapCells",
                                             "HCalFwdCells"])

##############################################################################################################
#######                                       DIGITISATION                                       #############
##############################################################################################################
from Configurables import CreateEmptyCaloCellsCollection
createemptycells = CreateEmptyCaloCellsCollection("CreateEmptyCaloCells")
createemptycells.cells.Path = "emptyCaloCells"

from Configurables import CreateCaloCells
if noise:
    from Configurables import NoiseCaloCellsFromFileTool, TubeLayerPhiEtaCaloTool
# 1. ECAL BARREL
if noise:
    noiseBarrel = NoiseCaloCellsFromFileTool("NoiseBarrel",
                                             readoutName = ecalBarrelReadoutNamePhiEta,
                                             noiseFileName = ecalBarrelNoisePath,
                                             elecNoiseHistoName = ecalBarrelNoiseHistName,
                                             activeFieldName = "layer",
                                             addPileup = False,
                                             numRadialLayers = 8)

    # add noise, create all existing cells in detector
    barrelGeometry = TubeLayerPhiEtaCaloTool("EcalBarrelGeo",
                                             readoutName = ecalBarrelReadoutNamePhiEta,
                                             activeVolumeName = "LAr_sensitive",
                                             activeFieldName = "layer",
                                             fieldNames = ["system"],
                                             fieldValues = [5],
                                             activeVolumesNumber = 8)
    createEcalBarrelCells = CreateCaloCells("CreateECalBarrelCells",
                                            geometryTool = barrelGeometry,
                                            doCellCalibration=False, # already calibrated
                                            addCellNoise=True, filterCellNoise=False,
                                            noiseTool = noiseBarrel,
                                            hits="ECalBarrelCells",
                                            cells="ECalBarrelCellsNoise")
    # noiseEndcap = NoiseCaloCellsFromFileTool("NoiseEndcap",
    #                                          readoutName = ecalEndcapReadoutName,
    #                                          noiseFileName = ecalEndcapNoisePath,
    #                                          elecNoiseHistoName = ecalEndcapNoiseHistName,
    #                                          activeFieldName = "layer",
    #                                          addPileup = False,
    #                                          numRadialLayers = 40,
    #                                          noiseCells = "ECalEndcapElNoiseOnlyCells")
    # endcapGeometry = TubeLayerPhiEtaCaloTool("EcalEndcapGeo",
    #                                          readoutName = ecalEndcapReadoutName,
    #                                          activeVolumeName = "layerEnvelope",
    #                                          activeFieldName = "layer",
    #                                          activeVolumesNumber = 40,
    #                                          fieldNames = ["system"],
    #                                          fieldValues = [6])
    # createEcalEndcapCells = CreateCaloCells("CreateECalEndcapCells",
    #                                         geometryTool = endcapGeometry,
    #                                         doCellCalibration=False, # already calibrated
    #                                         addCellNoise=True, filterCellNoise=False,
    #                                         noiseTool = noiseEndcap,
    #                                         hits="ECalEndcapCells",
    #                                         cells="ECalEndcapCellsNoise")
    #Create calo clusters
    from Configurables import CreateCaloClustersSlidingWindow, CaloTowerTool
    from GaudiKernel.PhysicalConstants import pi
    towersNoise = CaloTowerTool("towersNoise",
                           deltaEtaTower = 0.01, deltaPhiTower = 2*pi/704.,
                           ecalBarrelReadoutName = ecalBarrelReadoutNamePhiEta,
                           ecalEndcapReadoutName = ecalEndcapReadoutName,
                           ecalFwdReadoutName = ecalFwdReadoutName,
                           # hcalBarrelReadoutName = hcalBarrelReadoutName,
                           # hcalExtBarrelReadoutName = hcalExtBarrelReadoutName,
                           hcalBarrelReadoutName = "",
                           hcalExtBarrelReadoutName = "",
                           hcalEndcapReadoutName = hcalEndcapReadoutName,
                           hcalFwdReadoutName = hcalFwdReadoutName)
    towersNoise.ecalBarrelCells.Path = "ECalBarrelCellsNoise"
    towersNoise.ecalEndcapCells.Path = "ECalEndcapCells"
    towersNoise.ecalFwdCells.Path = "ECalFwdCells"
    # towersNoise.hcalBarrelCells.Path = "HCalBarrelCells"
    # towersNoise.hcalExtBarrelCells.Path = "HCalExtBarrelCells"
    towersNoise.hcalBarrelCells.Path = "emptyCaloCells"
    towersNoise.hcalExtBarrelCells.Path = "emptyCaloCells"
    towersNoise.hcalEndcapCells.Path = "HCalEndcapCells"
    towersNoise.hcalFwdCells.Path = "HCalFwdCells"
    createclustersNoise = CreateCaloClustersSlidingWindow("CreateCaloClustersNoise",
                                                          towerTool = towersNoise,
                                                          nEtaWindow = winEtaSeed, nPhiWindow = winPhiSeed,
                                                          nEtaPosition = winEtaPos, nPhiPosition = winPhiPos,
                                                          nEtaDuplicates = winEtaDup, nPhiDuplicates = winPhiDup,
                                                          nEtaFinal = winEta, nPhiFinal = winPhi,
                                                          energyThreshold = enThreshold,
                                                          OutputLevel = INFO)
    createclustersNoise.clusters.Path = "caloClustersNoise"
    from Configurables import CorrectCluster
    correctClusters = CorrectCluster("CorrectCluster",
                                     energyAxis = energy,
                                     numLayers = 8,
                                     etaValues = [0,0.25],
                                     presamplerShiftP0 = [0.05938, 0.05938],
                                     presamplerShiftP1 = [0.0001833,0.0001833],
                                     presamplerScaleP0  = [2.4, 2.4],
                                     presamplerScaleP1  = [-0.006838, -0.006838],
                                     mu = pileup,
                                     noiseFileName = ecalBarrelPileupNoisePath)
    correctClusters.clusters.Path = "caloClustersNoise",
    correctClusters.correctedClusters.Path = "caloClustersCorrected"

#Create calo clusters
from Configurables import CreateCaloClustersSlidingWindow, CaloTowerTool
from GaudiKernel.PhysicalConstants import pi
towers = CaloTowerTool("towers",
                       deltaEtaTower = 0.01, deltaPhiTower = 2*pi/704.,
                       ecalBarrelReadoutName = ecalBarrelReadoutNamePhiEta,
                       ecalEndcapReadoutName = ecalEndcapReadoutName,
                       ecalFwdReadoutName = ecalFwdReadoutName,
                       # hcalBarrelReadoutName = hcalBarrelReadoutName,
                       # hcalExtBarrelReadoutName = hcalExtBarrelReadoutName,
                       hcalBarrelReadoutName = "",
                       hcalExtBarrelReadoutName = "",
                       hcalEndcapReadoutName = hcalEndcapReadoutName,
                       hcalFwdReadoutName = hcalFwdReadoutName)
towers.ecalBarrelCells.Path = "ECalBarrelCells"
towers.ecalEndcapCells.Path = "ECalEndcapCells"
towers.ecalFwdCells.Path = "ECalFwdCells"
# towers.hcalBarrelCells.Path = "HCalBarrelCells"
# towers.hcalExtBarrelCells.Path = "HCalExtBarrelCells"
towers.hcalBarrelCells.Path = "emptyCaloCells"
towers.hcalExtBarrelCells.Path = "emptyCaloCells"
towers.hcalEndcapCells.Path = "HCalEndcapCells"
towers.hcalFwdCells.Path = "HCalFwdCells"

createclusters = CreateCaloClustersSlidingWindow("CreateCaloClusters",
                                                 towerTool = towers,
                                                 nEtaWindow = winEtaSeed, nPhiWindow = winPhiSeed,
                                                 nEtaPosition = winEtaPos, nPhiPosition = winPhiPos,
                                                 nEtaDuplicates = winEtaDup, nPhiDuplicates = winPhiDup,
                                                 nEtaFinal = winEta, nPhiFinal = winPhi,
                                                 energyThreshold = enThreshold)
createclusters.clusters.Path = "caloClusters"

# PODIO algorithm
from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput
out = PodioOutput("out")
out.outputCommands = ["keep *"]
out.filename = output_name

THistSvc().Output = ["rec DATAFILE='hist_"+output_name+"' TYP='ROOT' OPT='RECREATE'"]
THistSvc().PrintAll=True
THistSvc().AutoSave=True
THistSvc().AutoFlush=False
THistSvc().OutputLevel=INFO


#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
out.AuditExecute = True

list_of_algorithms = [podioinput,
                      createemptycells,
                      createclusters]
if noise:
    list_of_algorithms += [createEcalBarrelCells, createclustersNoise, correctedClustersNoise]

list_of_algorithms += [out]

ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax   = num_events,
    ExtSvc = [podioevent, geoservice]
)
