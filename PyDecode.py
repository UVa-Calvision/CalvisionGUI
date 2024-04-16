# ROOT GUI for online display of histograms
# Created in July 2023 at University of Michigan

import time
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
import re
import glob
#import serial

#import serial.tools.list_ports
class PyDeocde(object):
 
    def __init__(self, file_name, numDevices, chnlNames):
        # self.MF = ROOT.TGMainFrame.__init__(self, ROOT.gClient.GetRoot(), 1000, 700)
        # self.fHor1 = ROOT.TGHorizontalFrame(self, 60, 20, ROOT.kFixedWidth)
        # self.fExit = ROOT.TGTextButton(self.fHor1, "&Exit", "gApplication->Terminate(0)")
        # self.fExit.SetCommand('TPython::Exec( "raise SystemExit" )')
        # self.fHor1.AddFrame(self.fExit, ROOT.TGLayoutHints(
        #     ROOT.kLHintsTop | ROOT.kLHintsLeft | ROOT.kLHintsExpandX, 4, 4, 4, 4))
        # self.AddFrame(self.fHor1, ROOT.TGLayoutHints(ROOT.kLHintsBottom | ROOT.kLHintsRight, 2, 2, 5, 1))
        # self.f1 = ROOT.TGFrame(self,60,20,ROOT.kFixedWidth)
        # ec1 = TRootEmbeddedCanvas()
        self.numDevices = numDevices
        self.file_name = file_name
        self.signalPath = '../SignalFiles/'
        self.filepath = '../WaveDumpData/'
        self.decodeSignalFile = self.signalPath + "decodeSignal.txt"
        self.numEvents = 0
        self.binhistos = []
        self.binlegends = []
        self.minhistos = []
        self.sumhistos = []
        self.c1 = TCanvas('Bin Histos', '%s Bin Graph' %file_name, 100, 10,  1000, 800 )
        self.c2 = TCanvas('Min Histos', '%s Min Histos' %file_name, 300, 10, 1000, 800 )
        self.c3 = TCanvas('Sum Histos', '%s Sum Histos' %file_name, 500, 10, 1000, 800 )
        #self.AddFrame(self.c1)
        self.timerGoing = False
        self.qTimer = QTimer()
        self.arr_chnl_names = chnlNames
        print(self.arr_chnl_names)
        # self.evtNum_data = [[] for i in range(len(self.arr_chnl_names)*self.numDevices)]
        # self.data = [[] for i in range(len(self.arr_chnl_names)*self.numDevices)]
        self.generated_evtNum = []
        self.new_evtNum_data = []
        self.new_data = []
        self.evtTrigTime_data = []
        self.dataFiles = []
        self.dataFileInfo = []
        self.newEvents = 0
        self.rootBaseFile =  self.filepath + self.file_name + '/'+ self.file_name + '.root' 
        self.hfile = gROOT.FindObject(self.rootBaseFile)
        if self.hfile:
            self.hfile.Close()
        self.hfile = TFile(self.rootBaseFile, 'new')
        self.hfile.Close()
    
    # destructor
    def __del__(self):
        print('Inside destructor')
        self.c1.Close()
        self.c2.Close()
        self.c3.Close()
        for file in self.dataFiles:
            file.close()

        print('Object destroyed')
        

    def createHistos(self):
        # Create some histograms, a profile histogram and an ntuple
        
        for i in range(len(self.dataFiles)):
            device = self.dataFileInfo[i]["device"]
            chnl = self.dataFileInfo[i]["chnl"]
            self.binhistos.append(TMultiGraph())
            l = TLegend(0.1,0.7,0.48,0.9)
            l.SetHeader('Waveform chnl_%s' % chnl,"C")
            self.binlegends.append(l)
            self.minhistos.append(TH1F(self.file_name+'_min_hist_device_%s' % device + '_chnl_%s' % chnl, 'Min Histo for device %s' % device + ' channel %s;ADC Counts' % chnl, 100, 0, 0 ))
            self.sumhistos.append(TH1F(self.file_name+'_sum_hist_device_%s' % device + '_chnl_%s' % chnl, 'Sum Histo for device %s' % device + ' channel %s;ADC Counts' % chnl, 100, 0, 0 ))
        
        size = (int)((len(self.dataFiles))**(1/2))
        self.c1.Divide(size, size+1)
        self.c2.Divide(size, size+1)
        self.c3.Divide(size, size+1)
        # print("New histograms created!")
        

    def histosPlot(self):
        if (self.getData() > 0):
            # print("There is data")
            for i in range(len(self.dataFiles)):
                # print("Trying to plot %s" %i)
                if (len(self.new_data[i]) > 0):
                    # print("There are %i new events to plot." %(len(self.new_data[i])))
                    self.c1.cd(i+1)
                    self.plot_bin_ROOT(i)
                    self.c2.cd(i+1)
                    self.plot_min_ROOT(i)
                    self.c3.cd(i+1)
                    self.plot_sum_ROOT(i)
            self.c1.Modified()
            self.c1.Update()
            self.c2.Modified()
            self.c2.Update()
            self.c3.Modified()
            self.c3.Update()
        else:
            print("Something went wrong ... are you sure there is data?")
        
        
    def plot_bin_ROOT(self, chnlNum):
        """
        This is for dat file with header file (8 header lines)
        """
        # print("Event start from %d, ends at %d, total %d." %(self.evtNum_data[chnlNum][0],self.evtNum_data[chnlNum][-1],len(self.evtNum_data[chnlNum])))
        # missing_trigger = 0
        # for i in range (len(self.evtNum_data[chnlNum])-1):
        #     if self.evtNum_data[chnlNum][i]!=self.evtNum_data[chnlNum][i+1]-1:
        #         missing_trigger += 1
        # if missing_trigger>0:
        #     print("Missing %d triggers" % missing_trigger)

        # plot
        # #    evt_num = [0, 1, 200]  # randomly pick 3 events to check
        # if (self.numEvents == -1) or (self.numEvents > len(self.data[chnlNum])):
        #     plot_evts = len(self.data[chnlNum])
        #     if plot_evts > 50:
        #         print("Warning: This may take a bit...")
        # else:
        #     plot_evts = self.numEvents
        # numList = np.linspace(2,7,9)
        x = array("f", [(data*.2) for data in np.linspace(0, 1024, 1024)])
        # for evt_num in range(len(self.new_evtNum_data[chnlNum])):
        #     #x = array("f", [data for data in self.new_data[chnlNum][evt_num]])
        #     y = array("f", [data for data in self.new_data[chnlNum][evt_num]])
        #     a = TGraph(len(x),x,y)
        #     a.SetLineColor((int)(random.choice(numList)))
        #     self.binhistos[chnlNum].Add(a)
        #     self.binlegends[chnlNum].AddEntry(a, "evnt %i" %self.new_evtNum_data[chnlNum][evt_num])
        # self.binhistos[chnlNum].Draw("AL")
        # self.binlegends[chnlNum].Draw()
        if (self.binhistos[chnlNum].GetListOfGraphs()):
            self.binhistos[chnlNum].GetListOfGraphs().Clear()
            self.binlegends[chnlNum].Clear()
    
        for evt_num in range(min(5,len(self.new_evtNum_data[chnlNum]))):
            #x = array("f", [data for data in self.new_data[chnlNum][evt_num]])
            y = array("f", [data for data in self.new_data[chnlNum][evt_num]])
            a = TGraph(len(x),x,y)
            a.SetLineColor(evt_num+2)
            self.binhistos[chnlNum].Add(a)
            self.binlegends[chnlNum].AddEntry(a, "evnt %i" %self.new_evtNum_data[chnlNum][evt_num])
        self.binhistos[chnlNum].Draw("AL")
        self.binlegends[chnlNum].Draw()

    def plot_min_ROOT(self, chnlNum):
        """
        This is for dat file with header file (8 header lines)
        """
        # plot
        min_list = [min(data) for data in self.new_data[chnlNum]]
        # print(min_list)
        
        #self.minhistos[chnlNum].Clear()
        for d in min_list:
            self.minhistos[chnlNum].Fill(d)
        #self.minhistos[chnlNum].ResetStats()
        # self.minhistos[chnlNum].SetMaximum(max([min(data) for data in self.data[chnlNum]]) + 10)
        # self.minhistos[chnlNum].SetMinimum(min([min(data) for data in self.data[chnlNum]]) - 10)
        # Rmin = int(min([min(data) for data in self.data[chnlNum]]) - 10)
        # Rmax = int(max([min(data) for data in self.data[chnlNum]]) + 10)
        # print("Min - min %i, " %Rmin + "max %i" %Rmax)
        # self.minhistos[chnlNum].GetXaxis().SetRangeUser(Rmin, Rmax)
        self.minhistos[chnlNum].Draw("")
        #self.minhistos[chnlNum].SetBinsLength(10)
    
    def plot_sum_ROOT(self, chnlNum):
        """
        This is for dat file with header file (8 header lines)
        """
        # plot
        sum_list = [sum(data[0:1000]) for data in self.new_data[chnlNum]]
        # print(sum_list)
        for d in sum_list:
            self.sumhistos[chnlNum].Fill(d)
            #self.sumhistos[chnlNum].SetBinsLength(10)
        #self.sumhistos[chnlNum].SetCanExtend(kAllAxes)
        # Rmin = int(min([sum(data[0:1000]) for data in self.data[chnlNum]]) - 10)
        # Rmax = int(max([sum(data[0:1000]) for data in self.data[chnlNum]]) + 10)
        # print("Sum - min %i, " %Rmin + "max %i" %Rmax)
        # self.minhistos[chnlNum].GetXaxis().SetRangeUser(Rmin, Rmax)
        # self.sumhistos[chnlNum].GetXaxis().UnZoom()
        self.sumhistos[chnlNum].Draw("")
    
    def updateFileName(self, file_name):
        self.file_name = file_name
        self.rootBaseFile =  self.filepath + self.file_name + '/'+ self.file_name + '.root' 
    
    def stopTimer(self):
        self.timerGoing = False
        self.saveHistos()

    def start(self, file_name):
        self.updateFileName(file_name)
        with open("./temp.txt", 'w') as f:
            f.write("Opened "+ self.file_name)

        # self.createHistos()
        # Create a new canvas, and customize it.
        # self.c1.SetFillColor( 42 )
        # self.c1.GetFrame().SetFillColor( 21 )
        # self.c1.GetFrame().SetBorderSize( 6 )
        # self.c1.GetFrame().SetBorderMode( -1 )

        print(self.rootBaseFile)
        self.startRun()
        
    def startRun(self):
        #loop = QEventLoop()
        #loop.startTimer(qTimer)
        #loop.customEvent(qTimer)
        # set interval to 1 s
        self.timerGoing = True
        self.qTimer.setInterval(1000) # 1000 ms = 1 s
        # connect timeout signal to signal handler
        self.qTimer.timeout.connect(self.refresh)
        # start timer
        self.qTimer.start()
    
    def getData(self) -> int:
        ldF = len(self.dataFiles)
        if (ldF > 0):
            self.new_evtNum_data = [[] for i in range(ldF)]
            self.new_data = [[] for i in range(ldF)]
            header_size = 32
            for a in range(ldF):
                # print((str)(range(self.newEvents)))
                for i in range(self.newEvents):
                    # print("Chnl %s: event to read " %(self.arr_chnl_names[a%len(self.arr_chnl_names)]) + (str)(i))
                    header_content = self.dataFiles[a].read(header_size)
                    content = self.dataFiles[a].read(1024 * 4)
                    if (header_content and content):
                        header = struct.unpack("8i", header_content)
                        
                        # if header[5] in self.evtTrigTime_data:
                        #     evtNum = self.evtTrigTime_data.index(header[5])
                        # else:
                        #     self.evtTrigTime_data.append(header[5])
                        #     evtNum = self.evtTrigTime_data.index(header[5])
                        evtNum = header[4]
                        #content = self.dataFiles[a].read(1024 * 4)
                        # self.data[a].append(struct.unpack("1024f", content))
                        # self.evtNum_data[a].append(header[4])
                        self.new_data[a].append(struct.unpack("1024f", content))
                        self.new_evtNum_data[a].append(evtNum)
                        self.generated_evtNum[a].append(evtNum)
                        # print("Trigger Time: %i " %self.evtTrigTime_data[evtNum] + "Event Number: %i " %evtNum + "Event Number given: %i" %header[4])
                       
                    else:
                        print("I thought there was another new event?")
                if (self.dataFileInfo[a]["chnl"] == "00"):
                    print("Device %s" %self.dataFileInfo[a]["device"] + "Chnl 00, event %i" %header[4])
            return 1
        else:
            if self.createFiles() < 0:
                return -1
            else:
                self.createHistos()
                return self.getData()

    
    def createFiles(self) -> int:
        files = glob.glob(self.filepath + self.file_name + '/*.dat')
        if len(files) <= 0:
            return -1
        filesName_re = re.compile("../([a-zA-Z0-9_.]+)/([a-zA-Z0-9_.]+)/([a-zA-Z0-9_.]+)_device_(?P<device>\d)_chnl_(?P<chnl>[a-zA-Z0-9_.]+).dat$", re.I)
        files.sort()
        for file in files:
        #     for i in range(len(self.arr_chnl_names[d])):
        #         # fileToLookAt = os.path.join(self.filepath + self.file_name + "/" + self.file_name + "_device_%i" %d + "_chnl_" + self.arr_chnl_names[d][i] + '.dat')
        #         # if (os.path.isfile(fileToLookAt)):
        #         #     self.dataFiles.append(open(fileToLookAt, "rb"))
        #         # else:
        #         #     print("missing some files...")
        #         #     return -1
            info = filesName_re.match(file)
            if info:
                dinfo = info.groupdict()
                self.dataFileInfo.append(dinfo)
                self.dataFiles.append(open(file, "rb"))
                self.generated_evtNum.append([])
        return 1

    def refresh(self):
        if self.timerGoing:
            fileToLookAt = os.path.join(self.filepath + self.file_name + "/" + self.file_name + "_device_0_chnl_" + self.arr_chnl_names[0][0] + '.dat')
            events = 0
            
            if (len(self.dataFiles) > 0 or os.path.isfile(fileToLookAt)):
                try:
                    file_size = os.path.getsize(fileToLookAt)
                    #print(f"File Size in Bytes is {file_size}")
                    events = int (file_size / (1024 * 4 + 32))
                    #print("There are %i in the file" %events)
                except FileNotFoundError:
                    print("File not found.")
                except OSError:
                    print("OS error occurred.")
                
                self.newEvents = events - self.numEvents
                self.numEvents += self.newEvents
                if (self.newEvents > 0):
                    self.histosPlot()
            
            # if (os.path.isfile(self.decodeSignalFile)):
            #     with open(self.decodeSignalFile, 'r') as f:
            #         self.newEvents = (int) (f.read()) - self.numEvents
            #         if 0 < self.newEvents:
            #             print("%i new events!" %self.newEvents)
            #             self.numEvents += self.newEvents
            #             # if len(self.dataFiles) == 0:
            #             #     self.createFiles
            #             # if len(self.dataFiles) > 0:
            #             #     current = self.dataFiles[0].tell()
            #             #     self.dataFiles[len(self.dataFiles)-1].seek(0,2)
            #             #     file_size = self.dataFiles[len(self.dataFiles)-1].tell()
            #             #     self.dataFiles[len(self.dataFiles)-1].seek(current,0)
            #             #     events = int (file_size / (1024 * 4 + 32))
            #             #     print("There are %i in the file" %events)
            #             #     if (events != self.numEvents):
            #             #         self.newEvents = self.newEvents - (self.newEvents - events)
            #             if (self.newEvents > 0):
            #                 self.histosPlot()
        else:
            self.qTimer.stop()

    def saveHistos(self):
        self.hfile = TFile(self.rootBaseFile, 'RECREATE')
        for i in range(len(self.dataFileInfo)):
            # print("Trying to save %s" %i)
            device = self.dataFileInfo[i]["device"]
            chnl = self.dataFileInfo[i]["chnl"]
            self.binhistos[i].Write("MG_device_%s_" % device + chnl)
            self.binlegends[i].Write("LEG_device_%s_" % device + chnl)
            self.minhistos[i].Write()
            self.sumhistos[i].Write()
        if (len(self.hfile.GetListOfKeys()) < len(self.dataFiles)):
            print("Not enough histograms were saved...")
        self.hfile.Write()


    def close(self):
        self.stopTimer()
        self.hfile.Close()
        self.__del__()

# if __name__ == "__main__":
#     if(os.path.isfile("./stop.txt")):
#         os.remove("./stop.txt")

#     args = sys.argv[1:]
#     file_name = args[0]
#     print(file_name)
#     decode = PyDeocde(file_name, int(args[1]))
#     decode.start(file_name)

    # sys.exit(decode.__del__())