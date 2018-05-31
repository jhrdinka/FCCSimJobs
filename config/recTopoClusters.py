import argparse, os
simparser = argparse.ArgumentParser()

simparser.add_argument('--inName', type=str, help='Name of the input file', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('-N','--numEvents',  type=int, help='Number of simulation events to run', required=True)
simparser.add_argument("--physics", action='store_true', help="Physics events")
simparser.add_argument("--addElectronicsNoise", action='store_true', help="Add electronics noise (default: false)")
simparser.add_argument("--addPileupNoise", action='store_true', help="Add pileup noise")
simparser.add_argument("--mu", type=int, help="Number of pileup-events", default=0)
simparser.add_argument('--sigma1', type=int, default=4, help='Energy threshold [in number of sigmas] for seeding')
simparser.add_argument('--sigma2', type=int, default=2, help='Energy threshold [in number of sigmas] for neighbours')
simparser.add_argument('--sigma3', type=int, default=0, help='Energy threshold [in number of sigmas] for last neighbours')
simparser.add_argument('--detectorPath', type=str, help='Path to detectors', default = "/cvmfs/fcc.cern.ch/sw/releases/0.9.1/x86_64-slc6-gcc62-opt/linux-scientificcernslc6-x86_64/gcc-6.2.0/fccsw-0.9.1-c5dqdyv4gt5smfxxwoluqj2pjrdqvjuj")
simparser.add_argument("--addPileupToSignal", action='store_true', help="Add pileup events to signal (default: false)")
simparser.add_argument('--inPileupFileNames',type=str, nargs = "+", help='Name of the pileup input file')

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
num_events = 1 #simargs.numEvents
input_name = simargs.inName
output_name = simargs.outName
elNoise = simargs.addElectronicsNoise
puNoise = simargs.addPileupNoise
puEvents = simargs.mu
sigma1 = simargs.sigma1
sigma2 = simargs.sigma2
sigma3 = simargs.sigma3
path_to_detector = simargs.detectorPath
addPUevents = simargs.addPileupToSignal

print "number of events = ", num_events
print "input name: ", input_name
print "output name: ", output_name
print 'energy thresholds for reconstruction: ', sigma1, '-', sigma2, '-', sigma3
print "detectors are taken from: ", path_to_detector

print "add pileup events to signal: ", addPUevents
if addPUevents:
    input_pileup_name = simargs.inPileupFileNames
    print "PU", (puEvents)
    print "Input file names: ", input_pileup_name
    elNoise = True

print "add electronic noise in Barrel: ", elNoise
print "add pileup noise in Barrel: ", puNoise
if puNoise:
    print 'assuming %i pileup events '%(puEvents)

pileupFilenames = input_pileup_name
import random
random.shuffle(pileupFilenames)

from Gaudi.Configuration import *
##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################

detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                  path_to_detector+'/Detector/DetFCChhECalInclined/compact/FCChh_ECalBarrel_withCryostat.xml',
                  path_to_detector+'/Detector/DetFCChhHCalTile/compact/FCChh_HCalBarrel_TileCal.xml']

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
hcalBarrelReadoutName = "HCalBarrelReadout"
hcalExtBarrelReadoutName = "HCalExtBarrelReadout"
hcalEndcapReadoutName = "HECPhiEta"
hcalFwdReadoutName = "HFwdPhiEta"
tailCatcherReadoutName = "Muons_Readout"

# Geometry details to add noise to every Calo cell and paths to root files that have the noise const per cell
ecalBarrelNoisePath = "/afs/cern.ch/user/a/azaborow/public/FCCSW/elecNoise_ecalBarrel_50Ohm_traces2_2shieldWidth_noise.root"
ecalBarrelNoiseHistName = "h_elecNoise_fcc_"
# Geometry details to add noise to every Calo cell and paths to root files that have the noise const per cell
pileupNoisePath = "/afs/cern.ch/work/c/cneubuse/public/FCChh/inBfield/noiseBarrel_mu"+str(puEvents)+".root"
ecalBarrelPileupNoiseHistName = "h_pileup_ecal_layer"
hcalBarrelPileupNoiseHistName = "h_pileup_hcal_layer"
ecalBarrelPileupOffsetHistName = "h_mean_pileup_ecal_layer"
hcalBarrelPileupOffsetHistName = "h_mean_pileup_hcal_layer"
# active material identifier name
hcalIdentifierName = ["module", "row", "layer"]
# active material volume name
hcalVolumeName = ["moduleVolume", "wedgeVolume", "layerVolume"]
# ECAL bitfield names & values
hcalFieldNames=["system"]
hcalFieldValues=[8]

