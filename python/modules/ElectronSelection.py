import os
import sys
import math
import json
import ROOT
import random
import numpy as np

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module

from utils import getHist, getSFXY, deltaR

def CustomNoConvID(electron):
    if electron.GsfEleSCEtaMultiRangeCut>1 and \
        electron.GsfEleDEtaInSeedCut>1 and \
        electron.GsfEleDPhiInCut>1 and \
        electron.GsfEleFull5x5SigmaIEtaIEtaCut>1 and \
        electron.GsfEleEInverseMinusPInverseCut>1:
        return True
    else:
        return False

def CustomID(electron):
    if CustomNoConvID(electron) and \
        electron.GsfEleConversionVetoCut>1:
        return True
    else:
        return False

def CustomIsoID(electron):
    if electron.GsfEleSCEtaMultiRangeCut>1 and \
        electron.GsfEleDEtaInSeedCut>1 and \
        electron.GsfEleDPhiInCut>1 and \
        electron.GsfEleFull5x5SigmaIEtaIEtaCut>1 and \
        electron.GsfEleEInverseMinusPInverseCut>1 and \
        electron.GsfEleConversionVetoCut>1 and \
        electron.pfRelIso03_all<0.15:
        return True
    else:
        return False       


def LooseNoConvID(electron):
    if electron.MinPtCut >1 and \
        electron.GsfEleSCEtaMultiRangeCut>1 and \
        electron.GsfEleDEtaInSeedCut>1 and \
        electron.GsfEleDPhiInCut>1 and \
        electron.GsfEleFull5x5SigmaIEtaIEtaCut>1 and \
        electron.GsfEleHadronicOverEMEnergyScaledCut>1 and \
        electron.GsfEleEInverseMinusPInverseCut>1 and \
        electron.GsfEleRelPFIsoScaledCut>1 and \
        electron.GsfEleMissingHitsCut:
        return True
    else:
        return False

