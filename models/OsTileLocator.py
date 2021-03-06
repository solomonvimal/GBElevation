# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GBElevation
                                 A QGIS plugin
 Calculate elevation of points from 10m & 50m OS NTF files
                              -------------------
        begin                : 2017-10-19
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Luke Butler - Matrado Limited
        email                : luke@matrado.ca
 ***************************************************************************/
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import math
from qgis.core import QgsGeometry, QgsCoordinateReferenceSystem, QgsCoordinateTransform

class OsTileLocator:

    def __init__(self, featureGeometry, sourceCrs):
        self.featureGeometry = featureGeometry
        self.sourceCrs = sourceCrs
        self._setXYinCrs27700( featureGeometry, sourceCrs)
        self.grid = \
        [['V','W','X','Y','Z'], \
        ['Q','R','S','T','U'], \
        ['L','M','N','O','P'], \
        ['F','G','H','J','K'], \
        ['A','B','C','D','E']]

    def hundredKmSqTile(self):

        # False Origin of Grid 0,0 starts at Letter S
        # offset by 1,2 on grid lookup to start on this letter
        firstLetterX = math.trunc( self.x / 500000) + 2
        firstLetterY = math.trunc( self.y / 500000) + 1

        secondLetterX = math.trunc( (self.x % 500000) / 100000)
        secondLetterY = math.trunc( (self.y % 500000) / 100000)      

        firstLetter = self.grid[firstLetterY][firstLetterX]
        secondLetter = self.grid[secondLetterY][secondLetterX]

        return firstLetter + secondLetter


    def tenKmSqTile(self):

        firstNumber = math.trunc( (self.x % 100000) / 10000 )
        secondNumber = math.trunc( (self.y % 100000) / 10000 )

        tenKmSqTile = self.hundredKmSqTile() + str(firstNumber) + str(secondNumber)

        return tenKmSqTile

    def tenKmqlTileForNtfGrid(self):

        firstNumber = math.trunc( (self.x % 100000) / 20000 ) * 2
        secondNumber = math.trunc( (self.y % 100000) / 20000 ) * 2

        tenKmqlTileForNtfGrid = self.hundredKmSqTile() + str(firstNumber) + str(secondNumber)

        return tenKmqlTileForNtfGrid


    def fiveKmSqTile(self):

        if self.y % 10000 > 5000:
            NorthOrSouth = "N"
        else:
            NorthOrSouth = "S"

        if self.x % 10000 > 5000:
            WestOrEast = "E"
        else:
            WestOrEast = "W" 

        fiveKmSqTile = self.tenKmSqTile() + NorthOrSouth + WestOrEast

        return fiveKmSqTile


    def withinGB(self):
        if self.x >= 0 and self.x <=700000 and self.y >= 0 and self.y <=1300000:
            return True
        else:
            return False

    def _setXYinCrs27700( self, featureGeometry, sourceCrs ):
        if sourceCrs.authid() <> 'EPSG:27700':
            destCrs = QgsCoordinateReferenceSystem(27700)
            transformCrs = QgsCoordinateTransform(sourceCrs, destCrs)
            pointTransformed = transformCrs.transform(featureGeometry.asPoint())
        else:
            pointTransformed = featureGeometry.asPoint()

        self.x = pointTransformed.x()
        self.y = pointTransformed.y()
