import FWCore.ParameterSet.Config as cms

from FWCore.ParameterSet.VarParsing import VarParsing
FLAGS = VarParsing('analysis')
FLAGS.register('isScan', 0,
               VarParsing.multiplicity.singleton,
               VarParsing.varType.int,
               "whether we run the default or a parameter scan")
FLAGS.register('criticalDensity', 0.6,
               VarParsing.multiplicity.singleton,
               VarParsing.varType.float,
               "critical density in GeV")
FLAGS.register('criticalEtaPhiDistance', 0.025,
               VarParsing.multiplicity.singleton,
               VarParsing.varType.float,
               "Minimal distance in eta,phi space from nearestHigher to become a seed")
FLAGS.register('kernelDensityFactor', 0.2,
               VarParsing.multiplicity.singleton,
               VarParsing.varType.float,
               "Kernel factor to be applied to other LC while computing the local density")
FLAGS.parseArguments()

from Configuration.StandardSequences.Eras import eras
from Configuration.Eras.Era_Phase2C17I13M9_cff import Phase2C17I13M9

process = cms.Process('TEST', Phase2C17I13M9)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
#process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('SimGeneral.MixingModule.mix_POISSON_average_cfi')
#process.load('Configuration.Geometry.GeometryExtended2026D49Reco_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('Configuration.StandardSequences.RawToDigi_cff')
process.load('Configuration.StandardSequences.L1Reco_cff')
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.RecoSim_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
process.load('Configuration.Geometry.GeometryExtended2026D88_cff')
process.load('Configuration.Geometry.GeometryExtended2026D88Reco_cff')

from FastSimulation.Event.ParticleFilter_cfi import *

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring('file:step2.root'),
    secondaryFileNames = cms.untracked.vstring(),
    skipEvents = cms.untracked.uint32(20),
    duplicateCheckMode = cms.untracked.string('noDuplicateCheck'),
    dropDescendantsOfDroppedBranches=cms.untracked.bool(False),
    inputCommands=cms.untracked.vstring(
        'keep *',
        'drop *l1tTkPrimaryVertexs_L1TkPrimaryVertex__HLT',
    )
)

