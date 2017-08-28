
from array import *
from math import exp, log
from ROOT import *
from rhapi import RhApi
API_URL = 'http://gem-machine-a:8113'
q = 'select c.part_serial_number, c.RNORM_MOHM, c.VMON_VLT from gem_omds.c1920 c'
api = RhApi(API_URL, debug = False)
data = api.json(q)
# print api.csv(q) # uncomment to debug

# initializes lists of parameters
list_RNORM_MOHM = []
list_VMON_VLT = []
# starts parsing json data
measurements = data['data']
measurementCount = 0
graphCount = 0
PART_SERIAL_NUMBER = '';
for m in measurements:
        # for each measurement
        measurementCount += 1
        old_PART_SERIAL_NUMBER = PART_SERIAL_NUMBER
        PART_SERIAL_NUMBER = m[0]
        list_RNORM_MOHM.append( m[1] )
        list_VMON_VLT.append( m[2] )
	# print m # uncomment to debug
        if (measurementCount > 1 and  list_VMON_VLT[len(list_VMON_VLT) - 1] <  list_VMON_VLT[len(list_VMON_VLT) - 2]):
                graphCount += 1
		# prints information on the analyzed data
		print graphCount, old_PART_SERIAL_NUMBER
		# if the measurement just read is from a new set of measurements
                # all elements in the lists represent a unique set of measurement, except for the last element
                # create graph
                c = TCanvas( 'c'+str(graphCount),'c'+ str(graphCount), 200, 10, 700, 500 )
                c.DrawFrame(0, 0.99, 6000, 1.004)
		c.SetGrid()
                # n is the number of points in the graph
                n = len(list_VMON_VLT) - 1
                x, y = array('d'), array('d')
                for i in range( n ):
                        x.append( list_VMON_VLT[i] )
                        y.append( list_RNORM_MOHM[i] )
                # -- DRAWS GRAPH 1 --
		gr = TGraph( n, x, y )
                gr.SetMarkerColor(kGreen-6)
                gr.SetMarkerStyle(20)
                gr.Draw("P")
                c.cd()
		# -- WRITES DESCRIPTION --
		description = TLatex()
		description.SetTextSize(0.03);
		description.SetTextAngle(0.0);
		description.DrawLatex(2200, 0.9885, "Applied Voltage (V)")
		description.SetTextAngle(90.0)	
		description.DrawLatex(-550, 0.994, "Normalized resistance (%)")
		# -- CREATES FINAL IMAGE --
		img = TImage.Create()
                img.FromPad(c)
                img.WriteImage('gQC4_second_' + str(graphCount) + '_' + old_PART_SERIAL_NUMBER.replace('/','-') + '.png')
                # updates the lists to only have the values of the last measurement
                list_RNORM_MOHM = [ m[1] ]
                list_VMON_VLT = [ m[2] ]
		c.Close()		

# prints information on analyzed data. This information is generated with negligible processing cost.
print 'data retrieved from '+str(measurementCount)+' measurements,'
print 'distributed in '+str(graphCount)+' sets.'
