import ROOT
from ROOT import TFile, RooFit

f = TFile.Open('higgsCombineTest.GenerateOnly.mH120.123456.root')
toy_roodataset = f.Get("toys/toy_1")
axis_vars = ROOT.RooArgList(toy_roodataset.get(0))

out = TFile.Open('test_rds_draw.root','recreate')
for i in range(axis_vars.getSize()):
    v = axis_vars[i]
    if not isinstance(v,ROOT.RooRealVar): continue
    if "jetmass":
        v2_name =  v.GetName().replace("jetmass","resmass")
        for R in ["_LOW","_SIG","_HIGH"]:
            v2_name = v2_name.replace(R,"")
        print v2_name
        v2 = axis_vars.find(v2_name)
    else:
        continue

    v2.Print()
    hist = ROOT.RooAbsData.createHistogram(toy_roodataset,v.GetName(),v
    )
    hist.Sumw2(False)
    hist.SetBinErrorOption(ROOT.TH1.kPoisson)
    hist.Write()

out.Close()
