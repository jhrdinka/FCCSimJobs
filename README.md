#FCCSimJobs
This package is used to centrally produced full simulation events for FCC-hh a center of mass of 100. Any other future collider can also be supported by this framework. 
In order to use it, please get in contact with clement.helsens@cern.ch as running this package requieres specific rights.

Table of contents
=================
  * [FCCSimJobs](#fccsimjobs)
  * [Table of contents](#table-of-contents)
  * [Clone and initialisation](#clone-and-initialisation)
  * [Sending simulation jobs](#sending-simulation-jobs)
     * [Single Particles](#single-particles)
     * [Physics](#physics)
     * [Common options](#common-options)
     * [FCCSW configuration](#fccsw-configuration)
     * [Running examples](#running-examples)
        * [Simulation](#simulation)
        * [Reconstruction](#reconstruction)
     * [Miscellaneous](#miscellaneous)
     * [Expert mode](#expert-mode)

Clone and initialisation
========================

If you do not attempt to contribute to the repository, simply clone it:
```
git clone git@github.com:clementhelsens/FCCSimJobs.git
```

If you aim at contributing to the repository, you need to fork and then clone the forked repository:
```
git clone git@github.com:YOURGITUSERNAME/FCCSimJobs.git
```

Sending simulation jobs
=======================
Various options are available and are explained below. 

Single Particles
================
If **--singlePart** is used, the following options are possible:
   - **--particle** for the particle ID. The supported ones are 11(e-), -11(e+), -13(mu-), 13(mu+), 22, 111(pi0), 211(pi+), -211(pi-), 130(K0L). For example to run single anti-muon, use **--particle -13**
   - the angle is changed using **--phiMin** and **--phiMax**, default are 0 and 2pi respectively
   
 
Physics
=======
If **--physics** is used, the following options are possible
   - **--process** to select the type of process. Two types are available
      - from LHE events, this will call a gun that will produce 2 back to back objects, the following keys are available **ljets**, **cjets**, **bjets**, **top**, **Wqq**, **Zqq**, **Hbb**. If this option is used, the pt can also be given using **--pt**
      - from calling pythia8 direcly, thus generating the events at 100TeV, the following keys are available **MinBias**, **Haa**, **Zee**, **H4e**
      

Common options
==============
There are common options
   - the pseudo-rapidity range is changed using **--etaMin** and **--etaMax**, default is 0 for both 
   - the batch system is either **--lsf**  or **--condor**
   - the number of events per job is configured through **-n**
   - and the number of jobs to send is configured through **-N**

FCCSW configuration
===================
The default FCC Software verson is 0.9.1 taken from
```
/cvmfs/fcc.cern.ch/sw/releases/0.9.1/x86_64-slc6-gcc62-opt/linux-scientificcernslc6-x86_64/gcc-6.2.0/fccsw-0.9.1-c5dqdyv4gt5smfxxwoluqj2pjrdqvjuj
```
   - the **--local** option allows to initialize local SW installation, add your path in inits/private.py script
   - the cell positions reconstruction is running only on local SW installation (/afs/cern.ch/work/c/cneubuse/public/TopoClusters/FCCSW/), to use this add **--local inits/reco.py**
   - the topo-clusters reconstruction is running only on local SW installation (/afs/cern.ch/work/c/cneubuse/public/TopoClusters/FCCSW/), to use this add **--local inits/reco.py**
 

Running examples
================

Simulation
==========
```
python python/send.py --singlePart --particle 11 -e 500 -n 10 -N 1 --condor --etaMin 3.5 --etaMax 3.5
python python/send.py --singlePart --particle -211 -e 10 -n 10 -N 1 --condor
python python/send.py --physics --process Zqq --pt 1000 -n 10 -N 1 --lsf
python python/send.py --physics --process Haa -n 10 -N 1 --lsf
```

Reconstruction
==============

```
python python/send.py --singlePart --particle 11 -e 500 -N 1 --condor --etaMin 3.5 --etaMax 3.5 --recSlidingWindow
python python/send.py --singlePart --particle -211 -e 10 -N 1 --condor --recSlidingWindow --noise
python python/send.py --physics --process Zqq --pt 1000 -N 1 --lsf --recSlidingWindow
python python/send.py --physics --process Haa  -N 1 --lsf --recSlidingWindow
python python/send.py --local inits/reco.py --singlePart --particle 11 -e 100 -N 1 --condor --recPositions
```
to run the topo-clustering:
```
python python/send.py --local inits/reco.py --physics --process MinBias -N 1 --lsf --recTopoClusters

```
- to add electronics noise in the reconstruction step, add **--noise**
- to include pileup noise, add **--addPileupNoise** and specify the pileup configuration with **--pileup** (choose from: 100, 200, 500 or 1000) 
```
python python/send.py --local inits/reco.py --physics --process MinBias -N 1 --lsf --recTopoClusters --noise
python python/send.py --local inits/reco.py --physics --process MinBias -N 1 --lsf --recTopoClusters --addPileupNoise --mu 100
```

Pileup
==============

There are several approaches of addressing the pile-up in the detector:

1. Apply noise in the detector that represents the noise introduced by the simultanous collisions. The offset in the energy deposit is assumed to be corrected for.

- estimation of the pile-up noise per cell and per cluster (only in ECal detector at the moment) can be done using **--estimatePileup** job option.
  It creates histograms filling in the information on the deposits per event. This can be later scaled with *sqrt(mu)* for the noise (RMS of the energy distributions) and with *mu* for the mean energy deposit.
  Detailed analysis and this scaling is done with FCC_calo_analysis_cpp toolkit.

- apply estimated noise levels at the cluster level for sliding window reconstruction or per cell for the topological clusters (**--addPileupNoise**).

2. Mix already simulated events in order to overlay:


2.1. merge MinBias events (**--mergePileup**)

2.2. merge signal and PU events that are later passed to the reconstruction (**--addPileupToSignal**)
```
python python/send.py --singlePart --particle -211 -e 10 --addPileupToSignal --pileup 200 --local inits/pileup.py -N 1 --lsf
```

Miscellaneous
==============
Formatting rules:
- The directory names are used to identify their content. Please make sure that their are:
  - only root files with **edm classes** in /simu/ and /reco/
  - only root files with **ntuples** in /ntup/
  - and **all other** types of outputs in /ana/ 
If this is not followed, the files can be lost, due to the automatic cleaning of "bad" jobs/output files.

- Also, please often check the afs directory where the jobs where send, because there will be the log files stored there as well as the output root file when running on condor (needs to be understood)

- Few times a day, a script will run to check the jobs that have been processed and the results will be published on this webpage
http://fcc-physics-events.web.cern.ch/fcc-physics-events/FCCsim_v01.php

- Once in a while you can run the clean script to remove all the jobs that are marked as failed in the database.
This is something that can not be done centrally yet as I do not have rights to remove files I haven't produced.

Expert mode
===========
check for a given process
```
python python/run.py --check --version v03 --process physics/MinBias/bFieldOn/etaFull/simu
```

check for everything
```
python python/run.py --check --version v03
```

merge the yaml
```
python python/run.py --merge --version v03
```

clean the yaml from bad jobs
```
python python/run.py --clean --version v03
```

clean the yaml from old jobs that have not produced corrupted output files
```
python python/run.py --cleanold --version v03
```

make the web page
```
python python/run.py --web --version v03
```



WARNING
===========

Official installation of FCCSW does not support certain options (not yet in the release). Please check the following list for the recommended versions:

```
--mergePileup --local inits/pileup.py
--addPileupToSignal --local inits/pileup.py
--estimatePileup --local inits/pileup.py
--recPositions --local inits/reco.py
--recTopoClusters --local inits/reco.py
```
