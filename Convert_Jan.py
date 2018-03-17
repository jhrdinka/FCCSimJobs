import os
import sys
import math
import numpy as n
import ROOT as r
from ROOT import gSystem
gSystem.Load("libCaloAnalysis")
from ROOT import Decoder

system_decoder = Decoder("system:4")
ecalBarrel_decoder = Decoder("system:4,cryo:1,type:3,subtype:3,layer:8,eta:9,phi:10")
hcalBarrel_decoder = Decoder("system:4,module:7,row:9,layer:5,tile:2,eta:1,phi:10")
hcalExtBarrel_decoder = Decoder("system:4,module:7,row:9,layer:5,tile:2,eta:1,phi:10")
ecalEndcap_decoder = Decoder("system:4,subsystem:1,type:3,subtype:3,layer:8,eta:10,phi:10")
hcalEndcap_decoder = Decoder("system:4,subsystem:1,type:3,subtype:3,layer:8,eta:10,phi:10")
ecalFwd_decoder = Decoder("system:4,subsystem:1,type:3,subtype:3,layer:8,eta:11,phi:10")
hcalFwd_decoder = Decoder("system:4,subsystem:1,type:3,subtype:3,layer:8,eta:11,phi:10")

lastECalBarrelLayer = int(7)
lastECalEndcapLayer = int(39)
lastECalFwdLayer = int(41)

def systemID(cellid):
    system_decoder.setValue(cellid)
    return system_decoder["system"]
    
def benchmarkCorr(ecal, ecal_last, ehad, ehad_first):
    a=0.978
    b=0.479
    c=-0.0000054
    ebench = ecal*a + ehad + b * math.sqrt(math.fabs(a*ecal_last*ehad_first)) + c*(ecal*a)**2
    return ebench

def signy(y):
    if y>0: return 1
    elif y<0: return -1
    return 0

if len(sys.argv)!=3:
    print 'usage python Convert.py infile outfile'
infile_name = sys.argv[1]
outfile_name = sys.argv[2]

infile=r.TFile.Open(infile_name)
intree=infile.Get('events')

seed_eta    = n.zeros(1, dtype='float32') 
seed_phi    = n.zeros(1, dtype='float32') 
true_pt     = n.zeros(1, dtype='float32') 
true_energy = n.zeros(1, dtype='float32') 
gen_pdgid  = n.zeros(1, dtype=int) 
gen_status = n.zeros(1, dtype='float32') 

#isPionCharged etcetc
isPionCharged = n.zeros(1, dtype=int) 
isGamma       = n.zeros(1, dtype=int) 
isElectron    = n.zeros(1, dtype=int) 
isNeutralPion = n.zeros(1, dtype=int)
isMuon        = n.zeros(1, dtype=int)

cluster_eta = r.std.vector(float)()
cluster_phi = r.std.vector(float)()
cluster_pt  = r.std.vector(float)()
cluster_ene = r.std.vector(float)()
cluster_x = r.std.vector(float)()
cluster_y = r.std.vector(float)()
cluster_z = r.std.vector(float)()

rec_eta = r.std.vector(float)()
rec_phi = r.std.vector(float)()
rec_pt  = r.std.vector(float)()
rec_ene = r.std.vector(float)()
rec_x = r.std.vector(float)()
rec_y = r.std.vector(float)()
rec_z = r.std.vector(float)()
rec_layer = r.std.vector(float)()
rec_detid = r.std.vector(int)()

outfile=r.TFile(outfile_name,"recreate")

outtree=r.TTree('tree','tree') 

maxEvent = intree.GetEntries()
print 'Number of events : ',maxEvent

ev_num = n.zeros(1, dtype=int) 
ev_e =  n.zeros(1, dtype=float)
ev_ebench =  n.zeros(1, dtype=float)
nrechits = n.zeros(1, dtype=int) 

outtree.Branch("ev_num", ev_num, "ev_num/I")
outtree.Branch("ev_e", ev_e, "ev_e/D")
outtree.Branch("ev_ebench", ev_ebench, "ev_ebench/D")
outtree.Branch("nrechits", nrechits, "nrechits/F")

outtree.Branch("cluster_pt", cluster_pt)
outtree.Branch("cluster_eta", cluster_eta)
outtree.Branch("cluster_phi", cluster_phi)
outtree.Branch("cluster_energy", cluster_ene)
outtree.Branch("cluster_x", cluster_x)
outtree.Branch("cluster_y", cluster_y)
outtree.Branch("cluster_z", cluster_z)

outtree.Branch("rechit_pt", rec_pt)
outtree.Branch("rechit_eta", rec_eta)
outtree.Branch("rechit_phi", rec_phi)
outtree.Branch("rechit_energy", rec_ene)
outtree.Branch("rechit_layer", rec_layer)
outtree.Branch("rechit_x", rec_x)
outtree.Branch("rechit_y", rec_y)
outtree.Branch("rechit_z", rec_z)
outtree.Branch("rechit_detid", rec_detid)