# inputs for topo-clustering
inputCellCollectionECalBarrel = "ECalBarrelCells"
inputCellCollectionHCalBarrel = "HCalBarrelCells"
inputNoisePerCell = "/afs/cern.ch/work/c/cneubuse/public/FCChh/cellNoise_map_segHcal_constNoiseLevel.root"

##############################################################################################################
#######                                        INPUT                                             #############
##############################################################################################################

# reads HepMC text file and write the HepMC::GenEvent to the data service
from Configurables import ApplicationMgr, FCCDataSvc, PodioInput, PodioOutput
podioevent = FCCDataSvc("EventDataSvc", input=input_name)

podioinput = PodioInput("PodioReader", collections = ["ECalBarrelCells", "HCalBarrelCells","GenParticles","GenVertices"], OutputLevel = DEBUG)

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
#######                                       ADD PILEUP EVENTS                              #############
##############################################################################################################
if addPUevents:

    # edm data from simulation: hits and positioned hits
    from Configurables import PileupCaloHitMergeTool
    ecalbarrelmergetool = PileupCaloHitMergeTool("ECalBarrelHitMerge")
    ecalbarrelmergetool.noPositionedHits = True
    ecalbarrelmergetool.pileupHitsBranch = "mergedECalBarrelCells"
    ecalbarrelmergetool.signalHits = "ECalBarrelCells"
    ecalbarrelmergetool.mergedHits = "pileupECalBarrelCells"

   # edm data from simulation: hits and positioned hits
    hcalbarrelmergetool = PileupCaloHitMergeTool("HCalBarrelHitMerge")
    hcalbarrelmergetool.noPositionedHits = True
    hcalbarrelmergetool.pileupHitsBranch = "mergedHCalBarrelCells"
    hcalbarrelmergetool.signalHits = "HCalBarrelCells"
    hcalbarrelmergetool.mergedHits = "pileupHCalBarrelCells"
    
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
        "PileupCaloHitMergeTool/HCalBarrelHitMerge"
        ]
    overlay.PileUpTool = pileuptool

    inputCellCollectionECalBarrel = "pileupECalBarrelCells"
    inputCellCollectionHCalBarrel = "pileupHCalBarrelCells"
    inputNoisePerCell = "/afs/cern.ch/work/c/cneubuse/public/FCChh/inBfield/cellNoise_map_segHcal_noiseLevelElectronicsPileup_mu"+str(puEvents)+".root"

##############################################################################################################
#######                                       CELL POSITIONS  TOOLS                              #############
##############################################################################################################

#Configure tools for calo cell positions
from Configurables import CellPositionsECalBarrelTool, CellPositionsHCalBarrelNoSegTool, CellPositionsCaloDiscsTool, CellPositionsTailCatcherTool
ECalBcells = CellPositionsECalBarrelTool("CellPositionsECalBarrel",
                                         readoutName = ecalBarrelReadoutName,
                                         OutputLevel = INFO)
EMECcells = CellPositionsCaloDiscsTool("CellPositionsEMEC",
                                       readoutName = ecalEndcapReadoutName,
                                       OutputLevel = INFO)
ECalFwdcells = CellPositionsCaloDiscsTool("CellPositionsECalFwd",
                                          readoutName = ecalFwdReadoutName,
                                          OutputLevel = INFO)
HCalBcellVols = CellPositionsHCalBarrelNoSegTool("CellPositionsHCalBarrelVols",
                                                 readoutName = hcalBarrelReadoutName,
                                                 OutputLevel = INFO)
HECcells = CellPositionsCaloDiscsTool("CellPositionsHEC",
                                      readoutName = hcalEndcapReadoutName,
                                      OutputLevel = INFO)
HCalFwdcells = CellPositionsCaloDiscsTool("CellPositionsHCalFwd",
                                          readoutName = hcalFwdReadoutName,
                                          OutputLevel = INFO)

##############################################################################################################
#######                          PREPARE TOPO CLUSTERING :                                       #############
#######                          PREPARE EMPTY CELL COLLECTIONS                                  #############
#######                          READ NEIGHBOURS MAP                                             #############
##############################################################################################################

