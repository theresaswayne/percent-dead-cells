#@File(label = "Input directory", style = "directory") inputFile
#@File(label = "Output directory", style = "directory") outputFile
#@ String  (label = "File extension", value=".czi") ext
#@double(label = "Typical nuclear long axis diameter, um", value = 15.0) nucDiam

# Note: Do not change or remove the first few lines! They provide essential parameters.

# percent_dead.py
# IJ Jython script by Theresa Swayne, 2018
# Written for Robert Hawley, Columbia University
# Given a set of CZI images from a multi-well plate, multiple positions per plate, 
#   counts nuclei in each of 2 channels: C1 (all cells) and C2 (dead cells)
# 	and reports the percentage of dead cells per image

# Input: A folder of images with name format: basename-Scene-XXX-PX-WW.czi
# Output: 
#	A CSV file with 1 row per image, containing the # nuclei in each channel and the % dead 
#	For each image, An ROIset containing detected nuclei in each channel

# Usage: Place all images in one folder.
#	Run the script.

# ---- Imports

from ij import IJ, WindowManager
from ij.gui import Roi, PolygonRoi, FreehandRoi, Line, ProfilePlot
from ij.plugin.frame import RoiManager
from ij.measure import Calibration, ResultsTable
import csv, os, sys, random, math
import datetime
import time
from loci.plugins import BF

# --- Helper functions

# helper function for ROI mgr
def get_roi_manager(new=False):
	""" flexible ROI mgr handling, copied from Particles_From_Mask.py template in Fiji
	if new = True, a new blank mgr is returned
	if new = False (default) and the ROI manager is open, returns that mgr.
	if new = False and the ROI manager is NOT open, creates a new one without throwing an error
	"""
	rm = RoiManager.getInstance()
	if not rm:
		rm = RoiManager()
	if new:
		rm.runCommand("Reset")
	return rm

# --- Function for walking through the folder
# based on IJ1 Process Folder template

def run():

	inputDir = inputFile.getAbsolutePath()
	outputDir = outputFile.getAbsolutePath()
	for root, directories, filenames in os.walk(inputDir):
		filenames.sort()
		for filename in filenames:
			print "Checking:",filename
			# Check for file extension
			if not filename.endswith(ext):
				continue
			process(inputDir, outputDir, filename)

# --- Function for processing each file
# based on IJ1 Process Folder template

def process(inputDir, outputDir, fileName):

	# open the image
	print "Processing:",fileName
	imps = BF.openImagePlus(os.path.join(inputDir, fileName)) # bio-formats opens an array
	imp = imps[0]

	# get image info
	imageName = imp.getTitle()
	wellName = imageName[-6:-4]
	posName = imageName[-8]
	print "This image comes from well "+wellName+" position "+posName
	imageCalib = imp.getCalibration()
	pixSize = imageCalib.pixelHeight # assuming in microns

	rm = get_roi_manager(new=True) # reset the ROI mgr

	
	# pre-processing
	IJ.run(imp, "Gaussian Blur...", "sigma=3 scaled stack"); # 3 micron radius

	# analysis

	# channel 1 Hoechst
	#TODO: select first channel
	IJ.run(imp, "Find Maxima...", "noise=5 output=[Point Selection]"); # more noise tol = selects fewer stray points
	rm.addRoi(imp.getRoi());
	C1RoiName = wellName+"-"+posName+"-C1"
	rm.rename(0, C1RoiName) # ROI indices start with 0
	rm.select(0)
	IJ.run(imp, "Measure", "") # one line per point
	rt = ResultsTable.getResultsTable()
	C1Count = rt.getCounter() # an integer
	C1Count = float(C1Count)
	rt.reset()
	
	# channel 2 Sytox
	#TODO: select second channel
	IJ.run(imp, "Find Maxima...", "noise=60 output=[Point Selection]");
	rm.addRoi(imp.getRoi());
	C2RoiName = wellName+"-"+posName+"-C2"
	rm.rename(1, C2RoiName)
	rm.select(1)
	IJ.run(imp, "Measure", "")
	C2Count = rt.getCounter()
	C2Count = float(C2Count)
	rt.reset()

	# save the ROIset
	print "Saving to", outputDir

	rm.runCommand("Show All")
	rm.runCommand("Show None")
	rm.deselect()
	roisetName = imageName + "_ROIs.zip"
	rm.runCommand("Save", os.path.join(outputDir, roisetName))

	# write data
	fracDead = C2Count/C1Count
	for j in range(1):
		print "Collecting row " + str(j)
		resultsRow = [imageName, wellName, posName, C1Count, C2Count, fracDead]
		csvWriter.writerow(resultsRow)
	
	# close image
	imp.close()

# ---- SETUP

# setup output file

# TODO: collect one of the filenames in script params

currTime = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
print "Current time is " + currTime
resultsName = currTime + "_Results.csv"
outputDir = outputFile.getAbsolutePath()
csvPath = os.path.join(outputDir, resultsName)
csvExists = os.path.exists(csvPath)
csvFile = open(csvPath, 'ab') # creates the file. a for append, b for binary (avoiding potential problems with ascii)
csvWriter = csv.writer(csvFile) # this object is able to write to the output file

# add headers to output file
if not csvExists: # avoids appending multiple headers
    headers = ['Filename','Well','Position','Hoechst Count','SYTOX Count','Fraction Dead']
    csvWriter.writerow(headers)
else:
    print "Appending to existing file."


# --- PROCESS THE FOLDER

run()

csvFile.close() # closes the output file so it can be used elsewhere

rm = get_roi_manager(new=True)

IJ.run("Clear Results")

print "Finished."

 