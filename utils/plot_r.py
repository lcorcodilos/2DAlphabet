import ROOT, sys, array

# First sys arg is file name

f = ROOT.TFile(sys.argv[0])
lim = f.Get('limit')
r = []
r_errLow = []
r_errHigh = []

for i in range(1,lim.GetEntries()+1):
    lim.GetEntry(i)
    r.append(lim.r)
    r_errLow.append(lim.rLoErr)
    r_errHigh.append(lim.rHiErr)

r_array = array.array('d',r)
r_errLow_array = array.array('d',r_errLow)
r_errHigh_array = array.array('d',r_errHigh)
x = array.array('i',range(1,lim.GetEntries()+1))
x_err = array.array('d',[0.5 for i in range(1,lim.GetEntries()+1)])

g = ROOT.TGraphAsymmErrors(lim.GetEntries(),x,r,x_err,x_err,r_errLow_array,r_errHigh_array)
g.Draw()
raw_input('')