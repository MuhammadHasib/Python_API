"""
from ROOT import *
from array import *
import os
import requests
from math import log

out_file = TFile("myGraph.root", "RECREATE")
h = TH1F("my_histogram", "My Title;X;# of entries", 100, -5, 5)
h.FillRandom("gaus")
h.Write()
out_file.Close();
"""

from array import *
from math import log
from ROOT import *
from rhapi import RhApi
API_URL = 'http://gem-machine-a:8113'
#q = 'select c.part_serial_number, c.IMON_UA, c.GAIN, c.GAIN_ERROR, c.RATE_HZ, c.RATE_ERROR_HZ from gem_omds.c4260 c'
#q = 'select * from gem_omds.gem_chmbr_qc5_effgain_v c'
api = RhApi(API_URL, debug = False)
print api.csv(q)
data = api.json(q)


# initializes lists of parameters
list_IMON_UA = []
list_GAIN = []
list_GAIN_ERROR = []
list_RATE_HZ = []
list_RATE_ERROR_HZ = []
# starts parsing json data
measurements = data['data']
measurementCount = 0
graphCount = 0
PART_SERIAL_NUMBER = '';
RUN_NUMBER = '';
RUN_TYPE = '';
for m in measurements:
	# for each measurement
	measurementCount += 1
	old_PART_SERIAL_NUMBER = PART_SERIAL_NUMBER
	old_RUN_NUMBER = RUN_NUMBER
	old_RUN_TYPE = RUN_TYPE
	PART_SERIAL_NUMBER = m[0]
	RUN_TYPE = m[2]
	RUN_NUMBER = m[3]
	list_IMON_UA.append( m[8] )
	list_GAIN.append( m[15] )
	list_GAIN_ERROR.append( m[16] )
	list_RATE_HZ.append( m[11] )
	list_RATE_ERROR_HZ.append( m [12] )
	#if (measurementCount > 0 and  list_IMON_UA[len(list_IMON_UA) - 1] >  list_IMON_UA[len(list_IMON_UA) - 2]):
	if (measurementCount > 1 and  old_RUN_NUMBER != RUN_NUMBER):
		# if the measurement just read is from a new set of measurements
		# all elements in the lists represent a unique set of measurement, except for the last element
		graphCount += 1
		print graphCount, old_PART_SERIAL_NUMBER, old_RUN_NUMBER
		# create graph
		c = TCanvas( 'c'+str(graphCount), 'Gain Uniformity', 200, 10, 700, 500 )
		#c = TCanvas( 'c', 'c', 200, 10, 700, 500 )
		c.DrawFrame(500, 9.999, 750, 1000000)
		# in this particular case we use a mono-log graph
		c.SetLogy()
		c.SetGrid()
		# n is the number of point in the graph
		n = len(list_IMON_UA) -1
		#print (n)
		x, xErr, y, yErr, logY, y2, y2Err = array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d')
		for i in range( n ):
			x.append( list_IMON_UA[i] )
			xErr.append(0.0);
			y.append( list_GAIN[i] )
			yErr.append( list_GAIN_ERROR[i] )
			logY.append( log( list_GAIN[i] ) )
			y2.append( list_RATE_HZ[i] )
			y2Err.append( list_RATE_ERROR_HZ[i] )
		gr = TGraphErrors( n, x, y, xErr, yErr )
		# calculates the Pearson's correlation coefficient of (x,log y) values.
                # i.e.: r = sum((xi - x_mean)(logYi - logY_mean)) / sqrt(sum((xi - x_mean)^2)) / sqrt(sum((logYi - logY_mean)^2))
                logGraph = TGraph(n, x, logY)
		gr.SetTitle( old_PART_SERIAL_NUMBER )
		gr.SetMarkerColor(kAzure+9)
		gr.SetMarkerStyle(20)
		gr.GetXaxis().SetTitle( 'Divider current (uA)' )
		gr.GetYaxis().SetTitle( 'gain (r = ' + str(logGraph.GetCorrelationFactor()) + ')' )
		#gr.GetXaxis().SetRange(450, 750)
		gr.Draw("P")

		gr2 = TGraphErrors( n, x, y2, xErr, y2Err)
		gr2.SetMarkerColor(kOrange+1)
		gr2.SetMarkerStyle(20)
		gr2.Draw("P")

 		#draw axis on the right side of the pad
 		rightAxis =  TGaxis(750,10,750,1000000,0,4000,50510,"+L")
  		rightAxis.SetLabelSize(0.03)
		rightAxis.SetTitleSize(0.02)
		rightAxis.Draw()

		img = TImage.Create()
		img.FromPad(c)
		img.WriteImage('gQC5_Gain_Imon' + str(graphCount) + '_' + old_PART_SERIAL_NUMBER.replace('/','-') + '.png')
		# updates the lists to only have the values of the last measurement
		list_IMON_UA = [ m[8] ]
		list_GAIN = [ m[15] ]
		list_GAIN_ERROR = [ m[16] ]

# prints information on analyzed data. This information is generated with negligible processing cost.
print 'data retrieved from '+str(measurementCount)+' measurements,'
print 'distributed in '+str(graphCount)+' sets.'

