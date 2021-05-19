import sys, ROOT
from RpfHandler import RpfHandler
from header import openJSON, projInfoLookup

ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(1)

def GetMCratio(projDir, region):
    histfile = ROOT.TFile.Open('%s/%s/organized_hists.root'%(projDir,region),'READ')
    p = histfile.Get('qcdmc_pass_FULL_%s'%(region))
    f = histfile.Get('qcdmc_fail_FULL_%s'%(region))
    ratio = p.Clone('qcdmc_ratio_FULL_%s'%(region))
    ratio.Divide(f)
    ratio.SetDirectory(0)
    return ratio

def FuncFill(func):
    for xbin in range(1,func.dummy_TH2.GetNbinsX()+1):
        for ybin in range(1,func.dummy_TH2.GetNbinsY()+1):
            func.Eval(xbin,ybin)
    return func

def FuncToHist(func):
    out = func.dummy_TH2.Clone()
    out.Reset()
    for xbin in range(1,out.GetNbinsX()+1):
        for ybin in range(1,out.GetNbinsY()+1):
            out.SetBinContent(xbin,ybin,func.getFuncBinVal(None,xbin,ybin))
    return out

# Naming information
projDir = sys.argv[1]
if projDir.split('/')[-1] == '': card_tag = projDir.split('/')[-2]
else: card_tag = projDir.split('/')[-1]
projInfo = projInfoLookup(projDir,card_tag)

c = ROOT.TCanvas('c','',900,700)
# Loop over all regions/config folders
for region in projInfo.keys():
    rratio = projInfo[region]['rpf'] # Get rratio RpfHandler
    fd_file = ROOT.TFile.Open('%s/fitDiagnostics.root'%projDir) # Get post-fit parameter values
    fit_result = fd_file.Get('fit_s')
    rratio_RRVs = rratio.getFuncVarNames()

    # Set the post-fit parameter values
    for rrv_name in rratio_RRVs:
        postfit_val = fit_result.floatParsFinal().find(rrv_name).getValV()
        print ('%s/%s setting %s to %.2f'%(projDir,region,rrv_name,postfit_val))
        rratio.setFuncParam(rrv_name, postfit_val)
    # Fill all of the "bins" of the RpfHandler
    rratio = FuncFill(rratio)

    # Get the MC shape
    mc_rpf = GetMCratio(projDir, region)

    # Create total TF
    rpf = mc_rpf.Clone('%s_rpf'%region)
    rpf.Multiply(FuncToHist(rratio))

    c.cd()
    rpf.GetXaxis().SetTitle(projInfo[region]['xVarTitle'])
    rpf.GetYaxis().SetTitle(projInfo[region]['yVarTitle'])
    rpf.GetZaxis().SetTitle('Transfer function value')
    rpf.SetTitle('Transfer function - %s'%region)
    c.SetLeftMargin(0.15)
    rpf.GetXaxis().SetTitleSize(0.03)
    rpf.GetYaxis().SetTitleSize(0.03)
    rpf.GetZaxis().SetTitleSize(0.03)
    rpf.GetXaxis().SetTitleOffset(1.8)
    rpf.GetYaxis().SetTitleOffset(2.3)
    rpf.GetZaxis().SetTitleOffset(1.7)
    rpf.GetXaxis().SetLabelSize(0.03)
    rpf.GetYaxis().SetLabelSize(0.03)
    rpf.GetZaxis().SetLabelSize(0.03)
    rpf.Draw('surf')
    c.Print('%s/%s/transferFunc_surf.pdf'%(projDir,region),'pdf')
    
