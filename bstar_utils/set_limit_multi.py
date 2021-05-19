from optparse import OptionParser
import subprocess
import array, math
from  array import array

import ROOT
from ROOT import *

import header
from header import WaitForJobs, make_smooth_graph, Inter
import tdrstyle, CMS_lumi

gStyle.SetOptStat(0)
gROOT.SetBatch(kTRUE)

parser = OptionParser()

# parser.add_option('-t', '--tag', metavar='FILE', type='string', action='store',
#                 default   =   'dataBsOff',
#                 dest      =   'tag',
#                 help      =   'Tag ran over')
parser.add_option('-s', '--signals', metavar='FILE', type='string', action='store',
                default   =   'bstar_signalsLH.txt',
                dest      =   'signals',
                help      =   'Text file containing the signal names and their corresponding cross sections')
parser.add_option('-P', '--plotOnly', action="store_true",
                default   =   False,
                dest      =   'plotOnly',
                help      =   'Only plots if True')
parser.add_option('--unblind', action="store_false",
                default   =   True,
                dest      =   'blind',
                help      =   'Only plot observed limit if false')
parser.add_option('--drawIntersection', action="store_true",
                default   =   False,
                dest      =   'drawIntersection',
                help      =   'Draw intersection values')
parser.add_option('-l', '--lumi', metavar='F', type='string', action='store',
                default       =       '137.44',
                dest          =       'lumi',
                help          =       'Luminosity option')
parser.add_option('-m', '--mod', metavar='F', type='string', action='store',
                default       =       '',
                dest          =       'mod',
                help          =       'Modification to limit title on y-axis. For example, different handedness of the signal')

(options, args) = parser.parse_args()

multi_sig_files = options.signals.split(',')
cstr = options.mod

expected_graphs = {}

for signal_file_name in multi_sig_files:
    # Open signal file
    signal_file = open(signal_file_name,'r')
    # Read in names of project spaces as a list of strings and strip whitespace
    signal_names = signal_file.readline().split(',')
    signal_names = [n.strip() for n in signal_names]
    # Read in mass as a list of strings, strip whitespace, and convert to ints
    signal_mass = signal_file.readline().split(',')
    signal_mass = [float(m.strip())/1000 for m in signal_mass]
    # Read in xsecs as a list of strings, strip whitespace, and convert to floats
    theory_xsecs = signal_file.readline().split(',')
    theory_xsecs = [float(x.strip()) for x in theory_xsecs]
    # Read in xsecs that samples were normalized to
    signal_xsecs = signal_file.readline().split(',')

    if 'tprime' in signal_file_name.split('/')[-1]:
        signal_xsecs = [float(x.strip()) for x in signal_xsecs]
    elif 'bprime' in signal_file_name.split('/')[-1]:
        signal_xsecs = [float(x.strip()) for x in signal_xsecs]
    else:
        signal_xsecs = [float(x.strip()) for x in signal_xsecs]

    # Get theory PDF variations - BSTAR SPECIFIC
    bs_path = '/uscms_data/d3/lcorcodi/BStar13TeV/CMSSW_10_2_0/src/BStar13TeV/SFs/'

    if 'LH' in signal_file_name.split('/')[-1]:
        hand = 'LH'
    elif 'RH' in signal_file_name.split('/')[-1]:
        hand = 'RH'
    elif 'VL' in signal_file_name.split('/')[-1]:
        hand = 'VL'

    if 'bprimeb' in signal_file_name.split('/')[-1]:
        label = "B'(+b)"
    elif 'bprime' in signal_file_name.split('/')[-1]:
        label = "B'(+t)"
    #     theory_var_file = TFile.Open(bs_path+'pdf_norm_uncertainties_TBprime.root')
    #     sigma_max = 1
    #     sigma_min = 1e-5
    #     mass_min = 1.4
    #     mass_max = 1.8
    elif 'tprime' in signal_file_name.split('/')[-1]:
        label = "T'"
    #     theory_var_file = TFile.Open(bs_path+'pdf_norm_uncertainties_TBprime.root')
    #     sigma_max = 10
    #     sigma_min = 5e-3
    #     mass_min = 1.4#0.59
    #     mass_max = 1.8#1.81
    elif 'bstar' in signal_file_name.split('/')[-1]:
        label = 'b*'
    else:
        label = 'X'
    theory_var_file = TFile.Open(bs_path+'pdf_norm_uncertainties_bstar.root')
    sigma_max = 20
    sigma_min = 0.00008
    mass_min = 1.2
    mass_max = 4.2
    # else: label = 'X'

    # Initialize arrays to eventually store the points on the TGraph
    x_mass = array('d')
    y_limit = array('d')
    y_mclimit  = array('d')
    y_mclimitlow68 = array('d')
    y_mclimitup68 = array('d')
    y_mclimitlow95 = array('d')
    y_mclimitup95 = array('d')

    tdrstyle.setTDRStyle()

    # For each signal
    for this_index, this_name in enumerate(signal_names):
        # Setup call for one of the signal
        this_xsec = signal_xsecs[this_index]
        this_mass = signal_mass[this_index]
        this_output = TFile.Open(this_name+'/higgsCombineTest.AsymptoticLimits.mH120.root')
        if not this_output: continue
        this_tree = this_output.Get('limit')
        print (this_mass)
        # Set the mass (x axis)
        x_mass.append(this_mass)
        # Grab the cross section limits (y axis)
        for ievent in range(int(this_tree.GetEntries())):
            this_tree.GetEntry(ievent)
            
            # Nominal expected
            if this_tree.quantileExpected == 0.5:
                print '\t%s %s'%(this_name,this_tree.limit*this_xsec)
                y_mclimit.append(this_tree.limit*this_xsec)
            # -1 sigma expected
            if round(this_tree.quantileExpected,2) == 0.16:
                y_mclimitlow68.append(this_tree.limit*this_xsec)
            # +1 sigma expected
            if round(this_tree.quantileExpected,2) == 0.84:
                y_mclimitup68.append(this_tree.limit*this_xsec)
            # -2 sigma expected
            if round(this_tree.quantileExpected,3) == 0.025:
                y_mclimitlow95.append(this_tree.limit*this_xsec)
            # +2 sigma expected
            if round(this_tree.quantileExpected,3) == 0.975:
                y_mclimitup95.append(this_tree.limit*this_xsec)

            # Observed (plot only if unblinded)
            if this_tree.quantileExpected == -1: 
                if not options.blind:
                    #print '\t%s %s'%(this_name,this_tree.limit*this_xsec)
                    y_limit.append(this_tree.limit*this_xsec)
                else:
                    y_limit.append(0.0)
    
    # Expected
    g_mclimit = TGraph(len(x_mass), x_mass, y_mclimit)
    g_mclimit.SetTitle("")
    g_mclimit.SetMarkerStyle(21)
    g_mclimit.SetMarkerColor(1)
    g_mclimit.SetLineColor(1)
    g_mclimit.SetLineStyle(1)
    g_mclimit.SetLineWidth(3)
    g_mclimit.SetMarkerSize(0.)

    g_mclimit.GetXaxis().SetTitle("m_{X_{"+cstr+"}} [TeV]")  # NOT GENERIC
    g_mclimit.GetYaxis().SetTitle("#sigma_{X_{"+cstr+"}} #times B(X_{"+cstr+"}#rightarrow tW) (pb)") # NOT GENERIC
    g_mclimit.GetYaxis().SetRangeUser(0., 80.)
    g_mclimit.GetXaxis().SetRangeUser(mass_min, mass_max)
    g_mclimit.SetMinimum(sigma_min) #0.005
    g_mclimit.SetMaximum(sigma_max)

    g_mclimit.GetXaxis().SetTitle("m_{X_{"+cstr+"}} [TeV]")  # NOT GENERIC
    g_mclimit.GetYaxis().SetTitle("#sigma_{X_{"+cstr+"}} B(X_{"+cstr+"}#rightarrow tW) (pb)") # NOT GENERIC

    # graphWP.Draw("l")
    g_mclimit.GetYaxis().SetTitleOffset(1.5)
    g_mclimit.GetXaxis().SetTitleOffset(1.25)

    expected_graphs[label] = g_mclimit
    

