#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  5 14:13:45 2019

@author: aguimera
"""
import PyCont.DaqInterface as DaqInt

#import DaqInterface as DaqInt
import numpy as np


# Daq card connections mapping 'Chname':(DCout, ACout)
aiChannels = {'Ch01': ('ai0', 'ai8'),
              'Ch02': ('ai1', 'ai9'),
              'Ch03': ('ai2', 'ai10'),
              'Ch04': ('ai3', 'ai11'),
              'Ch05': ('ai4', 'ai12'),
              'Ch06': ('ai5', 'ai13'),
              'Ch07': ('ai6', 'ai14'),
              'Ch08': ('ai7', 'ai15'),
              'Ch09': ('ai16', 'ai24'),
              'Ch10': ('ai17', 'ai25'),
              'Ch11': ('ai18', 'ai26'),
              'Ch12': ('ai19', 'ai27'),
              'Ch13': ('ai20', 'ai28'),
              'Ch14': ('ai21', 'ai29'),
              'Ch15': ('ai22', 'ai30'),
              'Ch16': ('ai23', 'ai31'),
              }


##############################################################################


class ChannelsConfig():

    DCChannelIndex = None
    ACChannelIndex = None
    ChNamesList = None
    AnalogInputs = None
    GateChannel = None

    # Events list
    DataEveryNEvent = None
    DataDoneEvent = None

    def _InitAnalogInputs(self):
        print('InitAnalogInputs')
        self.DCChannelIndex = {}
        self.ACChannelIndex = {}
        InChans = []
        index = 0
        sortindex = 0
        for ch in self.ChNamesList:
            if self.AcqDC:
                InChans.append(aiChannels[ch][0])
                self.DCChannelIndex[ch] = (index, sortindex)
                index += 1
                print(ch, ' DC -->', aiChannels[ch][0])
                print('SortIndex ->', self.DCChannelIndex[ch])
            if self.AcqAC:
                InChans.append(aiChannels[ch][1])
                self.ACChannelIndex[ch] = (index, sortindex)
                index += 1
                print(ch, ' AC -->', aiChannels[ch][1])
                print('SortIndex ->', self.ACChannelIndex[ch])
            sortindex += 1

        print('Input ai', InChans)

        self.AnalogInputs = DaqInt.ReadAnalog(InChans=InChans)
        # events linking
        self.AnalogInputs.EveryNEvent = self.EveryNEventCallBack
        self.AnalogInputs.DoneEvent = self.DoneEventCallBack

    def _InitAnalogOutputs(self, ChVds, ChVs):
        print('ChVds ->', ChVds)
        print('ChVs ->', ChVs)
        self.VsOut = DaqInt.WriteAnalog((ChVs,))
        self.VdsOut = DaqInt.WriteAnalog((ChVds,))

    def __init__(self, Channels,
                 AcqDC=True, AcqAC=True,
                 ChVds='ao0', ChVs='ao1',
                 ACGain=1e6, DCGain=10e3):
        print('InitChannels')
        self._InitAnalogOutputs(ChVds=ChVds, ChVs=ChVs)

        self.ChNamesList = sorted(Channels)
        self.AcqAC = AcqAC
        self.AcqDC = AcqDC
        self.ACGain = ACGain
        self.DCGain = DCGain
        self._InitAnalogInputs()

    def StartAcquisition(self, Fs, Refresh, Vgs, Vds, **kwargs):
        self.SetBias(Vgs=Vgs, Vds=Vds)
        EveryN = Refresh*Fs # TODO check this
        self.AnalogInputs.ReadContData(Fs=Fs,
                                       EverySamps=EveryN)

    def SetBias(self, Vgs, Vds):
        print('ChannelsConfig SetBias Vgs ->', Vgs, 'Vds ->', Vds)
        self.VdsOut.SetVal(Vds)
        self.VsOut.SetVal(-Vgs)
        self.BiasVd = Vds-Vgs
        self.Vgs = Vgs
        self.Vds = Vds

    def _SortChannels(self, data, SortDict):
        (samps, inch) = data.shape
        sData = np.zeros((samps, len(SortDict)))
        for chn, inds in sorted(SortDict.iteritems()):
            sData[:, inds[1]] = data[:, inds[0]]

        return sData

    def EveryNEventCallBack(self, Data):

        _DataEveryNEvent = self.DataEveryNEvent

        if _DataEveryNEvent is not None:
            if self.AcqDC:
                aiDataDC = self._SortChannels(Data, self.DCChannelIndex)
                aiDataDC = (aiDataDC-self.BiasVd) / self.DCGain

            if self.AcqAC:
                aiDataAC = self._SortChannels(Data, self.ACChannelIndex)
                aiDataAC = aiDataAC / self.ACGain

            if self.AcqAC and self.AcqDC:
                aiData = np.hstack((aiDataDC, aiDataAC))
                _DataEveryNEvent(aiData)
            elif self.AcqAC:
                _DataEveryNEvent(aiDataAC)
            elif self.AcqDC:
                _DataEveryNEvent(aiDataDC)
        
    def DoneEventCallBack(self, Data):
        print('Done callback')

    def Stop(self):
        print('Stopppp')
        self.SetBias(Vgs=0, Vds=0)
        self.AnalogInputs.StopContData()


