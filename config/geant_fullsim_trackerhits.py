import argparse
simparser = argparse.ArgumentParser()
simparser.add_argument("--bFieldOff", action='store_true', help="Switch OFF magnetic field (default: B field ON)")

simparser.add_argument('-s','--seed', type=int, help='Seed for the random number generator', required=True)
simparser.add_argument('-N','--numEvents', type=int, help='Number of simulation events to run', required=True)
simparser.add_argument('--outName', type=str, help='Name of the output file', required=True)


genTypeGroup = simparser.add_mutually_exclusive_group(required = True) # Type of events to generate
genTypeGroup.add_argument("--singlePart", action='store_true', help="Single particle events")
genTypeGroup.add_argument("--pythia", action='store_true', help="Events generated with Pythia")

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
print "B field: ", magnetic_field
print "number of events = ", num_events
print "seed: ", seed
print "output name: ", output_name
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

##############################################################################################################
#######                                         GEOMETRY                                         #############
##############################################################################################################

path_to_detector = '/afs/cern.ch/work/h/helsens/public/FCCsoft/FCCSW-0.8.3/'
from Configurables import GeoSvc
detectors_to_use = [ path_to_detector+ 'Detector/DetFCChhBaseline1/compact/FCChh_DectEmptyMaster.xml',
                     path_to_detector+ 'Detector/DetFCChhTrackerTkLayout/compact/Tracker.xml'
                   ]

from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc", detectors = detectors_to_use, OutputLevel = WARNING)

# tracker readout
trackerBarrelReadout = "TrackerBarrelReadout"
trackerEndCapReadout = "TrackerEndcapReadout"

##############################################################################################################
#######                                        SIMULATION                                        #############
##############################################################################################################

# Setting random seed, will be propagated to Geant
from Configurables import  RndmGenSvc
from GaudiSvc.GaudiSvcConf import HepRndm__Engine_CLHEP__RanluxEngine_
randomEngine = eval('HepRndm__Engine_CLHEP__RanluxEngine_')
randomEngine = randomEngine('RndmGenSvc.Engine')
randomEngine.Seeds = [seed]

messageLevelPythia =INFO

from Configurables import ApplicationMgr, FCCDataSvc, PodioOutput

podioevent   = FCCDataSvc("EventDataSvc")


# Geant4 service                                                                                                                                                                         
# Configures the Geant simulation: geometry, physics list and user actions
from Configurables import SimG4Svc, SimG4FullSimActions
actions = SimG4FullSimActions()
actions.enableHistory=True
geantservice = SimG4Svc("SimG4Svc", detector='SimG4DD4hepDetector', physicslist="SimG4FtfpBert", actions=actions)

#Setting random seeds for Geant4 simulations
#geantservice.g4PreInitCommands  += ["/random/setSeeds "+str(x)+" 0"] #where x is the number you want

# range cut
geantservice.g4PostInitCommands += ["/run/setCut 0.1 mm"]

# Geant4 algorithm                                                                                                                                                                                                       
# Translates EDM to G4Event, passes the event to G4, writes out outputs via tools                                                                                                                                          
# and a tool that saves the calorimeter hits                                                                                                                                                                                         
from Configurables import SimG4Alg, InspectHitsCollectionsTool,SimG4SaveTrackerHits,SimG4SaveParticleHistory

savetrackertool = SimG4SaveTrackerHits("saveTrackerHits", readoutNames = [trackerBarrelReadout, trackerEndCapReadout])
savetrackertool.positionedTrackHits.Path = "positionedHits"
savetrackertool.trackHits.Path = "hits"

savehisttool = SimG4SaveParticleHistory("saveHistory")
savehisttool.mcParticles.Path = "simParticles"
savehisttool.genVertices.Path = "simVertices"

# next, create the G4 algorithm, giving the list of names of tools ("XX/YY")
outputHitsTools = ["SimG4SaveTrackerHits/saveTrackerHits","SimG4SaveParticleHistory/saveHistory"]
geantsim = SimG4Alg("SimG4Alg", outputs = outputHitsTools)

if simargs.singlePart:
    from Configurables import SimG4SingleParticleGeneratorTool
    pgun=SimG4SingleParticleGeneratorTool("SimG4SingleParticleGeneratorTool", saveEdm=True,
                                          particleName=particle_geant_names[pdg], energyMin=energy * 1000, energyMax=energy * 1000,
                                          etaMin=etaMin, etaMax=etaMax, phiMin = phiMin, phiMax = phiMax)
    geantsim.eventProvider = pgun
else:

    from Configurables import PythiaInterface, GenAlg
    pythia8gentool = PythiaInterface("Pythia8",Filename=card)
    pythia8gen = GenAlg("Pythia8", SignalProvider=pythia8gentool)
    pythia8gen.hepmc.Path = "hepmc"
    from Configurables import HepMCToEDMConverter
    hepmc_converter = HepMCToEDMConverter("Converter")
    hepmc_converter.hepmc.Path="hepmc"
    hepmc_converter.genparticles.Path="allGenParticles"
    hepmc_converter.genvertices.Path="allGenVertices"
    from Configurables import SimG4PrimariesFromEdmTool
    particle_converter = SimG4PrimariesFromEdmTool("EdmConverter")
    particle_converter.genParticles.Path = "allGenParticles"
    geantsim.eventProvider = particle_converter

# Magnetic field
from Configurables import SimG4ConstantMagneticFieldTool
if magnetic_field:
    field = SimG4ConstantMagneticFieldTool("bField", FieldOn=True, IntegratorStepper="ClassicalRK4")
else:
    field = SimG4ConstantMagneticFieldTool("bField", FieldOn=False)

out = PodioOutput("out", 
                  OutputLevel=DEBUG)
#not keeping the hits
out.outputCommands = ["keep *"]

out.filename = "output.root"
if output_name != '':
    out.filename = output_name


#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
pythia8gen.AuditExecute = True
hepmc_converter.AuditExecute = True
geantsim.AuditExecute = True
out.AuditExecute = True

list_of_algorithms = [geantsim,
                      out]

if simargs.pythia:
    list_of_algorithms = [pythia8gen, hepmc_converter] + list_of_algorithms


ApplicationMgr(
    TopAlg = list_of_algorithms,
    EvtSel = 'NONE',
    EvtMax   = int(num_events),
    ExtSvc = [podioevent, geoservice, geantservice, audsvc],
 )

