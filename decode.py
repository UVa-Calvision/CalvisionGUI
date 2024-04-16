#!/usr/bin/env python
# coding: utf-8
import os
import sys

import numpy as np
import matplotlib.pyplot as plt
import struct

# single event

def plot_SingleEvt(txtFile, datFile):
    """
    This is for txt file with header file (8 header lines)
    """
    # read txt file
    f_txt = open(txtFile, "r")
    lines = f_txt.readlines()
    
    arr_txt = [float(line.strip()) for line in lines[8:]]
    
    # read dat file
    with open(datFile, 'rb') as f_dat:
        content = f_dat.read()
        arr_dat = struct.unpack("f" * (len(content) // 4), content)
    
    # plot
    fig, ax = plt.subplots(1,1,figsize=(9,6))
    x = np.linspace(0,1024,1024)
    plt.plot(x,arr_txt,label="txt")
    plt.plot(x,arr_dat,label="dat")
    plt.xlabel("# of ns", fontsize=20)
    plt.title("Single Event", fontsize=24)
    plt.legend(loc="lower right", fontsize=14)
    plt.show()
    
    fig.savefig("1event.png")
    plt.close()


# multi events

def plot_MultiEvt(txtFile, datFile):
    """
    This is for txt & dat file with header file (8 header lines)
    """
    # read txt file
    f_txt = open(txtFile, "r")

    arr_txt = []
    lines_txt = f_txt.readlines()
    idx = 0
    n_evt = int(len(lines_txt)/1032)
    for i in range(n_evt):
        arr_txt.append(lines_txt[idx+8:idx+1032])
        idx += 1032

    for i in range(len(arr_txt)):
        arr_txt[i] = [float(x.strip()) for x in arr_txt[i]]

    
    # read dat file
    
    header_size = 32
    
    arr_dat = []
    with open(datFile, 'rb') as f_dat:
        while (f_dat.read(header_size)):
            content = f_dat.read(1024*4)
            arr_dat.append(struct.unpack("1024f", content))
    
    # plot
    fig, ax = plt.subplots(1,1,figsize=(9,6))
    x = np.linspace(0,1024,1024)
    
    evt_num = [0,100,200] # randomly pick 3 events to check
    plt.plot(x,arr_txt[evt_num[0]],label="txt_evt%i"%evt_num[0])
    plt.plot(x,arr_txt[evt_num[1]],label="txt_evt%i"%evt_num[1])
    plt.plot(x,arr_txt[evt_num[2]],label="txt_evt%i"%evt_num[2])
    plt.plot(x,arr_dat[evt_num[0]],label="dat_evt%i"%evt_num[0])
    plt.plot(x,arr_dat[evt_num[1]],label="dat_evt%i"%evt_num[1])
    plt.plot(x,arr_dat[evt_num[2]],label="dat_evt%i"%evt_num[2])
    plt.xlabel("# of ns", fontsize=20)
    plt.title("Multi Events", fontsize=24)
    plt.legend(loc="lower right", fontsize=14)
    plt.show()
    
    fig.savefig("multievents.png")
    plt.close('all')


def plot_bin(filepath, file_name, device_num, chnl_num, num_evts):
    """
    This is for dat file with header file (8 header lines)
    """
    # read dat file
    file_chnl_part = filepath+file_name + '/'+ file_name+'_device_%i' %device_num +'_chnl_%s' % chnl_num
    fileToLookAt = os.path.join(file_chnl_part + '.dat')
    header_size = 32

    arr_dat = []
    arr_evtNum_dat = []
    with open(fileToLookAt, 'rb') as f_dat:
        header_content = f_dat.read(header_size)
        print(struct.unpack("8i", header_content))
        while header_content:
            content = f_dat.read(1024 * 4)
            arr_dat.append(struct.unpack("1024f", content))
            arr_evtNum_dat.append(struct.unpack("8i", header_content)[4])
            header_content = f_dat.read(header_size)
    print("Event start from %d, ends at %d, total %d." %(arr_evtNum_dat[0],arr_evtNum_dat[-1],len(arr_evtNum_dat)))
    missing_trigger = 0
    for i in range (len(arr_evtNum_dat)-1):
        if arr_evtNum_dat[i]!=arr_evtNum_dat[i+1]-1:
            missing_trigger += 1
    if missing_trigger>0:
        print("Missing %d triggers" % missing_trigger)


    # plot
    fig, ax = plt.subplots(1, 1, figsize=(9, 6))
    x = np.linspace(0, 1024, 1024)
    #    evt_num = [0, 1, 200]  # randomly pick 3 events to check
    if (num_evts == -1) or (num_evts > len(arr_dat)):
        plot_evts = len(arr_dat)
        if plot_evts > 50:
            print("Warning: This may take a bit...")
    else:
        plot_evts = num_evts

    for evt_num in range(plot_evts):
        plt.plot(x*.2, arr_dat[evt_num], label="dat_evt%i" % evt_num)


    plt.xlabel("Time (ns)", fontsize=20)
    plt.title('chnl_%s' % chnl_num, fontsize=24)
    plt.legend(loc="lower right", fontsize=14)
    #plt.show()
    if not os.path.exists(filepath+file_name+'/waveforms'):
        os.makedirs(filepath+file_name+'/waveforms')
    png_name = filepath+file_name+'/waveforms/'+file_name+'_device_%i' %device_num +'_chnl_%s' % chnl_num+'.png'
    fig.savefig(png_name)
    plt.close('all')
    

def plot_all_bin_files(file_path,file_name, deviceNum, num_evts):
    #arr_chnl_names = ['0', '1', '2', '3', '4', '5', '6', '7', 'TR_0_0']
    arr_chnl_names = ['00', '01', '02', '03', '04', '05', '06', '07', 'TR_0_0']
    for d in range(deviceNum):
        for i in arr_chnl_names:
            print("working on channel %s" % i)
            plot_bin(file_path, file_name, d, i, num_evts)

def plot_min(filepath,file_name, device_num, chnl_num ,number_of_bins, plot_sum_flag):
    """
    This is for dat file with header file (8 header lines)
    """
    # read dat file
    file_chnl_part = filepath+file_name + '/'+ file_name+'_device_%i' %device_num + '_chnl_%s' % chnl_num
    fileToLookAt = os.path.join(file_chnl_part + '.dat')
    header_size = 32

    arr_dat = []
    with open(fileToLookAt, 'rb') as f_dat:
        while (f_dat.read(header_size)):
            content = f_dat.read(1024 * 4)
            arr_dat.append(struct.unpack("1024f", content))

    # plot
    min_list = [min(data) for data in arr_dat]
    fig = plt.figure()
    plt.hist(min_list,bins=number_of_bins)
    plt.xlabel("ADC counts", fontsize=20)
    plt.title('chnl_%s' % chnl_num+'_hist', fontsize=24)
    #plt.show()
    if not os.path.exists(filepath+file_name+'/min_hist'):
        os.makedirs(filepath+file_name+'/min_hist')
    png_name = filepath+file_name+'/min_hist/'+file_name+'_device_%i' %device_num +'_chnl_%s' % chnl_num+'_hist.png'
    fig.savefig(png_name)
    if plot_sum_flag:
        sum_list = [sum(data[0:1000]) for data in arr_dat]
        fig = plt.figure()
        plt.hist(sum_list, bins=number_of_bins)
        plt.xlabel("ADC counts", fontsize=20)
        plt.title('chnl_%s' % chnl_num + '_sum_hist', fontsize=24)
        # plt.show()
        if not os.path.exists(filepath + file_name + '/sum_hist'):
            os.makedirs(filepath + file_name + '/sum_hist')
        png_name = filepath + file_name + '/sum_hist/' + file_name + '_device_%i' %device_num +'_chnl_%s' % chnl_num + '_sum_hist.png'
        fig.savefig(png_name)
    plt.close('all')

def plot_all_min_files(filepath,file_name, deviceNum, num_bin, plot_sum_flag):
    arr_chnl_names = ['00', '01', '02', '03', '04', '05', '06', '07', 'TR_0_0']
    for d in range(deviceNum):
        for i in arr_chnl_names:
            print("working on channel %s min hist" % i)
            plot_min(filepath, file_name, d, i, num_bin, plot_sum_flag)

def plot_sum(filepath,file_name, device_num, chnl_num ,number_of_bins):
    """
    This is for dat file with header file (8 header lines)
    """
    # read dat file
    file_chnl_part = filepath+file_name + '/'+ file_name+'_device_%i' %device_num +'_chnl_%s' % chnl_num
    fileToLookAt = os.path.join(file_chnl_part + '.dat')
    header_size = 32

    arr_dat = []
    with open(fileToLookAt, 'rb') as f_dat:
        while (f_dat.read(header_size)):
            content = f_dat.read(1024 * 4)
            arr_dat.append(struct.unpack("1024f", content))

    # plot
    sum_list = [sum(data[0:1000]) for data in arr_dat]
    fig = plt.figure()
    plt.hist(sum_list,bins=number_of_bins)
    plt.xlabel("ADC counts", fontsize=20)
    plt.title('chnl_%s' % chnl_num+'_sum_hist', fontsize=24)
    #plt.show()
    if not os.path.exists(filepath+file_name+'/sum_hist'):
        os.makedirs(filepath+file_name+'/sum_hist')
    png_name = filepath+file_name+'/sum_hist/'+file_name+'_device_%i' %device_num +'_chnl_%s' % chnl_num+'_sum_hist.png'
    fig.savefig(png_name)
    plt.close('all')

def plot_all_sum_files(filepath,file_name, deviceNum, num_bin):
    arr_chnl_names = ['00', '01', '02', '03', '04', '05', '06', '07', 'TR_0_0']
    for d in range(deviceNum):
        for i in arr_chnl_names:
            print("working on channel %s min hist" % i)
            plot_sum(filepath, file_name, d, i, num_bin)
# def main():
#
#     #txtFile = "wave_0_ascii_header.txt"
#     #datFile = "wave_0_bin_noheader.dat"
#     #plot_SingleEvt(txtFile, datFile)
#
#     #txtFile = "wave_0_ascii_header_multievents.txt"
#     #datFile = "wave_0_bin_header_multievents.dat"
#     #plot_MultiEvt(txtFile, datFile)
#
#     #datFile = "run_angle_crystal_type_20230601_173819_chnl_0.dat"
#     plot_all_bin_files("run_1_baseline_0degrees_PbF2_20230602_125917", 10)
def main(args,dev):
    print(args + "...\n")
    filepath = '../WaveDumpData/'
    file_name = args
    devices = (int)(dev)
    with open("./temp.txt", 'w') as f:
        f.write("Opened "+ file_name)
    try:
        plot_all_bin_files(filepath,file_name,devices, 10)
        plot_all_min_files(filepath,file_name,devices,num_bin=20, plot_sum_flag=1)
        plot_all_sum_files(filepath,file_name,devices,num_bin=20)
    except (FileNotFoundError):
        print("File was not found, was data collected?")
    

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
    


