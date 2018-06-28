
from GaudiKernel import SystemOfUnits as units
import argparse
simparser = argparse.ArgumentParser()
simparser.add_argument("--bFieldOff", action='store_true', help="Switch OFF magnetic field (default: B field ON)")

simparser.add_argument('-s','--seed', type=int, help='Seed for the random number generator', required=True)
simparser.add_argument('-N','--numEvents', type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)
simparser.add_argument('--detectorPath', type=str, help='Path to detectors', default = "/cvmfs/fcc.cern.ch/sw/releases/0.9.1/x86_64-slc6-gcc62-opt/linux-scientificcernslc6-x86_64/gcc-6.2.0/fccsw-0.9.1-c5dqdyv4gt5smfxxwoluqj2pjrdqvjuj")
simparser.add_argument('--trackerMergedHits', action="store_true", help='In case hits should be merged')
simparser.add_argument('--tripletTracker', action="store_true", help="Use the triplet trigger tracker instead of the BaseLine")


genTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Type of events to generate
genTypeGroup.add_argument("--singlePart", action='store_true', help="Single particle events")
genTypeGroup.add_argument("--pythia", action='store_true', help="Events generated with Pythia")
genTypeGroup.add_argument("--useVertexSmearTool", action='store_true', help="Use the Gaudi Vertex Smearing Tool")

from math import pi
singlePartGroup = simparser.add_argument_group('Single particles')
import sys
singlePartGroup.add_argument('-e','--energy', type=int, required='--singlePart' in sys.argv, help='Energy of particle in GeV')
singlePartGroup.add_argument('--etaMin', type=float, default=0., help='Minimal pseudorapidity')
singlePartGroup.add_argument('--etaMax', type=float, default=0., help='Maximal pseudorapidity')
singlePartGroup.add_argument('--phiMin', type=float, default=0, help='Minimal azimuthal angle')
singlePartGroup.add_argument('--phiMax', type=float, default=2*pi, help='Maximal azimuthal angle')
singlePartGroup.add_argument('--particle', type=int, required='--singlePart' in sys.argv, help='Particle type (PDG)')

pythiaGroup = simparser.add_argument_group('Pythia','Common for min bias and LHE')
pythiaGroup.add_argument('-c', '--card', type=str, default='Generation/data/Pythia_minbias_pp_100TeV.cmd', help='Path to Pythia card (default: PythiaCards/default.cmd)')

simargs, _ = simparser.parse_known_args()

print "=================================="
print "==      GENERAL SETTINGS       ==="
print "=================================="
magnetic_field = not simargs.bFieldOff
num_events = simargs.numEvents
seed = simargs.seed
output_name = simargs.outName
path_to_detector = simargs.detectorPath
print "B field: ", magnetic_field
print "number of events = ", num_events
print "seed: ", seed
print "output name: ", output_name
print "detectors are taken from: ", path_to_detector
if simargs.singlePart:
    energy = simargs.energy
    etaMin = simargs.etaMin
    etaMax = simargs.etaMax
    phiMin = simargs.phiMin
    phiMax = simargs.phiMax
    pdg = simargs.particle
    particle_geant_names = {11: 'e-', -11: 'e+', -13: 'mu+', 13: 'mu-', 22: 'gamma', 111: 'pi0', 211: 'pi+', -211: 'pi-', 130: 'kaon0L'}
    print "=================================="
    print "==       SINGLE PARTICLES      ==="
    print "=================================="
    print "particle PDG, name: ", pdg, " ", particle_geant_names[pdg]
    print "energy: ", energy, "GeV"
    if etaMin == etaMax:
        print "eta: ", etaMin
    else:
        print "eta: from ", etaMin, " to ", etaMax
    if phiMin == phiMax:
        print "phi: ", phiMin
    else:
        print "phi: from ", phiMin, " to ", phiMax
elif simargs.pythia:
    card = simargs.card
    print "=================================="
    print "==            PYTHIA           ==="
    print "=================================="
    print "card = ", card
print "=================================="


from Gaudi.Configuration import *
from GaudiKernel import SystemOfUnits as units
##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################

path_to_detector=simargs.detectorPath

if simargs.trackerMergedHits:
   path_to_detector = "/afs/cern.ch/user/j/jhrdinka/public/FCCSW"

if simargs.tripletTracker:
  detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                    path_to_detector+'/Detector/DetFCChhTrackerTkLayout/triplet/FCCtriplet_1barrel30mm.xml',
                    ]
else:
  detectors_to_use=[path_to_detector+'/Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                    path_to_detector+'/Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml',
                    ]

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use, OutputLevel = WARNING)

##############################################################################################################
#######                                        SIMULATION                                        #############
##############################################################################################################
# Setting random seed, will be propagated to Geant
from Configurables import  RndmGenSvc
from GaudiSvc.GaudiSvcConf import HepRndm__Engine_CLHEP__RanluxEngine_
randomEngine = eval('HepRndm__Engine_CLHEP__RanluxEngine_')
randomEngine = randomEngine('RndmGenSvc.Engine')
randomEngine.Seeds = [seed]