class ElectronSelection(Module):
    def __init__(
        self,
        inputCollection = lambda event: Collection(event, "Electron"),
        outputName = "tightElectrons",
        electronID = "Iso_WP90",
        electronMinPt = 5.,
        electronMaxEta = 2.4,
        electronIPCuts = False,
        storeKinematics=['pt','eta'],
        storeWeights=False,
        selectLeadingOnly=False,
        globalOptions={"isData":False, "year":2016},
    ):
        IDs = ["Iso_WP80",
               "Iso_WP90",
               "Iso_WPL",
               "noIso_WP80",
               "noIso_WP90",
               "noIso_WPL",
               "None",
               "Custom",
               "CustomIso",
               "Iso",
               "CustomNoConv",
               "LooseNoConvID",
               "Inv"
              ]
        self.inputCollection = inputCollection
        self.outputName = outputName
        self.electronMinPt = electronMinPt
        self.electronMaxEta = electronMaxEta
        self.electronIPCuts = electronIPCuts
        self.storeKinematics = storeKinematics
        self.storeWeights = storeWeights
        self.selectLeadingOnly = selectLeadingOnly
        self.globalOptions = globalOptions
        self.electronIDName = electronID
        if electronID not in IDs:
            print("Undefined electron ID! Choose one of the following")
            print(IDs)
            sys.exit(1)
        elif electronID == "None":
            self.storeWeights = False
            self.electronID = lambda electron: True
        elif electronID == "Custom":
            self.electronID = lambda electron:  CustomID(electron)
        elif electronID == "CustomIso":
            self.storeWeights = False
            self.electronID = lambda electron:  CustomIsoID(electron)
        elif electronID == "Iso":
            self.storeWeights = False
            self.electronID = lambda electron:  \
                                electron.pfRelIso03_all<0.15
        elif electronID == "CustomNoConv":
            self.storeWeights = False
            self.electronID = lambda electron:  CustomNoConvID(electron)
        elif electronID == "LooseNoConv":
            self.storeWeights = False
            self.electronID = lambda electron:  LooseNoConvID(electron)
        elif electronID == "Inv":
            self.electronID = lambda electron: electron.mvaFall17V2Iso_WPL<1 and electron.pfRelIso03_all<0.8
            self.storeWeights = False

        else:
            self.electronID = lambda electron: getattr(electron, "mvaFall17V2"+electronID)


        id_hist_dict = {
                2016: "2016LegacyReReco_ElectronMVAREPLACE_Fall17V2.root",
                2017: "2017_ElectronMVAREPLACE.root",
                2018: "2018_ElectronMVAREPLACE.root"
        }

        self.id_alias_dict = {
            "Iso_WP80" : "80",
            "noIso_WP80" : "80noiso",
            "Iso_WP90" : "90",
            "noIso_WP90" : "90noiso",
        }

        #tight id efficiency
        if not self.globalOptions["isData"] and self.storeWeights:
            if self.electronIDName in self.id_alias_dict.keys():
                self.idHist = getHist(
                    "PhysicsTools/NanoAODTools/data/electron/{}/{}".format(globalOptions["year"], id_hist_dict[globalOptions["year"]].replace("REPLACE", self.id_alias_dict[self.electronIDName])),
                    "EGamma_SF2D"
                )
            elif self.electronIDName == "Custom":
                self.idHist = getHist(
                    "PhysicsTools/NanoAODTools/data/electron/{}/{}".format(globalOptions["year"], "scale_factor2D_geom_trailingLeptons_dxysig_trailingLeptons_pt_"+str(globalOptions["year"])+"_CustomID_syst.root"),
                    "scale_factor2D_geom_trailingLeptons_dxysig_trailingLeptons_pt_"+str(globalOptions["year"])+"_CustomID"
                )
            # elif self.electronIDName == "Custom":
            #     self.idHist = getHist(
            #         "PhysicsTools/NanoAODTools/data/electron/{}".format("scale_factor2D_trailingLeptons_dxysig_trailingLeptons_pt_Run-2.root"),
            #         "scale_factor2D_trailingLeptons_dxysig_trailingLeptons_pt_Run-2"
            #     )
        if not self.globalOptions["isData"]:
            if self.globalOptions["year"] == 2016:
                self.reco_hist_low = getHist(
                    "PhysicsTools/NanoAODTools/data/electron/2016/EGM2D_BtoH_low_RecoSF_Legacy2016.root",
                    "EGamma_SF2D"
                )    
                self.reco_hist_high = getHist(
                    "PhysicsTools/NanoAODTools/data/electron/2016/EGM2D_BtoH_GT20GeV_RecoSF_Legacy2016.root",
                    "EGamma_SF2D"
                )    
            elif self.globalOptions["year"] == 2017:
                self.reco_hist_low = getHist(
                    "PhysicsTools/NanoAODTools/data/electron/2017/egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root",
                    "EGamma_SF2D"
                )    
                self.reco_hist_high = getHist(
                    "PhysicsTools/NanoAODTools/data/electron/2017/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root",
                    "EGamma_SF2D"
                )    
            elif self.globalOptions["year"] == 2018:
                self.reco_hist_low = getHist(
                    "PhysicsTools/NanoAODTools/data/electron/2018/egammaEffi.txt_EGM2D_updatedAll.root",
                    "EGamma_SF2D"
                )   
                self.reco_hist_high = getHist(
                    "PhysicsTools/NanoAODTools/data/electron/2018/egammaEffi.txt_EGM2D_updatedAll.root",
                    "EGamma_SF2D"
                )                     
            else:
                print("Invalid year")
                sys.exit(1)

    def beginJob(self):
        pass

    def endJob(self):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        self.out.branch("n"+self.outputName, "I")
        if not self.globalOptions["isData"]:
            self.out.branch(self.outputName+"_weight_reco_nominal","F")
            self.out.branch(self.outputName+"_weight_reco_up","F")
            self.out.branch(self.outputName+"_weight_reco_down","F")

        if not self.globalOptions["isData"] and self.storeWeights:
            self.out.branch(self.outputName+"_weight_id_nominal","F")
            self.out.branch(self.outputName+"_weight_id_up","F")
            self.out.branch(self.outputName+"_weight_id_down","F")

        for variable in self.storeKinematics:
            self.out.branch(self.outputName+"_"+variable,"F",lenVar="n"+self.outputName)


    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def analyze(self, event):
        """process event, return True (go to next module) or False (fail, go to next event)"""
        electrons = self.inputCollection(event)
        muons = Collection(event, "Muon")


        selectedElectrons = []
        unselectedElectrons = []

        for electron in electrons:
            bitmap = electron.vidNestedWPBitmap
            # decision for each cut represented by 3 bits (0:fail, 1:veto, 2:loose, 3:medium, 4:tight)
            # Electron_vidNestedWPBitmap
            cuts = np.empty(10)

            for i in range(10):
                cuts[i] = (bitmap >> i*3) & 0x7

            electron.vetoId=electron.cutBased > 0
            electron.looseId=electron.cutBased > 1
            electron.mediumId=electron.cutBased> 2
            electron.tightId=electron.cutBased> 3

            electron.MinPtCut = cuts[0]
            electron.GsfEleSCEtaMultiRangeCut = cuts[1]
            electron.GsfEleDEtaInSeedCut = cuts[2]
            electron.GsfEleDPhiInCut = cuts[3]
            electron.GsfEleFull5x5SigmaIEtaIEtaCut = cuts[4]
            electron.GsfEleHadronicOverEMEnergyScaledCut = cuts[5]
            electron.GsfEleEInverseMinusPInverseCut = cuts[6]
            electron.GsfEleRelPFIsoScaledCut = cuts[7]
            electron.GsfEleConversionVetoCut = cuts[8]
            electron.GsfEleMissingHitsCut = cuts[9]

            if CustomID(electron):
                setattr(electron, "isCustomID", 1)
            else:
                setattr(electron, "isCustomID", 0)

            if CustomNoConvID(electron):
                setattr(electron, "isCustomNoConvID", 1)
            else:
                setattr(electron, "isCustomNoConvID", 0)

            if LooseNoConvID(electron):
                setattr(electron, "isLooseNoConvID", 1)
            else:
                setattr(electron, "isLooseNoConvID", 0)

            if electron.pt>self.electronMinPt and math.fabs(electron.eta)<self.electronMaxEta \
                and self.electronID(electron):
                # https://twiki.cern.ch/twiki/bin/view/CMS/CutBasedElectronIdentificationRun2
                if self.electronIPCuts:
                    if math.fabs(electron.eta) < 1.479:
                        if abs(electron.dxy) > 0.05 or abs(electron.dz) > 0.10:
                            unselectedElectrons.append(electron)
                            continue
                    else:
                        if abs(electron.dxy) > 0.10 or abs(electron.dz) > 0.20:
                            unselectedElectrons.append(electron)
                            continue

                if muons is not None and len(muons) > 0:
                    mindr = min(map(lambda muon: deltaR(muon, electron), muons))
                    if mindr < 0.05:
                        unselectedElectrons.append(electron)
                        continue

                selectedElectrons.append(electron)
            else:
                unselectedElectrons.append(electron)

        if len(selectedElectrons) > 0 and self.selectLeadingOnly:
            unselectedElectrons.extend(selectedElectrons[1:])
            selectedElectrons = [selectedElectrons[0]]


        if not self.globalOptions["isData"]:
            
            weight_reco_nominal = []
            weight_reco_up = []
            weight_reco_down = []

            for electron in selectedElectrons:
                if electron.pt > 20.:
                    reco_sf_nominal, reco_sf_err = getSFXY(self.reco_hist_high,electron.eta,electron.pt)
                else:
                    reco_sf_nominal, reco_sf_err = getSFXY(self.reco_hist_low,electron.eta,electron.pt)

                weight_reco_nominal.append(reco_sf_nominal)
                weight_reco_up.append(reco_sf_nominal+reco_sf_err)
                weight_reco_down.append(reco_sf_nominal-reco_sf_err)

            weight_reco_nominal = np.prod(np.array(weight_reco_nominal))
            weight_reco_up = np.prod(np.array(weight_reco_up))
            weight_reco_down = np.prod(np.array(weight_reco_down))

            self.out.fillBranch(self.outputName+"_weight_reco_nominal", weight_reco_nominal)
            self.out.fillBranch(self.outputName+"_weight_reco_up", weight_reco_up)
            self.out.fillBranch(self.outputName+"_weight_reco_down", weight_reco_down)
        
        if not self.globalOptions["isData"] and self.storeWeights:   
            
            weight_id_nominal = []
            weight_id_up = []
            weight_id_down = [] 

            for electron in selectedElectrons:

                weight_id = 0
                weight_id_err = 0

                if self.electronIDName in self.id_alias_dict.keys():
                    weight_id,weight_id_err = getSFXY(self.idHist,electron.eta,electron.pt)
                elif self.electronIDName == "Custom":
                    weight_id,weight_id_err = getSFXY(self.idHist,abs(electron.dxy)/(1e-5+abs(electron.dxyErr)),electron.pt)
                else:
                    print("Undefined ID: ", self.electronIDName)

                weight_id_nominal.append(weight_id)
                weight_id_up.append((weight_id+weight_id_err))
                weight_id_down.append((weight_id-weight_id_err))

            weight_id_nominal = np.prod(np.array(weight_id_nominal))
            weight_id_up = np.prod(np.array(weight_id_up))
            weight_id_down = np.prod(np.array(weight_id_down))

            self.out.fillBranch(self.outputName+"_weight_id_nominal", weight_id_nominal)
            self.out.fillBranch(self.outputName+"_weight_id_up", weight_id_up)
            self.out.fillBranch(self.outputName+"_weight_id_down", weight_id_down)

        self.out.fillBranch("n"+self.outputName,len(selectedElectrons))
        for variable in self.storeKinematics:
            self.out.fillBranch(self.outputName+"_"+variable,map(lambda electron: getattr(electron,variable), selectedElectrons))

        setattr(event,self.outputName,selectedElectrons)
        setattr(event,self.outputName+"_unselected",unselectedElectrons)

        return True