outtree.Branch("true_pt",     true_pt, "true_pt/F")
outtree.Branch("seed_eta",    seed_eta, "true_pt/F")
outtree.Branch("seed_phi",    seed_phi, "true_pt/F")
outtree.Branch("true_energy", true_energy, "true_pt/F")
outtree.Branch("gen_status",  gen_status, "true_pt/F")
outtree.Branch("gen_pdgid",   gen_pdgid, "true_pt/I")

outtree.Branch("isPionCharged", isPionCharged, "isPionCharged/I")
outtree.Branch("isGamma",       isGamma,       "isGamma/I")
outtree.Branch("isElectron",    isElectron,    "isElectron/I")
outtree.Branch("isNeutralPion",    isNeutralPion,    "isNeutralPion/I")
outtree.Branch("isMuon",    isMuon,    "isMuon/I")

numEvent = 0
for event in intree:
    ev_num[0] = numEvent
    numHits = 0
    E = .0
    Ebench = .0
    Eem = 0
    Ehad = 0
    EemLast = 0
    EhadFirst = 0
    
    #loops over gen particles
    # the tree will be filled for every gen particle in the event
    # the gen particle will be used as seed directly
    
    if event.GetBranchStatus("GenParticles"):
        for g in event.GenParticles:
            position = r.TVector3(g.core.p4.px,g.core.p4.py,g.core.p4.pz)
            
            pt=math.sqrt(g.core.p4.px**2+g.core.p4.py**2)
            eta=position.Eta()
            phi=position.Phi()
            
            tlv=r.TLorentzVector()
            tlv.SetPtEtaPhiM(pt,eta,phi,g.core.p4.mass)
            true_pt[0]=pt
            seed_eta[0]=eta
            seed_phi[0]=phi
            true_energy[0]=(math.sqrt(g.core.p4.mass**2+g.core.p4.px**2+g.core.p4.py**2+g.core.p4.pz**2))

            if math.fabs(tlv.E()-math.sqrt(g.core.p4.mass**2+g.core.p4.px**2+g.core.p4.py**2+g.core.p4.pz**2))>0.01 and g.core.status==1:
                print '=======================etlv  ',tlv.E(),'    ',math.sqrt(g.core.p4.mass**2+g.core.p4.px**2+g.core.p4.py**2+g.core.p4.pz**2),'  eta  ',eta,'   phi   ',phi,'  x  ',g.core.p4.px,'  y  ',g.core.p4.py,'  z  ',g.core.p4.pz
            gen_pdgid[0]=g.core.pdgId
            gen_status[0]=g.core.status
            
            
            # one-hot encoded input for categorisation
            
            isPionCharged[0]=0
            isGamma[0]=0
            isElectron[0]=0
            isNeutralPion[0]=0
            isMuon[0]=0

            if abs(g.core.pdgId)==211:
                isPionCharged[0]=1
            elif abs(g.core.pdgId)==11:
                isElectron[0]=1
            elif abs(g.core.pdgId)==22:
                isGamma[0]=1
            elif abs(g.core.pdgId)==111:
                isNeutralPion[0]=1
            elif abs(g.core.pdgId)==13:
                isMuon[0]=1
            ##etc.

            if event.GetBranchStatus("caloClustersBarrel"):
                for c in event.caloClustersBarrel:
                    position = r.TVector3(c.core.position.x,c.core.position.y,c.core.position.z)
                    cluster_ene.push_back(c.core.energy)
                    cluster_eta.push_back(position.Eta())
                    cluster_phi.push_back(position.Phi())
                    cluster_pt.push_back(c.core.energy*position.Unit().Perp())
                    cluster_x.push_back(c.core.position.x/10.)
                    cluster_y.push_back(c.core.position.y/10.)
                    cluster_z.push_back(c.core.position.z/10.)
            
            else:
                for c in event.HCalBarrelCellPositions:
                    hcalBarrel_decoder.setValue(c.core.cellId)
                    position = r.TVector3(c.position.x,c.position.y,c.position.z)
                    rec_ene.push_back(c.core.energy)
                    rec_eta.push_back(position.Eta())
                    rec_phi.push_back(position.Phi())
                    rec_pt.push_back(c.core.energy*position.Unit().Perp())
                    rec_layer.push_back(hcalBarrel_decoder["layer"] + lastECalBarrelLayer + 1)
                    rec_x.push_back(c.position.x/10.)
                    rec_y.push_back(c.position.y/10.)
                    rec_z.push_back(c.position.z/10.)
                    rec_detid.push_back(systemID(c.core.cellId))
                    if hcalBarrel_decoder["layer"] == 0:
                        EhadFirst += c.core.energy
                    E += c.core.energy
                    Ehad += c.core.energy
                    numHits += 1
            
                for c in event.ECalBarrelCellPositions:
                    ecalBarrel_decoder.setValue(c.core.cellId)
                    position = r.TVector3(c.position.x,c.position.y,c.position.z)
                    rec_ene.push_back(c.core.energy)
                    rec_eta.push_back(position.Eta())
                    rec_phi.push_back(position.Phi())
                    rec_pt.push_back(c.core.energy*position.Unit().Perp())
                    rec_layer.push_back(ecalBarrel_decoder["layer"])
                    rec_x.push_back(c.position.x/10.)
                    rec_y.push_back(c.position.y/10.)
                    rec_z.push_back(c.position.z/10.)
                    rec_detid.push_back(systemID(c.core.cellId))
                    if ecalBarrel_decoder["layer"] == lastECalBarrelLayer:
                        EemLast += c.core.energy
                    E += c.core.energy
                    Eem += c.core.energy
                    numHits += 1
            
                for c in event.HCalExtBarrelCellPositions:
                    hcalExtBarrel_decoder.setValue(c.core.cellId)
                    position = r.TVector3(c.position.x,c.position.y,c.position.z)
                    rec_ene.push_back(c.core.energy)
                    rec_eta.push_back(position.Eta())
                    rec_phi.push_back(position.Phi())
                    rec_pt.push_back(c.core.energy*position.Unit().Perp())
                    rec_layer.push_back(hcalExtBarrel_decoder["layer"] + lastECalBarrelLayer + 1)
                    rec_x.push_back(c.position.x/10.)
                    rec_y.push_back(c.position.y/10.)
                    rec_z.push_back(c.position.z/10.)
                    rec_detid.push_back(systemID(c.core.cellId))
                    E += c.core.energy
                    numHits += 1
                    
                for c in event.ECalEndcapCellPositions:
                    ecalEndcap_decoder.setValue(c.core.cellId)
                    position = r.TVector3(c.position.x,c.position.y,c.position.z)
                    rec_ene.push_back(c.core.energy)
                    rec_eta.push_back(position.Eta())
                    rec_phi.push_back(position.Phi())
                    rec_pt.push_back(c.core.energy*position.Unit().Perp())
                    rec_layer.push_back(ecalEndcap_decoder["layer"])
                    rec_x.push_back(c.position.x/10.)
                    rec_y.push_back(c.position.y/10.)
                    rec_z.push_back(c.position.z/10.)
                    rec_detid.push_back(systemID(c.core.cellId))
                    E += c.core.energy
                    numHits += 1
            
                for c in event.HCalEndcapCellPositions:
                    hcalEndcap_decoder.setValue(c.core.cellId)
                    position = r.TVector3(c.position.x,c.position.y,c.position.z)
                    rec_ene.push_back(c.core.energy)
                    rec_eta.push_back(position.Eta())
                    rec_phi.push_back(position.Phi())
                    rec_pt.push_back(c.core.energy*position.Unit().Perp())
                    rec_layer.push_back(hcalEndcap_decoder["layer"] + lastECalEndcapLayer + 1)
                    rec_x.push_back(c.position.x/10.)
                    rec_y.push_back(c.position.y/10.)
                    rec_z.push_back(c.position.z/10.)
                    rec_detid.push_back(systemID(c.core.cellId))
                    E += c.core.energy
                    numHits += 1
            
                for c in event.ECalFwdCellPositions:
                    ecalFwd_decoder.setValue(c.core.cellId)
                    position = r.TVector3(c.position.x,c.position.y,c.position.z)
                    rec_ene.push_back(c.core.energy)
                    rec_eta.push_back(position.Eta())
                    rec_phi.push_back(position.Phi())
                    rec_pt.push_back(c.core.energy*position.Unit().Perp())
                    rec_layer.push_back(ecalFwd_decoder["layer"])
                    rec_x.push_back(c.position.x/10.)
                    rec_y.push_back(c.position.y/10.)
                    rec_z.push_back(c.position.z/10.)
                    rec_detid.push_back(systemID(c.core.cellId))
                    E += c.core.energy
                    numHits += 1
            
                for c in event.HCalFwdCellPositions:
                    hcalFwd_decoder.setValue(c.core.cellId)
                    position = r.TVector3(c.position.x,c.position.y,c.position.z)
                    rec_ene.push_back(c.core.energy)
                    rec_eta.push_back(position.Eta())
                    rec_phi.push_back(position.Phi())
                    rec_pt.push_back(c.core.energy*position.Unit().Perp())
                    rec_layer.push_back(hcalFwd_decoder["layer"] + lastECalFwdLayer + 1)
                    rec_x.push_back(c.position.x/10.)
                    rec_y.push_back(c.position.y/10.)
                    rec_z.push_back(c.position.z/10.)
                    rec_detid.push_back(systemID(c.core.cellId))
                    E += c.core.energy
                    numHits += 1
            
            ev_ebench[0] = benchmarkCorr(Eem,EemLast,Ehad,EhadFirst)
            ev_e[0] = E
            nrechits[0] = numHits
            
            outtree.Fill()
            
            
            cluster_eta.clear()
            cluster_phi.clear()
            cluster_pt.clear()
            cluster_ene.clear()
            cluster_x.clear()
            cluster_y.clear()
            cluster_z.clear()
            
            rec_eta.clear()
            rec_phi.clear()
            rec_pt.clear()
            rec_ene.clear()
            rec_layer.clear()
            rec_x.clear()
            rec_y.clear()
            rec_z.clear()
            rec_detid.clear()
            
            numEvent += 1

outtree.Write()
outfile.Write()
outfile.Close()

