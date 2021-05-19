import ROOT, sys

f1 = ROOT.TFile.Open(sys.argv[1])
f2 = ROOT.TFile.Open(sys.argv[2])

vals1 = {}
vals2 = {}

for f in [f1,f2]:

    lim = f.Get('limit')

    for i in range(lim.GetEntries()):
        lim.GetEntry(i)
        #print '%.2f %%: %.2f'%(lim.quantileExpected,lim.limit)
        if f == f1: vals1[lim.quantileExpected] = lim.limit
        if f == f2: vals2[lim.quantileExpected] = lim.limit

for k in vals1.keys():
    print '%.2f %%: %.2f'%(k, (vals2[k]-vals1[k])/vals1[k])
