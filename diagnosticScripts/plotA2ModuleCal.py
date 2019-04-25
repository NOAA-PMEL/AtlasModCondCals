# for plotting the TC module calibrations and troubleshooting
# Author: Daryn White, daryn.white@noaa.gov
import os
import holoviews
import pandas
import argparse


class moduleData(object):
    """docstring for moduleData."""

    def toDataframe(file, sn):
        df = pandas.read_csv(file)
        dtIndex = 'DT_' + sn
        df = df.set_index(pandas.DatetimeIndex(df[dtIndex], tz='UTC', freq='infer', dayfirst=True))
        df = df.tz_convert('US/Pacific', copy=False)
        df.drop(dtIndex, axis=1, inplace=True)
        return df

    def toHvDataset(df):
        kdim = df.index.name
        dataSet = holoviews.Dataset(df.reset_index(), kdims=kdim)
        return dataSet

    def toHvCurve(arg):
        if type(arg) is not holoviews.core.data.Dataset:
            pass
        else:
            rt = arg.to(holoviews.Curve)
        return rt

    def saveHvFig(fig, name):
        if type(fig) is holoviews.element.chart.Curve:
            rt = holoviews.save(fig, name)
        else:
            pass
        return rt

    def __init__(self, arg):
        super(moduleData, self).__init__()
        self.arg = arg


def __int__(arg):
    parser = argparse.ArgumentParser()
    parser.add_argument('files')
