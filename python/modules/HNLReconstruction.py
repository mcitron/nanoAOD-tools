import os
import sys
import math
import json
import ROOT
import random

from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from utils import deltaR, deltaPhi


class HNLReconstruction(Module):
    def __init__(
        self,
        lepton1Object = lambda event: event.leadingLeptons[0],
        lepton2Object = None,
        jetCollection=lambda event: Collection(event, "Jet"),
        outputName="nominal",
        globalOptions={"isData":False, "isSignal":False},
        jetClasses=["isPrompt_MU", "isPrompt_E", "isPrompt_PHOTON", "isPrompt_TAU", "isUDS", "isG", "isB", "isC", "isPU"],

    ):
        self.lepton1Object = lepton1Object
        self.lepton2Object = lepton2Object
        self.jetCollection = jetCollection
        self.jetClasses=jetClasses

        self.outputName = outputName
        self.globalOptions = globalOptions

    def beginJob(self):
        pass

    def endJob(self):
        pass
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree

        self.out.branch("hnlJet_"+self.outputName+"_pt", "F")
        self.out.branch("hnlJet_"+self.outputName+"_ptsub", "F")
        self.out.branch("hnlJet_"+self.outputName+"_ptraw", "F")
        self.out.branch("hnlJet_"+self.outputName+"_ptrawsub", "F")
        self.out.branch("hnlJet_"+self.outputName+"_ptorig", "F")
        self.out.branch("hnlJet_"+self.outputName+"_ptorigsub", "F")
        self.out.branch("hnlJet_"+self.outputName+"_eta", "F")
        self.out.branch("hnlJet_"+self.outputName+"_phi", "F")
        self.out.branch("hnlJet_"+self.outputName+"_ncpf", "I")
        self.out.branch("hnlJet_"+self.outputName+"_nmu", "I")
        self.out.branch("hnlJet_"+self.outputName+"_ne", "I")


        if self.lepton2Object==None:
            self.out.branch(self.outputName+"_m_l1j", "F")
            self.out.branch(self.outputName+"_dPt_l1j", "F")
            self.out.branch(self.outputName+"_dPhi_l1j", "F")
            self.out.branch(self.outputName+"_dR_l1j", "F")
            self.out.branch(self.outputName+"_dEta_l1j", "F")
        else:
            self.out.branch(self.outputName+"_m_llj", "F")
            self.out.branch(self.outputName+"_dPt_llj", "F")
            self.out.branch(self.outputName+"_dPhi_l1j", "F")
            self.out.branch(self.outputName+"_dEta_l1j", "F")
            self.out.branch(self.outputName+"_dR_l2j", "F")

        if self.globalOptions["isSignal"]:
            self.out.branch("hnlJet_"+self.outputName+"_isTrueQ", "I")
            self.out.branch("hnlJet_"+self.outputName+"_isTrueQE", "I")
            self.out.branch("hnlJet_"+self.outputName+"_isTrueQMU", "I")
            self.out.branch("hnlJet_"+self.outputName+"_isTrueQTAU", "I")
            self.out.branch("hnlJet_"+self.outputName+"_trueLxy", "F")
            
            #number of jets in event that are LLP but are not selected
            self.out.branch(self.outputName+"_nTrueMissed", "I")
        # if not self.globalOptions["isData"]:
        #     for jetClass in self.jetClasses:
        #         self.out.branch("hnlJet_"+self.outputName+"_"+jetClass, "I")


    def fillTruthInfo(self,hnlJet,otherJets):
        if hnlJet!=None:
            self.out.fillBranch("hnlJet_"+self.outputName+"_isTrueQ", hnlJet.isLLP_Q)
            self.out.fillBranch("hnlJet_"+self.outputName+"_isTrueQE", hnlJet.isLLP_QE)
            self.out.fillBranch("hnlJet_"+self.outputName+"_isTrueQMU", hnlJet.isLLP_QMU)
            self.out.fillBranch("hnlJet_"+self.outputName+"_isTrueQTAU", hnlJet.isLLP_QTAU)
            self.out.fillBranch("hnlJet_"+self.outputName+"_trueLxy", hnlJet.displacement_xy)
        else:
            self.out.fillBranch("hnlJet_"+self.outputName+"_isTrueQ", -1)
            self.out.fillBranch("hnlJet_"+self.outputName+"_isTrueQE", -1)
            self.out.fillBranch("hnlJet_"+self.outputName+"_isTrueQMU", -1)
            self.out.fillBranch("hnlJet_"+self.outputName+"_isTrueQTAU", -1)
            self.out.fillBranch("hnlJet_"+self.outputName+"_trueLxy", -10)

     
        if len(otherJets)==0:
            self.out.fillBranch(self.outputName+"_nTrueMissed", 0)
        else:
            missed = sum(map(lambda x: x.isLLP_Q+x.isLLP_QE+x.isLLP_QMU+x.isLLP_QTAU,otherJets))
            self.out.fillBranch(self.outputName+"_nTrueMissed", missed)
            
            
    def fillHNLJetInfo(self,hnlJet):
        if hnlJet!=None:
            self.out.fillBranch("hnlJet_"+self.outputName+"_pt", hnlJet.pt)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptsub", hnlJet.p4Subtracted.Pt())
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptraw", hnlJet.ptRaw)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptrawsub", hnlJet.ptRawSubtracted)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptorig", hnlJet.p4Original.Pt())
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptorigsub", hnlJet.p4OriginalSubtracted.Pt())
            self.out.fillBranch("hnlJet_"+self.outputName+"_eta", hnlJet.eta)
            self.out.fillBranch("hnlJet_"+self.outputName+"_phi", hnlJet.phi)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ncpf", hnlJet.numberCpf)
            self.out.fillBranch("hnlJet_"+self.outputName+"_nmu", hnlJet.numberMuon)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ne", hnlJet.numberElectron)

        else:
            self.out.fillBranch("hnlJet_"+self.outputName+"_pt", 0)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptsub", 0)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptraw", 0)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptrawsub", 0)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptorig", 0)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ptorigsub", 0)
            self.out.fillBranch("hnlJet_"+self.outputName+"_eta", 0)
            self.out.fillBranch("hnlJet_"+self.outputName+"_phi", 0)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ncpf", -1)
            self.out.fillBranch("hnlJet_"+self.outputName+"_nmu", -1)
            self.out.fillBranch("hnlJet_"+self.outputName+"_ne", -1)            

    def analyze(self, event):

        lepton1 = self.lepton1Object(event)
        lepton2 = None if self.lepton2Object==None else self.lepton2Object(event)
          
        jets = self.jetCollection(event)

        if lepton2==None:
            if len(jets) > 0:
                #take jet opposite of l1 in transverse plane
                sortedJets = sorted(jets, key=lambda jet: math.fabs(deltaPhi(jet, lepton1)), reverse=True)
                hnlJet = sortedJets[0]
                self.fillHNLJetInfo(hnlJet)
                
                self.out.fillBranch(self.outputName+"_m_l1j", (lepton1.p4()+hnlJet.p4Subtracted).M())
                self.out.fillBranch(self.outputName+"_dPt_l1j", (lepton1.p4()-hnlJet.p4Subtracted).Pt())
                self.out.fillBranch(self.outputName+"_dPhi_l1j", math.fabs(deltaPhi(lepton1, hnlJet)))
                self.out.fillBranch(self.outputName+"_dR_l1j", deltaR(lepton1, hnlJet))
                self.out.fillBranch(self.outputName+"_dEta_l1j", math.fabs(lepton1.eta-hnlJet.eta))
                setattr(event, "hnlJets_"+self.outputName, [hnlJet])
                
                if self.globalOptions["isSignal"]:
                    self.fillTruthInfo(hnlJet,sortedJets[1:])

                # if not self.globalOptions["isData"]:
                #     for jetClass in self.jetClasses:
                #         self.out.fillBranch("hnlJet_"+self.outputName+"_"+jetClass, getattr(hnlJet, jetClass))  
  
            else:
                self.fillHNLJetInfo(None)
            
                self.out.fillBranch(self.outputName+"_m_l1j", 0)
                self.out.fillBranch(self.outputName+"_dPt_l1j", 0)
                self.out.fillBranch(self.outputName+"_dPhi_l1j", 0)
                self.out.fillBranch(self.outputName+"_dR_l1j", 0)
                self.out.fillBranch(self.outputName+"_dEta_l1j", 0)
                setattr(event, "hnlJets_"+self.outputName, [])
                
                if self.globalOptions["isSignal"]:
                    self.fillTruthInfo(None,[])

                          
                # if not self.globalOptions["isData"]:
                #     for jetClass in self.jetClasses:
                #         self.out.fillBranch("hnlJet_"+self.outputName+"_"+jetClass, -1)  
        else:
            if len(jets) > 0:
                #take jet closest to l2
                sortedJets = sorted(jets, key=lambda jet: deltaR(jet, lepton2), reverse=False)
                hnlJet = sortedJets[0]
                self.fillHNLJetInfo(hnlJet)
                
                self.out.fillBranch(self.outputName+"_m_llj", (lepton1.p4()+lepton2.p4()+hnlJet.p4Subtracted).M())
                self.out.fillBranch(self.outputName+"_dPt_llj", (lepton1.p4()-lepton2.p4()-hnlJet.p4Subtracted).Pt())
                self.out.fillBranch(self.outputName+"_dPhi_l1j", math.fabs(deltaPhi(lepton1,hnlJet)))
                self.out.fillBranch(self.outputName+"_dEta_l1j", math.fabs(lepton1.eta-hnlJet.eta))
                self.out.fillBranch(self.outputName+"_dR_l2j", deltaR(lepton2,hnlJet))
                setattr(event, "hnlJets_"+self.outputName, [hnlJet])
                
                if self.globalOptions["isSignal"]:
                    self.fillTruthInfo(hnlJet,sortedJets[1:])
                          
                # if not self.globalOptions["isData"]:
                #     for jetClass in self.jetClasses:
                #         self.out.fillBranch("hnlJet_"+self.outputName+"_"+jetClass, getattr(hnlJet, jetClass))  
                    
            else:
                self.fillHNLJetInfo(None)
            
                self.out.fillBranch(self.outputName+"_m_llj", 0)
                self.out.fillBranch(self.outputName+"_dPt_llj", 0)
                self.out.fillBranch(self.outputName+"_dPhi_l1j", 0)
                self.out.fillBranch(self.outputName+"_dEta_l1j", 0)
                self.out.fillBranch(self.outputName+"_dR_l2j", 0)
                setattr(event, "hnlJets_"+self.outputName, [])
                
                if self.globalOptions["isSignal"]:
                    self.fillTruthInfo(None,[])
            
                # if not self.globalOptions["isData"]:
                #     for jetClass in self.jetClasses:
                #         self.out.fillBranch("hnlJet_"+self.outputName+"_"+jetClass, -1)  
        
        return True