# Fill empty collections for un-used Calo systems
from Configurables import CreateEmptyCaloCellsCollection
createemptycells = CreateEmptyCaloCellsCollection("CreateEmptyCaloCells")
createemptycells.cells.Path = "emptyCaloCells"

from Configurables import TopoCaloNeighbours, TopoCaloNoisyCells
# read the neighbours map
readNeighboursMap = TopoCaloNeighbours("ReadNeighboursMap",
                                       fileName = "/afs/cern.ch/work/c/cneubuse/public/FCChh/neighbours_map_segHcal.root",
                                       OutputLevel = DEBUG)

##############################################################################################################
#######                          NOISE/NO NOISE TOOL FOR CLUSTER THRESHOLDS                      #############
##############################################################################################################

if elNoise:
    # Apply cell thresholds for electronics noise only if no pileup events have been merged
    if not addPUevents:
        inputNoisePerCell = "/afs/cern.ch/work/c/cneubuse/public/FCChh/cellNoise_map_segHcal_electronicsNoiseLevel.root"
        
    from Configurables import CreateCaloCells, NoiseCaloCellsFromFileTool, TubeLayerPhiEtaCaloTool, CalibrateCaloHitsTool, NoiseCaloCellsFlatTool, NestedVolumesCaloTool
    # ECal Barrel noise
    noiseBarrel = NoiseCaloCellsFromFileTool("NoiseBarrel",
                                             readoutName = ecalBarrelReadoutName,
                                             noiseFileName = ecalBarrelNoisePath,
                                             elecNoiseHistoName = ecalBarrelNoiseHistName,
                                             activeFieldName = "layer",
                                             addPileup = False,
                                             numRadialLayers = 8)
    
    # add noise, create all existing cells in detector
    barrelGeometry = TubeLayerPhiEtaCaloTool("EcalBarrelGeo",
                                             readoutName = ecalBarrelReadoutName,
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
                                            hits=inputCellCollectionECalBarrel,
                                            cells="ECalBarrelCellsNoise")

    # HCal Barrel noise
    noiseHcal = NoiseCaloCellsFlatTool("HCalNoise", cellNoise = 0.009)
    
    hcalgeo = NestedVolumesCaloTool("HcalGeo",
                                    activeVolumeName = hcalVolumeName,
                                    activeFieldName = hcalIdentifierName,
                                    readoutName = hcalBarrelReadoutName,
                                    fieldNames = hcalFieldNames,
                                    fieldValues = hcalFieldValues,
                                    OutputLevel = INFO)

    createHcalBarrelCells = CreateCaloCells("CreateHCalBarrelCells",
                                            geometryTool = hcalgeo,
                                            doCellCalibration = False,
                                            addCellNoise = True, filterCellNoise = False,
                                            noiseTool = noiseHcal,
                                            OutputLevel = INFO)
    createHcalBarrelCells.hits.Path=inputCellCollectionHCalBarrel
    createHcalBarrelCells.cells.Path="HCalBarrelCellsNoise"
    
    # Create topo clusters
    from Configurables import CaloTopoClusterInputTool, CaloTopoCluster
    createTopoInputNoise = CaloTopoClusterInputTool("CreateTopoInputNoise",
                                                    ecalBarrelReadoutName = ecalBarrelReadoutName,
                                                    ecalEndcapReadoutName = "",
                                                    ecalFwdReadoutName = "",
                                                    hcalBarrelReadoutName = hcalBarrelReadoutName,
                                                    hcalExtBarrelReadoutName = "",
                                                    hcalEndcapReadoutName = "",
                                                    hcalFwdReadoutName = "",
                                                    OutputLevel = INFO)
    createTopoInputNoise.ecalBarrelCells.Path = "ECalBarrelCellsNoise"
    createTopoInputNoise.ecalEndcapCells.Path = "emptyCaloCells"
    createTopoInputNoise.ecalFwdCells.Path = "emptyCaloCells"
    createTopoInputNoise.hcalBarrelCells.Path = "HCalBarrelCellsNoise"
    createTopoInputNoise.hcalExtBarrelCells.Path = "emptyCaloCells"
    createTopoInputNoise.hcalEndcapCells.Path = "emptyCaloCells"
    createTopoInputNoise.hcalFwdCells.Path = "emptyCaloCells"

    readNoisyCellsMap = TopoCaloNoisyCells("ReadNoisyCellsMap",
                                           fileName = inputNoisePerCell,
                                           OutputLevel = DEBUG)

    # Topo-Cluster Algorithm
    # Seed and neighbour thresholds 4 - 2 - 0 w/noise
    createTopoClustersNoise = CaloTopoCluster("CreateTopoClustersNoise",
                                              TopoClusterInput = createTopoInputNoise,
                                              # expects neighbours map from cellid->vec<neighbourIds>
                                              neigboursTool = readNeighboursMap,
                                              # tool to get noise level per cellid
                                              noiseTool = readNoisyCellsMap,
                                              # cell positions tools for all sub-systems
                                              positionsECalBarrelTool = ECalBcells,
                                              positionsHCalBarrelTool = HCalBcellVols,
                                              seedSigma = sigma1,
                                              neighbourSigma = sigma2,
                                              lastNeighbourSigma = sigma3,
                                              OutputLevel = INFO)
    createTopoClustersNoise.clusters.Path = "caloClustersBarrelNoise"
    createTopoClustersNoise.clusterCells.Path = "caloClusterBarrelNoiseCells"

    from Configurables import CreateCaloCellPositions
    positionsClusterBarrelNoise = CreateCaloCellPositions("positionsClusterBarrelNoise",
                                                          positionsECalBarrelTool = ECalBcells,
                                                          positionsHCalBarrelTool = HCalBcellVols,
                                                          positionsHCalExtBarrelTool = HCalBcellVols,
                                                          positionsEMECTool = EMECcells,
                                                          positionsHECTool = HECcells,
                                                          positionsEMFwdTool = ECalFwdcells,
                                                          positionsHFwdTool = HCalFwdcells,
                                                          hits = "caloClusterBarrelNoiseCells",
                                                          positionedHits = "caloClusterBarrelNoiseCellPositions",
                                                          OutputLevel = INFO)