process.options = cms.untracked.PSet(
    FailPath = cms.untracked.vstring(),
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    SkipEvent = cms.untracked.vstring(),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(1)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    makeTriggerResults = cms.obsolete.untracked.bool,
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(1),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(1),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False)
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('step3 nevts:10'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition
process.FEVTDEBUGHLToutput = cms.OutputModule("PoolOutputModule",
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('GEN-SIM-RECO'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:step3.root'),
    outputCommands = process.FEVTDEBUGHLTEventContent.outputCommands,
    splitLevel = cms.untracked.int32(0)
)

process.ticlTrackstersCLUE3DHigh.criticalDensity = cms.double(FLAGS.criticalDensity)
process.ticlTrackstersCLUE3DHigh.criticalEtaPhiDistance = cms.double(FLAGS.criticalEtaPhiDistance)
process.ticlTrackstersCLUE3DHigh.kernelDensityFactor = cms.double(FLAGS.kernelDensityFactor)
#process.particleFlowClusterHGCal.initialClusteringStep.filterByTracksterPID = cms.bool(True)

process.ticlMultiClustersFromTrackstersTEST = cms.EDProducer(
    "MultiClustersFromTrackstersProducer",
    LayerClusters = cms.InputTag("hgcalLayerClusters"),
    mightGet = cms.optional.untracked.vstring,
    verbosity = cms.untracked.uint32(3)
)
if FLAGS.isScan:
    process.ticlMultiClustersFromTrackstersTEST.Tracksters = cms.InputTag("ticlTrackstersCLUE3DHigh"), ## raw tracksters clue3d
else:
    process.ticlMultiClustersFromTrackstersTEST.Tracksters = cms.InputTag("ticlTrackstersMerge"), ## merged tracksters

process.ana = cms.EDAnalyzer(
    'HGCalAnalysis',
    detector = cms.string("all"),
    inputTag_HGCalMultiCluster = cms.string("ticlMultiClustersFromTrackstersTEST"),
    inputTag_Reco = cms.string("TEST"),  ## switch reco collection to use
    inputTag_ReReco = cms.string("TEST"),  ## switch reco collection to use
    # inputTag_HGCalMultiCluster = cms.string("hgcalMultiClusters"),
    CaloHitSourceEE = cms.string("HGCHitsEE"),
    CaloHitSourceHEfront = cms.string("HGCHitsHEfront"),
    CaloHitSourceHEback = cms.string("HGCHitsHEback"),
    rawRecHits = cms.bool(True),
    verbose = cms.bool(True),
    readCaloParticles = cms.bool(True),
    storeGenParticleOrigin = cms.bool(True),
    storeGenParticleExtrapolation = cms.bool(True),
    storeElectrons = cms.bool(True),
    storePFCandidates = cms.bool(True),
    storeGunParticles = cms.bool(True),
    readGenParticles = cms.bool(True),
    layerClusterPtThreshold = cms.double(-1),  # All LayerCluster belonging to a multicluster are saved; this Pt threshold applied to the others
    TestParticleFilter = ParticleFilterBlock.ParticleFilter
)

process.TFileService = cms.Service("TFileService",
                                   fileName = cms.string("file:step3.root"))

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, 'auto:phase2_realistic_T21', '')

# Path and EndPath definitions
process.raw2digi_step = cms.Path(process.RawToDigi)
process.L1Reco_step = cms.Path(process.L1Reco)
process.reconstruction_step = cms.Path(process.reconstruction)
process.recosim_step = cms.Path(process.recosim)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.FEVTDEBUGHLToutput_step = cms.EndPath(process.FEVTDEBUGHLToutput)
process.analyze_step = cms.Path(process.ana)
#process.analyze_step2 = cms.Path(process.HGCANALYZE)
#process.extendclue3d = cms.Path(process.ticlTrackstersCLUE3DHighTEST*process.ticlMultiClustersFromTrackstersTEST)
process.extendclue3d = cms.Path(process.ticlMultiClustersFromTrackstersTEST)

rereco = True
if rereco:
    # Schedule definition
    #    process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.recosim_step,process.analyze_step2,process.endjob_step)#,process.FEVTDEBUGHLToutput_step)
    #    process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.recosim_step,process.analyze_step,process.endjob_step)#,process.FEVTDEBUGHLToutput_step) ##### used for actual reco+ntupler last 05/07/2021
    #process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.extendclue3d,process.recosim_step,process.analyze_step,process.endjob_step)
    #    process.schedule = cms.Schedule(process.reconstruction_step,process.analyze_step,process.endjob_step)
    #    process.schedule = cms.Schedule(process.analyze_step,process.endjob_step)
    process.schedule = cms.Schedule(process.raw2digi_step,process.reconstruction_step,process.extendclue3d,process.analyze_step,process.endjob_step)



#    process.schedule = cms.Schedule(process.raw2digi_step,process.L1Reco_step,process.reconstruction_step,process.recosim_step,process.endjob_step,process.FEVTDEBUGHLToutput_step)
    from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
    associatePatAlgosToolsTask(process)



    # Customisation from command line

    #Have logErrorHarvester wait for the same EDProducers to finish as those providing data for the OutputModule
    from FWCore.Modules.logErrorHarvester_cff import customiseLogErrorHarvesterUsingOutputCommands
    process = customiseLogErrorHarvesterUsingOutputCommands(process)

    # Add early deletion of temporary data products to reduce peak memory need
    from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
    process = customiseEarlyDelete(process)
    # End adding early deletion

else:
    process.schedule = cms.Schedule(process.analyze_step2)#,process.FEVTDEBUGHLToutput_step)
