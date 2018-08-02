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
IJ.run(imp, "Analyze Particles...", "size=500-1000 clear add")  # 17 particles
rm = RoiManager.getInstance()
if not rm:
	rm = RoiManager()

# output
outputDir = outputFile.getAbsolutePath()

# try to save the rois

numROIs = rm.getCount()

# method 1 array

indexList = range(numROIs)
print "my list is ",indexList
aROIs = array('i', indexList)
print "my array is ",aROIs
print "the type of my array variable is ",type(aROIs)

rm.setSelectedIndexes(aROIs) # try to fix bug of not saving Hoechst ROIs
selRois = rm.getSelectedIndexes()
print selRois, " are selected with an array"   # TODO: NOTE HERE!  last one is not selected

roisetName = "array_ROIs.zip"
#print "Saving " + str(len(roi_list)) + " ROIs to " + outputDir + str(os.sep) + roisetName
print "Saving " + str(numROIs) + " ROIs to " + outputDir + str(os.sep) + roisetName # TODO: it only saves the 1st ROI now!
rm.runCommand("save selected", os.path.join(outputDir, roisetName))  

# http://forum.imagej.net/t/jython-roi-manager-deletion-by-index/5013/6
# http://forum.imagej.net/t/select-rois-in-the-roi-manager-according-to-the-measured-data/908
# NOTE "save selected" is necessary. "Save" gives an array index out of bounds on last image in a set.


# method 2 enumeration
#for i, roi in enumerate(rm.getRoisAsArray()): # 0- based counting same as ROI indices
	#print i
	# rm.select(i) # selects only 1 roi
	#indexList = 
	#aROIs = array('i',
	#rm.setSelectedIndexes(selected)
	
#selRois = rm.getSelectedIndexes()
#print selRois, " are selected with enumeration"

#roisetName = "enum_ROIs.zip"
#print "Saving " + str(len(roi_list)) + " ROIs to " + outputDir + str(os.sep) + roisetName
#print "Saving " + str(numROIs) + " ROIs to " + outputDir + str(os.sep) + roisetName 
#rm.runCommand("save selected", os.path.join(outputDir, roisetName))  