##############################################################################################################
#######                          NOISE/NO NOISE TOOL FOR CLUSTER THRESHOLDS                      #############
##############################################################################################################

if puNoise:

    from Configurables import CreateCaloCells, NoiseCaloCellsFromFileTool, TubeLayerPhiEtaCaloTool, CalibrateCaloHitsTool, NoiseCaloCellsFlatTool, NestedVolumesCaloTool
    # ECal Barrel noise
    noiseBarrel = NoiseCaloCellsFromFileTool("NoiseECalBarrel",
                                             readoutName = ecalBarrelReadoutName,
                                             cellPositionsTool = ECalBcells,
                                             noiseFileName = pileupNoisePath,
                                             elecNoiseHistoName = ecalBarrelNoiseHistName,
                                             pileupHistoName = ecalBarrelPileupNoiseHistName,
                                             activeFieldName = "layer",
                                             addPileup = True,
                                             numRadialLayers = 8)
    
    # add noise, create all existing cells in detector
    barrelGeometry = TubeLayerPhiEtaCaloTool("EcalBarrelGeo",
                                             readoutName = ecalBarrelReadoutName,
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
                                            hits="ECalBarrelCellsRedo",
                                            cells="ECalBarrelCellsNoise")
    
    # HCal Barrel noise
    noiseHcal = NoiseCaloCellsFromFileTool("NoiseHCalBarrel",
                                           readoutName = hcalBarrelReadoutName,
                                           cellPositionsTool = HCalBcellVols,
                                           noiseFileName = pileupNoisePath,
                                           elecNoiseHistoName = hcalBarrelPileupNoiseHistName,
                                           activeFieldName = "layer",
                                           addPileup = False,
                                           numRadialLayers = 10)
    
    hcalgeo = NestedVolumesCaloTool("HcalGeo",
                                    activeVolumeName = hcalVolumeName,
                                    activeFieldName = hcalIdentifierName,
                                    readoutName = hcalBarrelReadoutName,
                                    fieldNames = hcalFieldNames,
                                    fieldValues = hcalFieldValues,
                                    OutputLevel = INFO)
    
    createHcalBarrelCells = CreateCaloCells("CreateHCalBarrelCells",
                                            geometryTool = hcalgeo,
                                            doCellCalibration = False,
                                            addCellNoise = True, filterCellNoise = False,
                                            noiseTool = noiseHcal,
                                            OutputLevel = INFO)
    createHcalBarrelCells.hits.Path="HCalBarrelCells"
    createHcalBarrelCells.cells.Path="HCalBarrelCellsNoise"
       
    # Create topo clusters
    from Configurables import CaloTopoClusterInputTool, CaloTopoCluster
    createTopoInputNoise = CaloTopoClusterInputTool("CreateTopoInputNoise",
                                                    ecalBarrelReadoutName = ecalBarrelReadoutName,
                                                    ecalEndcapReadoutName = "",
                                                    ecalFwdReadoutName = "",
                                                    hcalBarrelReadoutName = hcalBarrelReadoutName,
                                                    hcalExtBarrelReadoutName = "",
                                                    hcalEndcapReadoutName = "",
                                                    hcalFwdReadoutName = "",
                                                    OutputLevel = DEBUG)
    createTopoInputNoise.ecalBarrelCells.Path = "ECalBarrelCellsNoise"
    createTopoInputNoise.ecalEndcapCells.Path = "emptyCaloCells"
    createTopoInputNoise.ecalFwdCells.Path = "emptyCaloCells"
    createTopoInputNoise.hcalBarrelCells.Path =     "HCalBarrelCellsNoise"
    createTopoInputNoise.hcalExtBarrelCells.Path = "emptyCaloCells"
    createTopoInputNoise.hcalEndcapCells.Path = "emptyCaloCells"
    createTopoInputNoise.hcalFwdCells.Path = "emptyCaloCells"
    
    readNoisyCellsMap = TopoCaloNoisyCells("ReadNoisyCellsMap",
                                           fileName = "/afs/cern.ch/work/c/cneubuse/public/FCChh/inBfield/cellNoise_map_segHcal_noiseLevelElectronicsPileup_mu"+str(puEvents)+".root",
                                           OutputLevel = INFO)
    
    # Topo-Cluster Algorithm
    # Seed and neighbour thresholds 4 - 2 - 0 w/noise
    createTopoClustersNoise = CaloTopoCluster("CreateTopoClustersNoise",
                                              TopoClusterInput = createTopoInputNoise,
                                              # expects neighbours map from cellid->vec<neighbourIds>
                                              neigboursTool = readNeighboursMap,
                                              # tool to get noise level per cellid
                                              noiseTool = readNoisyCellsMap,
                                              # cell positions tools for all sub-systems
                                              positionsECalBarrelTool = ECalBcells,
                                              positionsHCalBarrelTool = HCalBcellVols,
                                              seedSigma = sigma1,
                                              neighbourSigma = sigma2,
                                              lastNeighbourSigma = sigma3,
                                              OutputLevel = DEBUG)
    createTopoClustersNoise.clusters.Path = "caloClustersBarrelNoise"
    createTopoClustersNoise.clusterCells.Path = "caloClusterBarrelNoiseCells"
    
    from Configurables import CreateCaloCellPositions
    positionsClusterBarrelNoise = CreateCaloCellPositions("positionsClusterBarrelNoise",
                                                          positionsECalBarrelTool = ECalBcells,
                                                          positionsHCalBarrelTool = HCalBcellVols,
                                                          positionsHCalExtBarrelTool = HCalBcellVols,
                                                          positionsEMECTool = EMECcells,
                                                          positionsHECTool = HECcells,
                                                          positionsEMFwdTool = ECalFwdcells,
                                                          positionsHFwdTool = HCalFwdcells,
                                                          hits = "caloClusterBarrelNoiseCells",
                                                          positionedHits = "caloClusterBarrelNoiseCellPositions",
                                                          OutputLevel = INFO)
    