from Configurables import SimG4FullSimActions
actions = SimG4FullSimActions()
actions.enableHistory=True

# Magnetic field
from Configurables import SimG4ConstantMagneticFieldTool
if magnetic_field:
    field = SimG4ConstantMagneticFieldTool("bField", FieldOn=True, FieldZMax=20*units.m, IntegratorStepper="ClassicalRK4")
else:
    field = SimG4ConstantMagneticFieldTool("bField", FieldOn=False)

from Configurables import SimG4Svc
geantservice = SimG4Svc("SimG4Svc", detector='SimG4DD4hepDetector', physicslist="SimG4FtfpBert", actions=actions, magneticField=field, OutputLevel = VERBOSE)
# range cut
geantservice.g4PostInitCommands += ["/run/setCut 0.1 mm"]

from Configurables import SimG4Alg, SimG4SingleParticleGeneratorTool, SimG4SaveTrackerHits, SimG4SaveParticleHistory

savehisttool = SimG4SaveParticleHistory("saveHistory")
savehisttool.mcParticles.Path = "SimParticles"
savehisttool.genVertices.Path = "SimVertices"

savetrackertool = SimG4SaveTrackerHits("saveTrackerHits", readoutNames = ["TrackerBarrelReadout", "TrackerEndcapReadout"]) 
savetrackertool.positionedTrackHits.Path = "TrackerPositionedHits"
savetrackertool.trackHits.Path = "TrackerHits"
savetrackertool.digiTrackHits.Path = "TrackerDigiPostPoint"
outputHitsTools = []
outputHitsTools += [ "SimG4SaveTrackerHits/saveTrackerHits"]
outputHitsTools += [ "SimG4SaveParticleHistory/saveHistory"]

geantsim = SimG4Alg("SimG4Alg", outputs = outputHitsTools)

if simargs.singlePart:
    from Configurables import SimG4SingleParticleGeneratorTool
    pgun=SimG4SingleParticleGeneratorTool("SimG4SingleParticleGeneratorTool", saveEdm=True,
                                          particleName=particle_geant_names[pdg], energyMin=energy * 1000, energyMax=energy * 1000,
                                          etaMin=etaMin, etaMax=etaMax, phiMin = phiMin, phiMax = phiMax, OutputLevel = VERBOSE)
    geantsim.eventProvider = pgun
else:
    from Configurables import PythiaInterface, GenAlg, GaussSmearVertex
    smeartool = GaussSmearVertex("GaussSmearVertex")
    if simargs.useVertexSmearTool:
        smeartool.xVertexSigma = 0.5*units.mm
        smeartool.yVertexSigma = 0.5*units.mm
        smeartool.zVertexSigma = 40*units.mm
        smeartool.tVertexSigma = 180*units.picosecond

    pythia8gentool = PythiaInterface("Pythia8",Filename=card)
    pythia8gen = GenAlg("Pythia8", SignalProvider=pythia8gentool, VertexSmearingTool=smeartool)
    pythia8gen.hepmc.Path = "hepmc"
    from Configurables import HepMCToEDMConverter
    hepmc_converter = HepMCToEDMConverter("Converter", hepmcStatusList=[]) # save all the particles from Pythia
    hepmc_converter.hepmc.Path="hepmc"
    hepmc_converter.genparticles.Path="allGenParticles"
    hepmc_converter.genvertices.Path="GenVertices"
    from Configurables import GenParticleFilter
    ### Filters generated particles
    # accept is a list of particle statuses that should be accepted
    genfilter = GenParticleFilter("StableParticles", accept=[1], OutputLevel=DEBUG)
    genfilter.allGenParticles.Path = "allGenParticles"
    genfilter.filteredGenParticles.Path = "GenParticles"
    from Configurables import SimG4PrimariesFromEdmTool
    particle_converter = SimG4PrimariesFromEdmTool("EdmConverter")
    particle_converter.genParticles.Path = "GenParticles"
    geantsim.eventProvider = particle_converter

# PODIO algorithm
from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput
podioevent = FCCDataSvc("EventDataSvc")
out = PodioOutput("out")
out.outputCommands = ["drop *",
                      "keep GenParticles",
                      "keep GenVertices",
                      "keep SimParticles",
                      "keep SimVertices",
                      "keep TrackerHits",
                      "keep TrackerPositionedHits",
                      "keep TrackerDigiPostPoint",
                      ]
out.filename = output_name

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
geantsim.AuditExecute = True
out.AuditExecute = True


list_of_algorithms = [geantsim,  out]
if simargs.pythia:
    list_of_algorithms = [pythia8gen, hepmc_converter, genfilter] + list_of_algorithms

ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax   = num_events,
    ExtSvc = [podioevent, geoservice, geantservice],
)
