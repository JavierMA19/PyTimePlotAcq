#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 12:25:45 2019

@author: aguimera
"""

from PyQt5 import Qt
import pyqtgraph.parametertree.parameterTypes as pTypes
import numpy as np
import TPacqCore as CoreMod
import FileModule as FileMod


SampSettingConf = ({'title': 'Channels Config',
                    'name': 'ChsConfig',
                    'type': 'group',
                    'children': ({'title': 'Acquire DC',
                                  'name': 'AcqDC',
                                  'type': 'bool',
                                  'value': False},
                                 {'title': 'Acquire AC',
                                  'name': 'AcqAC',
                                  'type': 'bool',
                                  'value': True},
                                 {'tittle': 'Channels',
                                  'name': 'Channels',
                                  'type': 'group',
                                  'children': ({'name': 'Ch01',
                                                'tip': 'Ch01',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch02',
                                                'tip': 'Ch02',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch03',
                                                'tip': 'Ch03',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch04',
                                                'tip': 'Ch04',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch05',
                                                'tip': 'Ch05',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch06',
                                                'tip': 'Ch06',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch07',
                                                'tip': 'Ch07',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch08',
                                                'tip': 'Ch08',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch09',
                                                'tip': 'Ch09',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch10',
                                                'tip': 'Ch10',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch11',
                                                'tip': 'Ch11',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch12',
                                                'tip': 'Ch12',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch13',
                                                'tip': 'Ch13',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch14',
                                                'tip': 'Ch14',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch15',
                                                'tip': 'Ch15',
                                                'type': 'bool',
                                                'value': True},
                                               {'name': 'Ch16',
                                                'tip': 'Ch16',
                                                'type': 'bool',
                                                'value': True},), },
                                 ), },

                   {'name': 'Sampling Settings',
                    'type': 'group',
                    'children': ({'title': 'Sampling Frequency',
                                  'name': 'Fs',
                                  'type': 'float',
                                  'value': 10e3,
                                  'step': 100,
                                  'siPrefix': True,
                                  'suffix': 'Hz'},
                                 {'title': 'Refresh Time',
                                  'name': 'Refresh',
                                  'type': 'float',
                                  'value': 1,
                                  'step': 0.01,
                                  'limits': (0.10, 300),
                                  'siPrefix': True,
                                  'suffix': 's'},
                                 {'title': 'Fs by Channel',
                                  'name': 'FsxCh',
                                  'type': 'float',
                                  'value': 1e4,
                                  'step': 100,
                                  'siPrefix': True,
                                  'suffix': 'Hz',
                                  'readonly': True},
                                 {'title': 'Vds',
                                  'name': 'Vds',
                                  'type': 'float',
                                  'value': 0.05,
                                  'step': 0.01,
                                  'limits': (0, 0.1)},
                                 {'title': 'Vgs',
                                  'name': 'Vgs',
                                  'type': 'float',
                                  'value': 0.1,
                                  'step': 0.1,
                                  'limits': (-0.1, 0.5)}, ), }
                   )


###############################################################################


class SampSetParam(pTypes.GroupParameter):
    NewConf = Qt.pyqtSignal()

    Chs = []
    Acq = {}

    def __init__(self, **kwargs):
        super(SampSetParam, self).__init__(**kwargs)
        self.addChildren(SampSettingConf)

        self.SampSet = self.param('Sampling Settings')
        self.Fs = self.SampSet.param('Fs')
        self.Refresh = self.SampSet.param('Refresh')
        self.FsxCh = self.SampSet.param('FsxCh')

        self.ChsConfig = self.param('ChsConfig')
        self.Channels = self.ChsConfig.param('Channels')

        # Init Settings
        self.on_Acq_Changed()
        self.on_Ch_Changed()
        self.on_Fs_Changed()

        print(self.children())
        # Signals
        self.Channels.sigTreeStateChanged.connect(self.on_Ch_Changed)
        self.ChsConfig.param('AcqAC').sigValueChanged.connect(self.on_Acq_Changed)
        self.ChsConfig.param('AcqDC').sigValueChanged.connect(self.on_Acq_Changed)
        self.Fs.sigValueChanged.connect(self.on_Fs_Changed)

    def on_Acq_Changed(self):
        for p in self.ChsConfig.children():
            if p.name() is 'AcqAC':
                self.Acq[p.name()] = p.value()
            if p.name() is 'AcqDC':
                self.Acq[p.name()] = p.value()
        self.NewConf.emit()

    def on_Fs_Changed(self):
        Ts = 1/self.Fs.value()
        FsxCh = 1/(Ts*len(self.Chs))
        if self.Acq['AcqDC'] and self.Acq['AcqAC'] is True:
            FsxCh = FsxCh * 0.5
#        IntTime = (1/(FsxCh))
        self.SampSet.param('FsxCh').setValue(FsxCh)
        self.SampSet.param('Refresh').setValue(self.Refresh)

    def on_Ch_Changed(self):
        self.Chs = []
        for p in self.Channels.children():
            if p.value() is True:
                self.Chs.append(p.name())
        self.on_Fs_Changed()
        self.NewConf.emit()

    def GetChannelsNames(self):
        Ind = 0
        ChNames = {}
        acqTys = []
        for tyn, tyv in self.Acq.items():
            if tyv:
                acqTys.append(tyn)

        if 'AcqAC' in acqTys:
            for Ch in self.Chs:
                ChNames[Ch + 'AC'] = Ind
                Ind += 1

        if 'AcqDC' in acqTys:
            for Ch in self.Chs:
                ChNames[Ch + 'DC'] = Ind
                Ind += 1
        return ChNames

    def GetSampKwargs(self):
        GenKwargs = {}
        for p in self.SampSet.children():
            GenKwargs[p.name()] = p.value()
        return GenKwargs

    def GetChannelsConfigKwargs(self):
        ChanKwargs = {}
        for p in self.ChsConfig.children():
            if p.name() is 'Channels':
                ChanKwargs[p.name()] = self.Chs
            else:
                ChanKwargs[p.name()] = p.value()
        print(ChanKwargs)
        return ChanKwargs

###############################################################################


class DataAcquisitionThread(Qt.QThread):
    NewTimeData = Qt.pyqtSignal()

    def __init__(self, ChannelsConfigKW, SampKw):
        print('InitDataAcqThread')
        super(DataAcquisitionThread, self).__init__()
        print(ChannelsConfigKW)
        self.DaqInterface = CoreMod.ChannelsConfig(**ChannelsConfigKW)
        self.DaqInterface.DataEveryNEvent = self.NewData
        self.SampKw = SampKw

    def run(self, *args, **kwargs):
        print('Run')
        print(self.SampKw)
        self.DaqInterface.StartAcquisition(**self.SampKw)
        loop = Qt.QEventLoop()
        loop.exec_()

#    def CalcAverage(self, MuxData):
#        Avg = np.mean(LinesSorted[:,-2:,:], axis=1)
#        return np.mean(MuxData[:, self.AvgIndex:, :], axis=1)

    def NewData(self, aiData):
        print('NewData')
#        self.OutData = self.CalcAverage(MuxData)
        self.aiData = aiData
        self.NewTimeData.emit()