##############################################################################################################
#######                                 TOPO-CLUSTERING                                          #############
##############################################################################################################
    
# "Noise" level without added noise for topo thresholds set to 1.875MeV and 2.875MeV in E and HCal
# in case of added PU events, the thresholds are set to the PU/cell estimates
readNoNoisyCellsMap = TopoCaloNoisyCells("ReadNoNoisyCellsMap",
                                         fileName = inputNoisePerCell,
                                         OutputLevel = DEBUG)

print "ECal cell collection used in Topo-clustering: ", inputCellCollectionECalBarrel
print "HCal cell collection used in Topo-clustering: ", inputCellCollectionHCalBarrel

# Create topo clusters
from Configurables import CaloTopoClusterInputTool, CaloTopoCluster, TopoCaloNeighbours
createTopoInput = CaloTopoClusterInputTool("CreateTopoInput",
                                           ecalBarrelReadoutName = ecalBarrelReadoutName,
                                           ecalEndcapReadoutName = "",
                                           ecalFwdReadoutName = "",
                                           hcalBarrelReadoutName = hcalBarrelReadoutName,
                                           hcalExtBarrelReadoutName = "",
                                           hcalEndcapReadoutName = "",
                                           hcalFwdReadoutName = "",
                                           OutputLevel = INFO)
