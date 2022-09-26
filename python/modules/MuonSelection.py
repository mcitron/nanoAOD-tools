import os
import sys
import math
import json
import ROOT
import random
import numpy as np 

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from utils import getGraph, getHist, getHistCanvas, combineHist2D, getSFXY, deltaR

class MuonSelection(Module):
    TIGHT = 1
    MEDIUM = 2
    LOOSE = 3
    NONE = 4
    INV = 5

    def __init__(
        self,
        inputCollection=lambda event: Collection(event, "Muon"),
        outputName="tightMuons",
        muonID=TIGHT,
        muonIso=TIGHT,
        muonMinPt=25.,
        muonMaxEta=2.4,
        muonMaxDxy=-1.,
        muonMaxDz=-1.,
        storeKinematics=['pt','eta'],
        storeWeights=False,
        selectLeadingOnly=False,
        globalOptions={"isData":False, "year":2016}
    ):
        
        self.globalOptions = globalOptions
        self.inputCollection = inputCollection
        self.outputName = outputName
        self.muonMinPt = muonMinPt
        self.muonMaxEta = muonMaxEta
        self.muonMaxDxy = muonMaxDxy
        self.muonMaxDz = muonMaxDz
        self.storeKinematics = storeKinematics
        self.storeWeights = storeWeights
        self.selectLeadingOnly = selectLeadingOnly
        self.muonID=muonID

        if muonID==MuonSelection.MEDIUM or muonIso==MuonSelection.MEDIUM:
            print("Unsupported ID or ISO")
            sys.exit(1)

        if self.storeWeights:

            if self.globalOptions["year"] == 2016:
                #tight id efficiency
                idTightSFBToF = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/RunBCDEF_SF_ID.root",
                    "NUM_TightID_DEN_genTracks_eta_pt"
                )
                idTightSFGToH = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/RunGH_SF_ID.root",
                    "NUM_TightID_DEN_genTracks_eta_pt"
                )
                self.idTightSFHist = combineHist2D(
                    idTightSFBToF,
                    idTightSFGToH,
                    1.-16226.5/35916.4,
                    16226.5/35916.4
                )
                
                #loose id efficiency
                idLooseSFBToF = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/RunBCDEF_SF_ID.root",
                    "NUM_LooseID_DEN_genTracks_eta_pt"
                )
                idLooseSFGToH = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/RunGH_SF_ID.root",
                    "NUM_LooseID_DEN_genTracks_eta_pt"
                )

                self.idLooseSFHist = combineHist2D(
                    idLooseSFBToF,
                    idLooseSFGToH,
                    1.-16226.5/35916.4,
                    16226.5/35916.4
                )
                
                
                #tight iso and tight id efficiency
                isoTightTightSFBToF = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/RunBCDEF_SF_ISO.root",
                    "NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt"
                )
                isoTightTightSFGToH = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/RunGH_SF_ISO.root",
                    "NUM_TightRelIso_DEN_TightIDandIPCut_eta_pt"
                )
                self.isoTightTightSFHist = combineHist2D(
                    isoTightTightSFBToF,
                    isoTightTightSFGToH,
                    1.-16226.5/35916.4,
                    16226.5/35916.4
                )
                
                #loose iso and loose id efficiency
                # isoLooseLooseSFBToF = getHist(
                #     "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/RunBCDEF_SF_ISO.root",
                #     "NUM_LooseRelIso_DEN_LooseID_eta_pt"
                # )
                # isoLooseLooseSFGToH = getHist(
                #     "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/RunGH_SF_ISO.root",
                #     "NUM_LooseRelIso_DEN_LooseID_eta_pt"
                # )
                
                # self.isoLooseLooseSFHist = combineHist2D(
                #     isoLooseLooseSFBToF,
                #     isoLooseLooseSFGToH,
                #     1.-16226.5/35916.4,
                #     16226.5/35916.4
                # )

                # self.isoLooseLooseSFHist = getHistCanvas(
                #     "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/NUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt.root",
                #     "cNUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt", "NUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt"
                # )
                self.isoLooseLooseSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/scale_factor2D_absdxy_sig_pt_TnP_2016.root",
                    "scale_factors_2016"
                )

                self.recoSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2016/rootfiles/scale_factor2D_absdxy_pt_TnP_reco_2016.root",
                    "scale_factors_2016"
                )

            elif self.globalOptions["year"] == 2017:
                #tight id efficiency
                self.idTightSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2017/rootfiles/RunBCDEF_SF_ID.root",
                    "NUM_TightID_DEN_genTracks_pt_abseta"
                )
                
                #loose id efficiency
                self.idLooseSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2017/rootfiles/RunBCDEF_SF_ID.root",
                    "NUM_LooseID_DEN_genTracks_pt_abseta"
                )
                
                #tight iso and tight id efficiency
                self.isoTightTightSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2017/rootfiles/RunBCDEF_SF_ISO.root",
                    "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta"
                )
                
                #loose iso and loose id efficiency
                # self.isoLooseLooseSFHist = getHist(
                #     "PhysicsTools/NanoAODTools/data/muon/2017/rootfiles/RunBCDEF_SF_ISO.root",
                #     "NUM_LooseRelIso_DEN_LooseID_pt_abseta"
                # )
                # self.isoLooseLooseSFHist = getHistCanvas(
                #     "PhysicsTools/NanoAODTools/data/muon/2017/rootfiles/NUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt.root",
                #     "cNUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt", "NUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt"
                # )
                self.isoLooseLooseSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2017/rootfiles/scale_factor2D_absdxy_sig_pt_TnP_2017.root",
                    "scale_factors_2017"
                )

                self.recoSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2017/rootfiles/scale_factor2D_absdxy_pt_TnP_reco_2017.root",
                    "scale_factors_2017"
                )

            elif self.globalOptions["year"] == 2018:

                #tight id efficiency
                self.idTightSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2018/rootfiles/RunABCD_SF_ID.root",
                    "NUM_TightID_DEN_TrackerMuons_pt_abseta"
                )
                
                #loose id efficiency
                self.idLooseSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2018/rootfiles/RunABCD_SF_ID.root",
                    "NUM_LooseID_DEN_TrackerMuons_pt_abseta"
                )
                
                #tight iso and tight id efficiency
                self.isoTightTightSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2018/rootfiles/RunABCD_SF_ISO.root",
                    "NUM_TightRelIso_DEN_TightIDandIPCut_pt_abseta"
                )
                
                #loose iso and loose id efficiency
                # self.isoLooseLooseSFHist = getHist(
                #     "PhysicsTools/NanoAODTools/data/muon/2018/rootfiles/RunABCD_SF_ISO.root",
                #     "NUM_LooseRelIso_DEN_LooseID_pt_abseta"
                # )
                # self.isoLooseLooseSFHist = getHistCanvas(
                #     "PhysicsTools/NanoAODTools/data/muon/2018/rootfiles/NUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt.root",
                #     "cNUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt", "NUM_LooseID_DEN_TrackerMuons_absdxy_sig_pt"
                # )
                self.isoLooseLooseSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2018/rootfiles/scale_factor2D_absdxy_sig_pt_TnP_2018.root",
                    "scale_factors_2018"
                )

                self.recoSFHist = getHist(
                    "PhysicsTools/NanoAODTools/data/muon/2018/rootfiles/scale_factor2D_absdxy_pt_TnP_reco_2018.root",
                    "scale_factors_2018"
                )

            else:
                print "Error - invalid year"
                sys.exit(1)

        if muonID==MuonSelection.TIGHT:
            self.muonId = lambda muon: muon.tightId==1
            if self.storeWeights:
                self.muonIdSF = self.idTightSFHist
        elif muonID==MuonSelection.LOOSE:
            self.muonId = lambda muon: muon.looseId==1
            if self.storeWeights:
                self.muonIdSF = self.isoLooseLooseSFHist
        elif muonID==MuonSelection.NONE:
            self.muonId = lambda muon: True
            if self.storeWeights:
                self.muonIdSF = self.idLooseSFHist
            
        if muonIso==MuonSelection.TIGHT:
            self.muonIso = lambda muon: muon.pfRelIso04_all<0.15
            if muonID==MuonSelection.TIGHT:
                if self.storeWeights:
                    self.muonIsoSF = self.isoTightTightSFHist
            elif muonID==MuonSelection.LOOSE:
                if self.storeWeights:
                    self.muonIsoSF = self.isoLooseTightSFHist

            else:
                print "Error - unsupported combination"
                sys.exit(1)

        elif muonIso==MuonSelection.LOOSE:
            self.muonIso = lambda muon: muon.pfRelIso04_all<0.25
            if muonID==MuonSelection.LOOSE:
                if self.storeWeights:
                    self.muonIsoSF = self.isoLooseLooseSFHist
            else:
                print "Error - unsupported combination"
                sys.exit(1)

        elif muonIso==MuonSelection.NONE:
            self.muonIso = lambda muon: True
            if self.storeWeights:
                if muonID==MuonSelection.TIGHT:
                    self.muonIsoSF = self.isoTightTightSFHist
                elif muonID==MuonSelection.LOOSE:
                    self.muonIsoSF = self.isoLooseLooseSFHist
                elif muonID==MuonSelection.NONE:
                    self.muonIsoSF = self.isoLooseLooseSFHist
                else:
                    print "Error - unsupported combination"
                    sys.exit(1)
                
        elif muonIso==MuonSelection.INV:
            self.muonIso = lambda muon: muon.pfRelIso04_all>0.25 and muon.pfRelIso04_all<0.8
            self.storeWeights = False
 
    def beginJob(self):
        pass
        
    def endJob(self):
        pass
        
    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("n"+self.outputName, "I")

        for variable in self.storeKinematics:
            self.out.branch(self.outputName+"_"+variable,"F",lenVar="n"+self.outputName)
            
        if not self.globalOptions["isData"] and self.storeWeights:
            self.out.branch(self.outputName+"_weight_id_nominal","F")
            self.out.branch(self.outputName+"_weight_id_up","F")
            self.out.branch(self.outputName+"_weight_id_down","F")
            
            self.out.branch(self.outputName+"_weight_iso_nominal","F")
            self.out.branch(self.outputName+"_weight_iso_up","F")
            self.out.branch(self.outputName+"_weight_iso_down","F")

            self.out.branch(self.outputName+"_weight_reco_nominal","F")
            self.out.branch(self.outputName+"_weight_reco_up","F")
            self.out.branch(self.outputName+"_weight_reco_down","F")
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass
        
    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        muons = self.inputCollection(event)

        selectedMuons = []
        unselectedMuons = []
        
        #https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideMuonIdRun2#Tight_Muon
        for muon in muons:
            muon.genPartFlav = -999
            if muon.pt>self.muonMinPt and math.fabs(muon.eta)<self.muonMaxEta and self.muonId(muon) and self.muonIso(muon):
                if self.muonMaxDxy > 0. and abs(muon.dxy) > self.muonMaxDxy:
                    unselectedMuons.append(muon)
                    continue
                if self.muonMaxDz > 0. and abs(muon.dz) > self.muonMaxDz:
                    unselectedMuons.append(muon)
                    continue
                selectedMuons.append(muon)                    
            else:
                unselectedMuons.append(muon)

        if len(selectedMuons) > 0 and self.selectLeadingOnly:
            unselectedMuons.extend(selectedMuons[1:])
            selectedMuons = [selectedMuons[0]]

        if not self.globalOptions["isData"] and self.storeWeights:
            weight_id_nominal = []
            weight_id_up = []
            weight_id_down = []
            
            weight_iso_nominal = []
            weight_iso_up = []
            weight_iso_down = []

            weight_reco_nominal = []
            weight_reco_up = []
            weight_reco_down = []

            for muon in selectedMuons:
                if self.globalOptions["year"] == 2016:
                    weight_id,weight_id_err = getSFXY(self.muonIdSF,muon.eta,muon.pt)
                elif self.globalOptions["year"] == 2017 or self.globalOptions["year"] == 2018:
                    weight_id,weight_id_err = getSFXY(self.muonIdSF,muon.pt, abs(muon.eta))

                if self.muonID==MuonSelection.LOOSE:
                    weight_id,weight_id_err = getSFXY(self.muonIdSF,abs(muon.dxy)/(1e-5+abs(muon.dxyErr)),muon.pt)

                weight_id_nominal.append(weight_id)
                weight_id_up.append((weight_id+weight_id_err))
                weight_id_down.append((weight_id-weight_id_err))                
   
                    
                if self.globalOptions["year"] == 2016:
                    weight_iso,weight_iso_err = getSFXY(self.muonIsoSF,muon.eta,muon.pt)
                elif self.globalOptions["year"] == 2017 or self.globalOptions["year"] == 2018:
                    weight_iso,weight_iso_err = getSFXY(self.muonIsoSF,muon.pt, abs(muon.eta))

                weight_iso_nominal.append(weight_iso)
                weight_iso_up.append((weight_iso+weight_iso_err))
                weight_iso_down.append((weight_iso-weight_iso_err))

                weight_reco,weight_reco_err = getSFXY(self.recoSFHist,abs(muon.dxy),muon.pt)

                weight_reco_nominal.append(weight_reco)
                weight_reco_up.append((weight_reco+weight_reco_err))
                weight_reco_down.append((weight_reco-weight_reco_err)) 

            weight_id_nominal = np.prod(np.array(weight_id_nominal))
            weight_id_up = np.prod(np.array(weight_id_up))
            weight_id_down = np.prod(np.array(weight_id_down))

            weight_iso_nominal = np.prod(np.array(weight_iso_nominal))
            weight_iso_up = np.prod(np.array(weight_iso_up))
            weight_iso_down = np.prod(np.array(weight_iso_down))

            weight_reco_nominal = np.prod(np.array(weight_reco_nominal))
            weight_reco_up = np.prod(np.array(weight_reco_up))
            weight_reco_down = np.prod(np.array(weight_reco_down))

            self.out.fillBranch(self.outputName+"_weight_id_nominal", weight_id_nominal)
            self.out.fillBranch(self.outputName+"_weight_id_up", weight_id_up)
            self.out.fillBranch(self.outputName+"_weight_id_down", weight_id_down)
            
            self.out.fillBranch(self.outputName+"_weight_iso_nominal", weight_iso_nominal)
            self.out.fillBranch(self.outputName+"_weight_iso_up", weight_iso_up)
            self.out.fillBranch(self.outputName+"_weight_iso_down", weight_iso_down)

            self.out.fillBranch(self.outputName+"_weight_reco_nominal", weight_reco_nominal)
            self.out.fillBranch(self.outputName+"_weight_reco_up", weight_reco_up)
            self.out.fillBranch(self.outputName+"_weight_reco_down", weight_reco_down)

        self.out.fillBranch("n"+self.outputName,len(selectedMuons))
        for variable in self.storeKinematics:
            self.out.fillBranch(self.outputName+"_"+variable,map(lambda muon: getattr(muon,variable),selectedMuons))

        setattr(event,self.outputName,selectedMuons)
        setattr(event,self.outputName+"_unselected",unselectedMuons)

        return True
