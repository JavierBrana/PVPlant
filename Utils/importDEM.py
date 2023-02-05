# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Javier Braña <javier.branagutierrez@gmail.com>  *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

def getFile():
    from PySide import QtGui
    filters = "Esri ASC (*.asc);;CSV (*.csv);;All files (*.*)"
    return QtGui.QFileDialog.getOpenFileName(None, "Open DEM,","",filters)[0]


def openEsri(filename):
    grid_space = 1
    file = open(filename, "r")
    templist = [line.split() for line in file.readlines()]
    file.close()
    del file

    # Read meta data:
    meta = templist[0:6]
    nx = int(meta[0][1])                        # NCOLS
    ny = int(meta[1][1])                        # NROWS
    xllref = meta[2][0]                         # XLLCENTER / XLLCORNER
    xllvalue = round(float(meta[2][1]), 3)
    yllref = meta[3][0]                         # YLLCENTER / XLLCORNER
    yllvalue = round(float(meta[3][1]), 3)
    cellsize = round(float(meta[4][1]), 3)      # CELLSIZE
    nodata_value = float(meta[5][1])            # NODATA_VALUE

    # set coarse_factor
    coarse_factor = max(round(grid_space / cellsize), 1)

    # Get z values
    templist = templist[6:(6 + ny)]
    templist = [templist[i][0::coarse_factor] for i in np.arange(0, len(templist), coarse_factor)]
    datavals = np.array(templist).astype(float)
    del templist

    # create xy coordinates: Coordenada X-Y del origen (por el centro o la esquina inferior
    # izquierda de la celda)
    if xllref.upper() == "XLLCENTER":
        xllvalue = xllvalue - cellsize * nx / 2.0
    if yllref.upper() == "YLLCENTER":
        yllvalue = yllvalue - cellsize * ny / 2.0
    x = 1000 * (cellsize * np.arange(nx)[0::coarse_factor] + xllvalue)
    y = 1000 * (cellsize * np.arange(ny)[-1::-1][0::coarse_factor] + yllvalue)
    z = 1000 * datavals

    return x, y, z, cellsize, nodata_value


def openCSV(filename, delim = ','):
    import csv
    pts = list()
    with open(filename, newline='\n') as csvfile:
        reader = csv.reader(csvfile, delimiter = delim)
        for row in reader:
            pts.append(FreeCAD.Vector(float(row[1]), float(row[2]), float(row[3])))

    return pts


def interpolatePoints(points, cellsize = 2.0):
    import numpy as np
    import scipy as sp
    import scipy.interpolate

    pts = list()
    x = list()
    y = list()
    z = list()
    for point in points:
        x.append(point.x)
        y.append(point.y)
        z.append(point.z)

    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    spline = sp.interpolate.Rbf(x, y, z, function='thin-plate')
    xtotalsteps = int((max(x) - min(x)) / cellsize)
    #ytotalsteps = int((max(y) - min(y)) / cellsize)
    xi = np.linspace(min(x), max(x), xtotalsteps)
    step = 100
    ini = min(y)
    while ini < max(y):
        end = min(ini + (step - 1) * cellsize, max(y))
        yi = np.linspace(ini, end, step)
        ini = end + cellsize
        X, Y = np.meshgrid(xi, yi)
        Z = spline(X, Y)
        xx = X.flatten()
        yy = Y.flatten()
        zz = Z.flatten()
        for i, point in enumerate(xx):
            pts.append(FreeCAD.Vector(xx[i], yy[i], zz[i]) * 1000)

    return pts