createTopoInput.ecalBarrelCells.Path = inputCellCollectionECalBarrel
createTopoInput.ecalEndcapCells.Path = "emptyCaloCells"
createTopoInput.ecalFwdCells.Path = "emptyCaloCells"
createTopoInput.hcalBarrelCells.Path = inputCellCollectionHCalBarrel
createTopoInput.hcalExtBarrelCells.Path = "emptyCaloCells"
createTopoInput.hcalEndcapCells.Path = "emptyCaloCells"
createTopoInput.hcalFwdCells.Path = "emptyCaloCells"

# Topo-Cluster Algorithm
# Seed and neighbour thresholds 4 - 0 - 0 if no noise added
createTopoClusters = CaloTopoCluster("CreateTopoClusters",
                                     TopoClusterInput = createTopoInput,
                                     # expects neighbours map from cellid->vec<neighbourIds>
                                     neigboursTool = readNeighboursMap,
                                     # tool to get noise level per cellid
                                     noiseTool = readNoNoisyCellsMap,
                                     # cell positions tools for all sub-systems
                                     positionsECalBarrelTool = ECalBcells,
                                     positionsHCalBarrelTool = HCalBcellVols,
                                     seedSigma = sigma1,
                                     neighbourSigma = sigma2,
                                     lastNeighbourSigma = sigma3,
                                     OutputLevel = INFO)
createTopoClusters.clusters.Path = "caloClustersBarrel"
createTopoClusters.clusterCells.Path = "caloClusterBarrelCells"


##############################################################################################################
#######                                       TOPO-CLUSTER CELL POSITIONS                        #############
##############################################################################################################
from Configurables import CreateCaloCellPositions
positionsClusterBarrel = CreateCaloCellPositions("positionsClusterBarrel",
                                                 positionsECalBarrelTool = ECalBcells,
                                                 positionsHCalBarrelTool = HCalBcellVols,
                                                 positionsHCalExtBarrelTool = HCalBcellVols,
                                                 positionsEMECTool = EMECcells,
                                                 positionsHECTool = HECcells,
                                                 positionsEMFwdTool = ECalFwdcells,
                                                 positionsHFwdTool = HCalFwdcells,
                                                 hits = "caloClusterBarrelCells",
                                                 positionedHits = "caloClusterBarrelCellPositions",
                                                 OutputLevel = INFO)

# PODIO algorithm
out = PodioOutput("out", OutputLevel=DEBUG)
out.outputCommands = ["drop *", "keep GenParticles", "keep GenVertices", "keep caloClustersBarrel", "keep caloClusterBarrelCells", "keep caloClusterBarrelCellPositions",]
out.filename = output_name

if addPUevents:
    out.outputCommands += ["keep pileupECalBarrelCells", "keep pileupHCalBarrelCells"]
if elNoise or puNoise:
    out.outputCommands += ["keep ECalBarrelCellsNoise", "keep HCalBarrelCellsNoise", "keep caloClustersBarrelNoise","keep caloClusterBarrelNoiseCells",  "keep caloClusterBarrelCellPositions"]
out.filename = output_name

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
podioinput.AuditExecute = True
createemptycells.AuditExecute = True
out.AuditExecute = True

list_of_algorithms = [podioinput,
                      recreateEcalBarrelCells,
                      createemptycells]

if addPUevents:
     list_of_algorithms += [overlay]
   
if elNoise or puNoise:
    list_of_algorithms += [createEcalBarrelCells, createHcalBarrelCells, createTopoClustersNoise, positionsClusterBarrelNoise]

else:
    list_of_algorithms += [createTopoClusters, positionsClusterBarrel]

list_of_algorithms += [out]

ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax   = num_events,
    ExtSvc = [geoservice, podioevent, audsvc],
    OutputLevel = VERBOSE)
