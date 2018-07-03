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
# 	NOTE: They must all be part of one experiment (same base name).
#	Run the script.

# ---- Imports

from ij import IJ, WindowManager
from ij.gui import Roi, PolygonRoi, FreehandRoi, Line, ProfilePlot
from ij.plugin.frame import RoiManager
from ij.measure import Calibration, ResultsTable
import csv
import os, sys, random, math
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

# Function for setting up output file

def create_csv(basename):
	''' 
		takes a string
		returns a path to a csv file with the given basename plus a date-time stamp
	'''
	currTime = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
	print "Current time is " + currTime
	resultsName = basename + "_"+currTime + "_Results.csv"
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
	
	csvFile.close()
	return csvPath

# function for pulling basename from directory

def get_basename(dirName, ext):

	'''
	takes a directory (path) and an extension (string)
	returns a string: basename of the first file (in the directory) that matches the extension
	'''

	inputDir = dirName.getAbsolutePath() # this is needed and I'm not sure why

	for root, directories, filenames in os.walk(inputDir):
		filenames.sort()
		for filename in filenames:
			print "Checking:",filename
			# Check for file extension
			if not filename.endswith(ext):
				continue
	
			fileWithExt = os.path.basename(filename)
			#print "The filename is " + str(fileWithExt)

			fileName = os.path.splitext(fileWithExt)[0]
			#print "The file name without extension is " + str(fileName) 
	
			base = fileName.split("Scene")[0] # should yield 2 components. 2nd contains scene, pos, well
			base = base[:-1] # strip trailing hyphen
			#print "The base image name is " + base 

			return base # loop terminates after the first run

# getting well and position info from filename
# assumes name format: basename-Scene-XXX-PX[X]-RC[C].czi
# basename = everything before "Scene"

def parse_fileinfo(filename):

	'''
	takes a filename from a Zeiss multiwell exported file
	name format: basename-Scene-XXX-PX-WW.czi
	returns a tuple of strings:
		basename
		well number
		position number within the well
	'''

	fileWithExt = os.path.basename(filename)
	fileWithoutExt = os.path.splitext(fileWithExt)[0]
	#print "The filename is " + str(fileWithExt)
	#print "The file name without extension is " + str(fileWithoutExt) 

	base,info = fileWithoutExt.split("Scene") # should yield 2 components. 2nd contains scene, pos, well
	base = base[:-1] # strip trailing hyphen
	#print "The base image name is " + str(base) 

	posInfo = info.split("-")
	# format -scene-pos-well.ext ... first item in list is empty

	scene = posInfo[1] # not returned
	pos = posInfo[2]
	well = posInfo[3]
	
	result = (base, well, pos) # string tuple
	return result
	
# --- Function for walking through the folder
# based on IJ1 Process Folder template

def run():

	inputDir = inputFile.getAbsolutePath()
	outputDir = outputFile.getAbsolutePath()

	# get base filename
	basename = get_basename(inputFile, ext) # don't have to use the abs path because I do it in the function

	# create results file using basename
	resultsPath = create_csv(basename)
	resultsFile = open(resultsPath, 'ab') # open the csv
	resultsWriter = csv.writer(resultsFile) # create a writer object

	for root, directories, filenames in os.walk(inputDir):
		filenames.sort()
		for filename in filenames:
			print "Checking:",filename
			# Check for file extension
			if not filename.endswith(ext):
				continue
			process(inputDir, outputDir, filename, resultsWriter)

	resultsFile.close() # close the csv
	

# --- Function for processing each file
# based on IJ1 Process Folder template

def process(inputDir, outputDir, fileName, resultsWriter):
	
	# open the image
	print "Processing:",fileName
	if ext != ".tif":
		imps = BF.openImagePlus(os.path.join(inputDir, fileName)) # bio-formats opens an array
		imp = imps[0]
	else:
		imp = IJ.openImage(os.path.join(inputDir, fileName)) # regular IJ opens a single image
		

	# get image info
	imageName = imp.getTitle()
	imageInfo = parse_fileinfo(fileName)
	
	wellName = imageInfo[1]
	posName = imageInfo[2]
	print "This image comes from well "+wellName+" position "+posName
	imageCalib = imp.getCalibration()
	pixSize = imageCalib.pixelHeight # assuming in microns
	# print "The pixel size is "+str(pixSize) # 1.29 for 10x Zeiss

	rm = get_roi_manager(new=True) # reset the ROI mgr

	
	# pre-processing
	bkgdRadius = int(nucDiam*pixSize*5) # radius should be considerably larger than nuclei. for d=15um, radius = 96
	IJ.run(imp, "Subtract Background...", "rolling="+str(bkgdRadius)+" stack");
	
	sigma = int(nucDiam/4)  # blurring radius should be smaller than nuclei. for d=15um, sigma = 3
	IJ.run(imp, "Gaussian Blur...", "sigma="+str(sigma)+" scaled stack"); # sigma is the radius, in microns

	# TODO: check for low S/N or other criteria to tell if severely out of focus
	  
	# analysis

	# channel 1 Hoechst
	imp.setC(1)
	# more noise tolerance = fewer stray points. tried: 50, 70 (about same)
	IJ.run(imp, "Find Maxima...", "noise=200 output=[Point Selection]"); # more noise tol = selects fewer stray points
	rm.addRoi(imp.getRoi());
	C1RoiName = wellName+"-"+posName+"-C1"
	rm.rename(0, C1RoiName) # ROI indices start with 0
	rm.select(0)
	IJ.run(imp, "Measure", "") # one line per point
	rt = ResultsTable.getResultsTable()
	C1Count = rt.getCounter() # an integer
	C1Count = float(C1Count)
	rm.deselect()
	rt.reset()
	
	# channel 2 Sytox
	imp.setC(2)
	
	# TODO: add threshold to this step
	
	# tried: 60 (too many dim nuclei), 100 (better but still too many)
	IJ.run(imp, "Find Maxima...", "noise=200 output=[Point Selection]"); # with sytox we want only the brightest cells
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
		resultsRow = [imageName[:-4], wellName, posName, C1Count, C2Count, fracDead]
		resultsWriter.writerow(resultsRow)
	
	# close image
	imp.close()



# --- ACTUALLY PROCESS THE FOLDER

run()

# clean up
rm = get_roi_manager(new=True)
IJ.run("Clear Results")
print "Finished."
 