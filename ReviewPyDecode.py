# ROOT GUI for online display of past histograms
# Created in July 2023 at University of Michigan

from PyQt5.QtCore import QTimer, QEventLoop
import sys
import ROOT
from ROOT import TCanvas, TLegend, TFile, TMultiGraph, TGraph, TGFrame, TGWindow, TGTab, TGButton, TRootEmbeddedCanvas, TApplication, TProfile, TNtuple, TH1F, TH2F
from ROOT import gROOT, gBenchmark, gRandom, gSystem
import numpy as np
import matplotlib.pyplot as plt
import struct
import ctypes
import multiprocessing
import os
from array import array
import random
#import serial

#import serial.tools.list_ports
class ReviewPyDecode(object):
 
    def __init__(self, file_name, rootFile):
        self.file_name = file_name
        self.signalPath = '../SignalFiles/'
        self.filepath = '../WaveDumpData/'
        self.numEvents = 0
        self.binhistos = []
        self.binlegends = []
        self.minhistos = []
        self.sumhistos = []
        self.c1 = TCanvas('Past Bin Histos', '%s Bin Graph' %file_name, 200, 10,  1000, 700 )
        self.c2 = TCanvas('Past Min Histos', '%s Min Histos' %file_name, 200, 10, 1000, 700 )
        self.c3 = TCanvas('Past Sum Histos', '%s Sum Histos' %file_name, 200, 10, 1000, 700 )
        self.arr_chnl_names = ['00', '01', '02', '03', '04', '05', '06', '07', 'TR_0_0', '08', '09', '10', '11', '12', '13', '14', '15']
        self.rootBaseFile =  rootFile
        # self.hfile = gROOT.FindObject(self.rootBaseFile)
        # if self.hfile:
        #     self.hfile.Close()
        self.hfile = TFile(self.rootBaseFile)
        print(self.file_name)
        #self.hfile.ls()
        self.histosPlot()
    
    # destructor
    def __del__(self):
        print('Inside destructor')
        self.close
        self.c1.Close()
        self.c2.Close()
        self.c3.Close()

        print('Object destroyed')

    def close(self):
        self.hfile.Close()
        print('Inside destructor')
        self.close()
        self.c1.Close()
        self.c2.Close()
        self.c3.Close()

        print('Object destroyed')

    def histosPlot(self):
        print("Trying to plot")
        obs = self.hfile.GetListOfKeys()
        print(obs)
        
        for o in obs:
            n = o.GetName()
            if "MG" in n:
                if not(n in self.binhistos):
                    self.binhistos.append(n)
                    print(n)
            elif "min" in n:
                if not(n in self.minhistos):
                    self.minhistos.append(n)
                    print(n)
            elif "sum" in n:
                if not(n in self.sumhistos):
                    self.sumhistos.append(n)
                    print(n)
            if "LEG" in n:
                if not(n in self.binlegends):
                    self.binlegends.append(n)
                    print(n)
        
        size = (int)((len(self.minhistos))**(1/2))
        self.c1.Divide(size, size+1)
        self.c2.Divide(size, size+1)
        self.c3.Divide(size, size+1)

        i = 0
        for p in self.binhistos:
            self.c1.cd(i+1)
            a = self.hfile.Get(p)
            a.Draw("AL")
            i += 1
        i = 0
        for p in self.binlegends:
            self.c1.cd(i+1)
            a = self.hfile.Get(p)
            a.Draw("")
            i += 1
        self.c1.Modified()
        self.c1.Update()

        i = 0
        for p in self.minhistos:
            self.c2.cd(i+1)
            a = self.hfile.Get(p)
            a.Draw("")
            i += 1
        self.c2.Modified()
        self.c2.Update()

        i = 0
        for p in self.sumhistos:
            self.c3.cd(i+1)
            a = self.hfile.Get(p)
            a.Draw("")
            i += 1
        self.c3.Modified()
        self.c3.Update()

        # i = 0
        # for chnl_num in self.arr_chnl_names:
        #     print("Trying to plot %s" %i)
        #     self.c1.cd(i+1)
        #     print("MG_%s" %chnl_num)
        #     a = self.hfile.Get("MG_%s" %chnl_num)
        #     a.Draw("AL")
        #     a = self.hfile.Get("LEG_%s" %chnl_num)
        #     a.Draw()
        #     self.c2.cd(i+1)
        #     a = self.hfile.Get(self.file_name+'_min_hist_chnl_%s' % chnl_num)
        #     a.Draw()
        #     self.c3.cd(i+1)
        #     a = self.hfile.Get(self.file_name+'_sum_hist_chnl_%s' % chnl_num)
        #     a.Draw()
        #     i += 1