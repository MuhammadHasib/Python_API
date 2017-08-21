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
q = 'select c.part_serial_number,c.IMON_UA, c.GAIN, c.GAIN_ERROR from gem_omds.c4260 c'
api = RhApi(API_URL, debug = False)
data = api.json(q)


# initializes lists of parameters
list_IMON_UA = []
list_GAIN = []
list_GAIN_ERROR = []
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
	list_IMON_UA.append( m[1] )
	list_GAIN.append( m[2] )
	list_GAIN_ERROR.append( m[3] )
	if (measurementCount > 0 and  list_IMON_UA[len(list_IMON_UA) - 1] >  list_IMON_UA[len(list_IMON_UA) - 2]):
		# if the measurement just read is from a new set of measurements
		# all elements in the lists represent a unique set of measurement, except for the last element
		graphCount += 1
		# create graph
		#c = TCanvas( 'c'+str(graphCount), 'canvas name', 200, 10, 700, 500 )
		c = TCanvas( 'c', 'c', 200, 10, 700, 500 )
		# in this particular case we use a mono-log graph
		c.SetLogy()
		c.SetGrid()
		# n is the number of point in the graph
		n = len(list_IMON_UA) - 1
		x, xErr, y, yErr, logY = array('d'), array('d'), array('d'), array('d'), array('d')
		for i in range( n ):
			x.append( list_IMON_UA[i] )
			xErr.append(0.0);
			y.append( list_GAIN[i] )
			yErr.append( list_GAIN_ERROR[i] )
			logY.append( log( list_GAIN[i] ) )
		gr = TGraphErrors( n, x, y, xErr, yErr )
		# calculates the Pearson's correlation coefficient of (x,log y) values.
                # i.e.: r = sum((xi - x_mean)(logYi - logY_mean)) / sqrt(sum((xi - x_mean)^2)) / sqrt(sum((logYi - logY_mean)^2))
                logGraph = TGraph(n, x, logY)
		gr.SetTitle( old_PART_SERIAL_NUMBER )
		gr.GetXaxis().SetTitle( 'Divider current (uA)' )
		gr.GetYaxis().SetTitle( 'gain (r = ' + str(logGraph.GetCorrelationFactor()) + ')' )
		gr.Draw("AP*")
		c.DrawFrame(500, 10, 750, 1000000)

		img = TImage.Create()
		img.FromPad(c)
		img.WriteImage('gQC5_Gain_Imon' + str(graphCount) + '_' + old_PART_SERIAL_NUMBER.replace('/','-') + '.png')
		# updates the lists to only have the values of the last measurement
		list_IMON_UA = [ m[1] ]
		list_GAIN = [ m[2] ]
		list_GAIN_ERROR = [ m[3] ]

# prints information on analyzed data. This information is generated with negligible processing cost.
print 'data retrieved from '+str(measurementCount)+' measurements,'
print 'distributed in '+str(graphCount)+' sets.'


