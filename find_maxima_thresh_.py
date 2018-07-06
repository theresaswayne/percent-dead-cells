# find_maxima_thresh.py
# testing ways to "find maxima" with a threshold and return an ROI showing positions

# tolerance =     /** maximum height difference between points that are not counted as separate maxima */


# ---- IMPORTS

from ij import IJ, WindowManager, ImagePlus
from ij.gui import Roi, PolygonRoi, FreehandRoi, Line, ProfilePlot
from ij.plugin.frame import RoiManager
from ij.measure import Calibration, ResultsTable
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


# open a test image
imp = IJ.openImage("http://imagej.nih.gov/ij/images/blobs.gif")
imp.show()
rm = get_roi_manager(new=True)


ip = imp.getProcessor()
mf = MaximumFinder()


# findMaxima(ImageProcessor ip, double tolerance, double threshold, int outputType, boolean excludeOnEdges, boolean isEDM)
# source: https://github.com/imagej/ImageJA/blob/8e283502055d25b9f0456f4aad95afa30a649d45/src/main/java/ij/plugin/filter/MaximumFinder.java

maxima = mf.findMaxima(ip, 100.0, 240.0, MaximumFinder.SINGLE_POINTS, False, False)

# note LIST produces list of coors, SINGLE POINTS produces a bunch of points that are shown by the code below.
# POINT_SELECTION is supposed to give just that but can't figure out how to get it in the manager

findmaximashow = ImagePlus("Found Maxima", maxima)
findmaximashow.show() #an image of all the points


#CountWithThresh = rt.getCounter()
#CountWithThresh = float(CountNoThresh)
#rt.reset()
#postReset = rt.getCounter()
#print "After resetting there are " + str(postReset) + " results"

#imp.show()
CountWithThresh = 777


# https://stackoverflow.com/questions/26526269/image-analysis-finding-proteins-in-an-image

# https://github.com/bgruening/galaxytools/blob/18b441b263846cece9c5527cab0de66a54ecba3a/tools/image_processing/imagej2/imagej2_find_maxima/jython_script.py




# add points from getMaxima (or list?) to the results table

#rt = ResultsTable()

#for i in range(maxima.npoints):
#    rt.incrementCounter()
#    rt.addValue("X", maxima.xpoints[i])
#    rt.addValue("Y", maxima.ypoints[i])

#rt.show("Results")



# Menu-based find maxima command

IJ.run(imp, "Find Maxima...", "noise=100 output=[Point Selection] light")
rm.addRoi(imp.getRoi());
rm.rename(0, "Maxima without threshold")
rm.select(0)
IJ.run(imp, "Measure", "")
rt = ResultsTable.getResultsTable()
CountNoThresh = rt.getCounter()
CountNoThresh = float(CountNoThresh)
rt.reset()
IJ.run("Select None")



# Report results

print "Without a threshold, I found "+ str(CountNoThresh) + " maxima."
print "With a threshold, I found " + str(CountWithThresh) + " maxima."

# TODO: as alternative, check out HMaxima transform from landini, basically subtracting the threshold before running the find maxima