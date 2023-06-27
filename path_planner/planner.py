import csv
from datetime import timedelta

import numpy as np
import pandas as pd
import traces
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d

from src.utils import delta_distance

columns = ["timeSeconds", "positionMeters", "velocityMetersPerSecond", "accelerationMetersPerSecondSq",
           "headingDegrees",
           "holonomicRotationDegrees", "curvatureRadPerMeter", "curveRadiusMeters", "angularVelocityDegreesPerSec",
           "angularAccelerationDegreesPerSecSq"]
df = pd.read_csv(r"C:\work\c++_projects\frc\FRC-team230-2022\src\main\deploy\pathplanner\generatedCSV\New Path.csv",
                 skiprows=[0, 1], names=columns, index_col=0)

df["velocityFeetPerSecond"] = df["velocityMetersPerSecond"].apply(lambda x: x * 3.28084)
df["angularVelocityRadiansPerSec"] = df["angularVelocityDegreesPerSec"].apply(lambda x: x * 0.0174533)
df["positionFeet"] = df["positionMeters"].apply(lambda x: x * 3.28084)
time = df.index.max()
dist = df["positionFeet"].min()
counts = time / 0.02
print(f"Time: {time}, Distance: {dist}, Loop counts: {counts}")


# data = df["positionFeet"].values
# data = data.reshape(1, data.shape[0])
# dl = np.linalg.norm(np.diff(data), axis=0)
# dl = np.insert(dl, 0, 0, axis=0)
# l = np.cumsum(dl)
# ll = np.arange(start=0, stop=dist, step=dist / counts)
# print(l.shape, df["positionFeet"].values)
# xx = interp1d(l, data)
# spaced_x = xx(ll)
#
# xy = np.column_stack((ll, spaced_x))
# print(xy)
def interp1d_column(data: dict):
    ts = traces.TimeSeries(data)
    interpolated = ts.sample(
        sampling_period=timedelta(seconds=0.02),
        interpolate='linear',
    )
    return pd.DataFrame(interpolated, columns=["time", "interpolated data"])


time_index = pd.to_datetime(df.index, unit='s')
df.set_index(time_index, drop=True, inplace=True)
int_time_index = interp1d_column(df["positionFeet"].to_dict())["time"]
df1 = pd.DataFrame(columns=df.columns, index=int_time_index)
df1.reset_index(inplace=True, drop=True)
for col in df.columns:
    data = df[col].to_dict()
    temp = interp1d_column(data)["interpolated data"]
    df1[col] = temp
df1.to_csv("data.csv")
output = df1[["velocityFeetPerSecond", "angularVelocityRadiansPerSec"]]
output.to_csv("data.txt", header=None, index=None, sep=',', mode='w')
