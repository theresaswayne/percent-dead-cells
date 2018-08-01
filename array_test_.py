#@ File (label = "Output directory", style = "directory") outputFile
#@ Double (label = "Typical nuclear long axis diameter, um", value = 15.0) nucDiam

# array test

from ij import IJ, WindowManager, ImagePlus
from ij.gui import Roi, PolygonRoi, FreehandRoi, Line, ProfilePlot
from ij.plugin.frame import RoiManager
from ij.measure import Calibration, ResultsTable
import csv
import os, sys, random, math
import datetime
import time
from loci.plugins import BF
from ij.process import ImageProcessor
from ij.plugin.filter import MaximumFinder
from array import array


# generate test data

# image
imp = IJ.openImage("http://imagej.nih.gov/ij/images/blobs.gif")

#ROIs
IJ.run(imp, "Make Binary", "")
IJ.run(imp, "Analyze Particles...", "clear add")  # 64 particles
rm = RoiManager.getInstance()
if not rm:
	rm = RoiManager()

# output
outputDir = outputFile.getAbsolutePath()

# try to save the rois

numROIs = rm.getCount()
indexList = range(numROIs)[:-1]
print "my list is ",indexList

aROIs = array('i', indexList)
print "my array is ",aROIs
print "the type of my array variable is ",type(aROIs)

rm.setSelectedIndexes(aROIs) # try to fix bug of not saving Hoechst ROIs
selRois = rm.getSelectedIndexes()
print selRois, " are selected"   # TODO: NOTE HERE!  last one is not selected

roisetName = "_ROIs.zip"
#print "Saving " + str(len(roi_list)) + " ROIs to " + outputDir + str(os.sep) + roisetName
print "Saving " + str(numROIs) + " ROIs to " + outputDir + str(os.sep) + roisetName # TODO: it only saves the 1st ROI now!

# http://forum.imagej.net/t/jython-roi-manager-deletion-by-index/5013/6
# http://forum.imagej.net/t/select-rois-in-the-roi-manager-according-to-the-measured-data/908
# NOTE "save selected" is necessary. "Save" gives an array index out of bounds on last image in a set.

rm.runCommand("save selected", os.path.join(outputDir, roisetName))  

# for i, roi in enumerate(rm.getRoisAsArray()): #TODO NOTE TRY THIS

# Select only FreeLine/FreeHand ROIs
#if roi.type == Roi.FREELINE:

#	fp = roi.getInterpolatedPolygon()
#	fp = roi.getInterpolatedPolygon(fp.getLength(False) / points_density, smooth)
#	newRoi = PolygonRoi(fp, Roi.POLYLINE)
#	newRois.append(newRoi)

#	# Delete old ROI
#	rm.select(i)
#	rm.runCommand("Delete")
	
#numROIs = 5
#indexList = range(numROIs)[:-1]
aROIs = array('i', indexList)


