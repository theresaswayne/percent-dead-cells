#@ File (label = "Input directory", style = "directory") inputFile
#@ File (label = "Output directory", style = "directory") outputFile
#@ String  (label = "File extension", value=".czi") ext
#@ Double (label = "Typical nuclear long axis diameter, um", value = 15.0) nucDiam
#@ Double (label = "Noise tolerance value for Hoechst. Higher = more stringent", value = 200) noise
#@ Double (label = "Pixel value threshold for SYTOX Green", value = 0) thresholdGreen

# Note: Do not change or remove the first few lines! They provide essential parameters.

# percent_dead.py
# ImageJ Jython script by Theresa Swayne, 2018
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

# ---- IMPORTS

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


# ---- HELPER FUNCTIONS

def get_roi_manager(new=False):
	"""
	flexible ROI mgr handling, copied from Particles_From_Mask.py template in Fiji
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

def create_csv(basename):
	''' 
	function to set up an output file for results
	basename: string
	creates a csv file with the given basename plus a date-time stamp, and writes headers to the file
	returns the path to the file 
	'''
	currTime = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
	# print "Current time is " + currTime
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
	
	csvFile.close() # close file so it can be used later
	return csvPath


def get_basename(dirName, ext):
	'''
	function for finding the experiment name from a set of images
	takes a directory (path) and an extension (string)
	returns a string: basename of the first file in the directory that matches the extension
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


def parse_fileinfo(filename):
	'''
	function for getting well and position info from filename
	takes a filename from a Zeiss multiwell exported file
	name format: basename-Scene-XXX-PX-WW.czi
	returns a tuple of strings:
		basename (everything before "Scene")
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

	

def run():
	'''
	Function for walking through the folder
	based on IJ1 Process Folder template
	'''

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


def process(inputDir, outputDir, fileName, resultsWriter):
	'''
	Function for procesing each file
	based on IJ1 Process Folder template

	inputDir, outputDir: directories
	fileName: string form of a filename
	resultsWriter: a CSV writer for an open file
	'''
	
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

	# channel 1 Hoechst  # TODO: adapt to use same technique as SYTOX and spin off into a function
	imp.setC(1)
	# more noise tolerance = fewer stray points. tried: 50, 70 (about same)
	IJ.run(imp, "Find Maxima...", "noise="+str(noise)+" output=[Point Selection]"); # more noise tol = selects fewer stray points

	roi = imp.getRoi()
	if roi is None: # there are no Hoechst maxima found
		C1Count = 0

	else:
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

	print str(C1Count) + " Hoechst-labeled cells found."


	if C1Count == 0: # no Hoechst, no cells, percent dead is undefined
		# write 0 in Hoechst column
		# write "" in sytox column and percent dead column -- note excel should not include these cells in average. R will not (use na.rm?)
		C2Count = ""
		fracDead = ""
		resultsRow = [imageName[:-4], wellName, posName, C1Count, C2Count, fracDead]
		print "Results: " + " ".join(map(str, resultsRow))
		resultsWriter.writerow(resultsRow)

	else:
		
		# channel 2 Sytox
		imp.setC(2)
		
		# ---- API findMaxima WITH THRESHOLD AND SINGLE POINTS 
		# findMaxima(ImageProcessor ip, double tolerance, double threshold, int outputType, boolean excludeOnEdges, boolean isEDM)
		# source: https://github.com/imagej/ImageJA/blob/8e283502055d25b9f0456f4aad95afa30a649d45/src/main/java/ij/plugin/filter/MaximumFinder.java
		# note LIST produces list of coords, SINGLE POINTS produces a bunch of points that are shown by the code below.
		# POINT_SELECTION is supposed to give just that but can't figure out how to get it in the manager
		# https://stackoverflow.com/questions/26526269/image-analysis-finding-proteins-in-an-image
		# https://github.com/bgruening/galaxytools/blob/18b441b263846cece9c5527cab0de66a54ecba3a/tools/image_processing/imagej2/imagej2_find_maxima/jython_script.py
		
		ip = imp.getProcessor()
		mf = MaximumFinder()
		# tried: 60 (too many dim nuclei), 100 (better but still too many), 200 (best)
		# with sytox we want only the brightest cells
		maxima = mf.findMaxima(ip, 100.0, thresholdGreen, MaximumFinder.SINGLE_POINTS, False, False)
		
		findmaximashow = ImagePlus("Found Maxima", maxima)
		findmaximashow.show() # an image of all the points
		maximaip = findmaximashow.getProcessor()
		maximahist = maximaip.getHistogram()
		C2Count = maximahist[255]
		print "Using the findMaxima method with a threshold of " + str(thresholdGreen) + ", I found "+ str(C2Count) + " maxima."
		
		if C2Count != 0:
			IJ.setRawThreshold(findmaximashow, 255, 255, "red")
			IJ.run(findmaximashow, "Create Selection", "")
			rm.addRoi(findmaximashow.getRoi())
			C2RoiName = wellName+"-"+posName+"-C2"
			rm.rename(1, C2RoiName)
	
		
		# save ROIs and data
	
		# pythonically select all rois
		roi_list = rm.getRoisAsArray()
		for roi in roi_list:
			rm.select(rm.getRoiIndex(roi))
	
		roisetName = imageName[:-4] + "_ROIs.zip"
		print "Saving " + str(len(roi_list)) + " ROIs to " + outputDir + str(os.sep) + roisetName
	
		# NOTE "save selected" is necessary. "Save" gives an array index out of bounds on last image in a set.
		rm.runCommand("save selected", os.path.join(outputDir, roisetName))  
	
		fracDead = C2Count/C1Count 
		resultsRow = [imageName[:-4], wellName, posName, C1Count, C2Count, fracDead]
		print "Results: " + " ".join(map(str, resultsRow))
		resultsWriter.writerow(resultsRow)

		# close maxima image
		findmaximashow.close()

	
	# close images
	imp.close()



# ---- ACTUALLY PROCESS THE FOLDER

run()

# clean up
rm = get_roi_manager(new=True)
IJ.run("Clear Results")
print "Finished."
 