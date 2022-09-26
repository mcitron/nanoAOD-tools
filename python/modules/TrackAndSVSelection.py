from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
import numpy as np
import math
import utils

class TrackAndSVSelection(Module):
    def __init__(
        self,
        jetCollection=lambda event: Collection(event, "Jet"),
        svType="adapted",
        cpfCollection=lambda event: Collection(event, "cpf"),
        lepton2Object = lambda event: None,
        outputName="hnlJet_track_weight",
        globalOptions={"isData":False, "isSignal":False, "year": 2016},
        storeWeights="False",

    ):
        self.jetCollection = jetCollection
        if svType not in ["regular", "adapted"]:
            raise ValueError("Wrong sv type")
        self.svType = svType
        self.cpfCollection = cpfCollection
        self.lepton2Object = lepton2Object
        self.outputName = outputName
        self.globalOptions = globalOptions
        if self.globalOptions["year"]== 2016 :   
           self.sf = utils.getHistCanvas("PhysicsTools/NanoAODTools/data/track/track_sf_2016.root", "c1" , "ratio")

        if self.globalOptions["year"]== 2017 :   
           self.sf = utils.getHistCanvas("PhysicsTools/NanoAODTools/data/track/track_sf_2017.root", "c1" , "ratio")

        if self.globalOptions["year"]== 2018 :   
           self.sf = utils.getHistCanvas("PhysicsTools/NanoAODTools/data/track/track_sf_2018.root", "c1" , "ratio")
          
      
        self.storeWeights = storeWeights

    def beginJob(self):
        pass
    def endJob(self):
        pass
        
    def endFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        pass

    def beginFile(self, inputFile, outputFile, inputTree, wrappedOutputTree):
        self.out = wrappedOutputTree
        
        if self.svType is not None:
            self.out.branch(self.outputName+"_"+self.svType+"_muon", "I")
            self.out.branch(self.outputName+"_"+self.svType+"_muon_dxy", "F")
            self.out.branch(self.outputName+"_"+self.svType+"_muon_pt", "F")
            self.out.branch(self.outputName+"_"+self.svType+"_muon_dxysig", "F")
            
            self.out.branch(self.outputName+"_"+self.svType+"_electron", "I")
            self.out.branch(self.outputName+"_"+self.svType+"_electron_pt", "F")
            self.out.branch(self.outputName+"_"+self.svType+"_electron_dxy", "F")
            self.out.branch(self.outputName+"_"+self.svType+"_electron_dxysig", "F")
        


            self.out.branch("n"+self.outputName+"_"+self.svType, "I")
            self.out.branch(self.outputName+"_"+self.svType+"_pt", "F", lenVar="nhnlJet_svMatchedTracks_"+self.svType)
            self.out.branch(self.outputName+"_"+self.svType+"_dxy", "F", lenVar="nhnlJet_svMatchedTracks_"+self.svType+"_"+self.outputName)
            self.out.branch(self.outputName+"_"+self.svType+"_dxysig", "F", lenVar="nhnlJet_svMatchedTracks_"+self.svType+"_"+self.outputName)
      
        if self.storeWeights:        
            self.out.branch(self.outputName+"_nominal", "F")
            self.out.branch(self.outputName+"_up", "F")
            self.out.branch(self.outputName+"_down", "F")
            
            self.out.branch("lepton2_track_nominal", "F")
            self.out.branch("lepton2_track_up", "F")
            self.out.branch("lepton2_track_down", "F")

    def analyze(self, event):
          
        jets = self.jetCollection(event)
        cpfs = self.cpfCollection(event)
        lepton2 = self.lepton2Object(event)


        # Iterate over all jets and find the matching tracks
        matchingVariable = "matchedSV_adapted" if self.svType == "adapted" else "matchedSV"
        cpfsMatchedToJetAndSV = []
        cpfMuon = 0
        cpfMuonpt = 0
        cpfMuondxy = 0
        cpfMuondxysig = 0
        cpfElectron = 0
        cpfElectronpt = 0
        cpfElectrondxy = 0
        cpfElectrondxysig = 0
        
        if len(jets) == 0:
            averageWeightUp = 1.
            ntracks = 0
            trackpt = 0
            trackdxy = 0
            trackdxysig = 0
        else:
            jet = jets[0]
            ntracks = len(cpfs)
            matchedCpfs = [cpf for cpf in cpfs if cpf.jetIdx == jet._index and getattr(cpf, matchingVariable, True)]
            if len(matchedCpfs) == 0:
                ntracks = 0
                trackpt = 0
                trackdxy = 0
                trackdxysig = 0
            else :
               trackpt = matchedCpfs[0].ptrel*jet.ptRaw
               trackdxy = matchedCpfs[0].trackSip2dVal
               trackdxysig = matchedCpfs[0].trackSip2dSig
            
            for cpf in matchedCpfs:
                cpf.pt = jet.ptRaw*cpf.ptrel
                if cpf.matchedMuon == True and cpfMuon == 0:
                  cpfMuon = 1
                  cpfMuonpt = cpf.pt
                  cpfMuondxy= cpf.trackSip2dVal
                  cpfMuondxysig = cpf.trackSip2dSig
                elif cpf.matchedElectron == True and cpfElectron == 0 :
                   cpfElectron = 1
                   cpfElectronpt = cpf.pt
                   cpfElectrondxy = cpf.trackSip2dVal
                   cpfElectrondxysig = cpf.trackSip2dSig
                  
            cpfsMatchedToJetAndSV.extend(matchedCpfs)
            self.out.fillBranch(self.outputName+"_"+self.svType+"_muon", cpfMuon)
            self.out.fillBranch(self.outputName+"_"+self.svType+"_muon_pt", cpfMuonpt)
            self.out.fillBranch(self.outputName+"_"+self.svType+"_muon_dxy", cpfMuondxy)
            self.out.fillBranch(self.outputName+"_"+self.svType+"_muon_dxysig", cpfMuondxysig)
            self.out.fillBranch(self.outputName+"_"+self.svType+"_electron", cpfElectron)
            self.out.fillBranch(self.outputName+"_"+self.svType+"_electron_pt", cpfElectronpt)
            self.out.fillBranch(self.outputName+"_"+self.svType+"_electron_dxy", cpfElectrondxy)
            self.out.fillBranch(self.outputName+"_"+self.svType+"_electron_dxysig", cpfElectrondxysig)
            

            
            self.out.fillBranch("n"+self.outputName+"_"+self.svType, len(cpfsMatchedToJetAndSV))
            self.out.fillBranch(self.outputName+"_"+self.svType+"_pt", map(lambda cpf: cpf.pt, cpfsMatchedToJetAndSV))
            self.out.fillBranch(self.outputName+"_"+self.svType+"_dxy", map(lambda cpf: cpf.trackSip2dVal, cpfsMatchedToJetAndSV))
            self.out.fillBranch(self.outputName+"_"+self.svType+"_dxysig", map(lambda cpf: cpf.trackSip2dSig, cpfsMatchedToJetAndSV))
            
            if self.storeWeights:
                weightedSFSum = 0. #sum of weights x SF
                weightedSFErrorSum2 = 0. #sum of weights^2 x SFerr ^ 2
                weightSum = 0. #sum of weights
                
                matchedCpfs = [cpf for cpf in cpfs if cpf.jetIdx == jet._index]
                matchedCpfs = sorted(matchedCpfs,key=lambda x: math.fabs(x.trackSip2dVal),reverse=True)
                
 
                if len(matchedCpfs) > 0:

                    matchedCpfs = matchedCpfs[:3]
                    
                    for i, cpf in enumerate(matchedCpfs) : 
                        dxy = max(self.sf.GetXaxis().GetXmin()*1.0001, min(self.sf.GetXaxis().GetXmax()*0.9999, math.fabs(cpf.trackSip2dVal)))
                        binNumber = self.sf.FindBin(dxy)

                        scaleFactor = self.sf.GetBinContent(binNumber)
                        scaleFactorErr = self.sf.GetBinError(binNumber)
                        
                        #skip if scaleFactor is unreasonably small
                        if scaleFactor<0.1:
                            scaleFactor = 1.
                            scaleFactorErr = 0.
                        
                        
                        weight = math.fabs(cpf.ptrel)+1e-3 #add slight bias to protect against very small weights
                        
                        weightSum += weight
                        weightedSFSum += weight*scaleFactor
                        weightedSFErrorSum2 += (weight**2)*(scaleFactorErr**2)

                        
                    weightedSFSum = weightedSFSum/weightSum
                    weightedSFError = math.sqrt(
                        weightedSFErrorSum2/weightSum**2
                    )
                    
                    
                    #add half the uncertainty to unity if SF uncertainty very small
                    if weightedSFError<(0.5*math.fabs(1.-weightedSFSum)):
                        weightedSFError = math.sqrt(weightedSFError**2+(0.5*(1.-weightedSFSum))**2)
                    
                    
                else:
                    weightedSFSum = 1.
                    weightedSFError = 0.

                
                self.out.fillBranch(self.outputName+"_nominal",weightedSFSum )
                self.out.fillBranch(self.outputName+"_up", weightedSFSum+weightedSFError)
                self.out.fillBranch(self.outputName+"_down", weightedSFSum-weightedSFError)
                
                resolvedLeptonWeight = 1.
                resolvedLeptonWeightErr = 0.
                if lepton2 and utils.deltaPhi(lepton2,jet)>0.4:
                    dxy = max(self.sf.GetXaxis().GetXmin()*1.0001, min(self.sf.GetXaxis().GetXmax()*0.9999, math.fabs(lepton2.dxy)))
                    binNumber = self.sf.FindBin(dxy)
                    resolvedLeptonWeight = self.sf.GetBinContent(binNumber)
                    resolvedLeptonWeightErr = self.sf.GetBinError(binNumber)
                    if resolvedLeptonWeight<0.1:
                        resolvedLeptonWeight = 1.
                        resolvedLeptonWeightErr = 0.
                    if resolvedLeptonWeightErr<(0.5*math.fabs(1.-resolvedLeptonWeight)):
                        resolvedLeptonWeightErr = math.sqrt(resolvedLeptonWeightErr**2+(0.5*(1.-resolvedLeptonWeight))**2)
                    
                
                self.out.fillBranch("lepton2_track_nominal", resolvedLeptonWeight)
                self.out.fillBranch("lepton2_track_up", resolvedLeptonWeight+resolvedLeptonWeightErr)
                self.out.fillBranch("lepton2_track_down", resolvedLeptonWeight-resolvedLeptonWeightErr)

        return True