# Make Canvas and TGraphs (mostly stolen from other code that formats well)
climits = TCanvas("climits", "climits",700, 600)
climits.SetLogy(True)
climits.SetLeftMargin(.15)
climits.SetBottomMargin(.15)  
climits.SetTopMargin(0.1)
climits.SetRightMargin(0.05)

# NOT GENERIC
# if options.hand == 'LH':
#     cstr = 'L'
# elif options.hand == 'RH':
#     cstr = 'R'
# elif options.hand == 'VL':
#     cstr = 'LR'
# else:
#     cstr = ''


gStyle.SetTextFont(42)
TPT = ROOT.TPaveText(.20, .22, .5, .27,"NDC")
TPT.AddText("All-Hadronic Channel") # NOT GENERIC
TPT.SetFillColor(0)
TPT.SetBorderSize(0)
TPT.SetTextAlign(12)
    
gStyle.SetLegendFont(42)
legend = TLegend(0.6, 0.5, 0.91, 0.87, '')
legend.SetHeader("95% CL upper limits")

colors = [ROOT.kBlack,ROOT.kRed,ROOT.kBlue]

expected_graphs['b*'].Draw("al")
for i,e in enumerate(expected_graphs.keys()):
    expected_graphs[e].SetLineColor(colors[i])
    expected_graphs[e].Draw("l")
    legend.AddEntry(expected_graphs[e],e,'l')
# g_error95.Draw("lf")
# g_error.Draw("lf")
# g_mclimit.Draw("l")

# Legend and draw



# if not options.blind:
#     legend.AddEntry(g_limit, "Observed", "l")
# legend.AddEntry(g_mclimit, "Median expected","l")
# legend.AddEntry(g_error, "68% expected", "f")
# legend.AddEntry(g_error95, "95% expected", "f")
# legend.AddEntry(WPunc, "Theory "+label+"_{"+cstr+"}", "lf")   # NOT GENERIC
# legend.AddEntry(WPunc, "Theory "+label+"_{"+cstr+"} PDF uncertainty", "f")

legend.SetBorderSize(0)
legend.SetFillStyle(0)
legend.SetLineColor(0)

legend.Draw("same")

# text1 = ROOT.TLatex()
# text1.SetNDC()
# text1.SetTextFont(42)
# text1.DrawLatex(0.17,0.88, "#scale[1.0]{CMS, L = "+options.lumi+" fb^{-1} at  #sqrt{s} = 13 TeV}") # NOT GENERIC

# TPT.Draw()      
climits.RedrawAxis()

CMS_lumi.extraText = 'Preliminary'
CMS_lumi.lumiTextSize     = 0.5

CMS_lumi.cmsTextSize      = 0.8
CMS_lumi.CMS_lumi(climits, 1, 11)

climits.SaveAs("mulitlimits_combine_"+options.lumi.replace('.','p')+"fb_"+cstr+".pdf")


