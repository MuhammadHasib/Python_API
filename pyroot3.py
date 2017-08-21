from ROOT import *
from array import *
import os
import requests
from math import log
"""
out_file = TFile("myGraph.root", "RECREATE")
h = TH1F("my_histogram", "My Title;X;# of entries", 100, -5, 5)
h.FillRandom("gaus")
h.Write()
out_file.Close();
"""

from rhapi import RhApi
API_URL = 'http://gem-machine-a:8113'
q = 'select c.part_serial_number,c.IMON_UA, c.GAIN, c.GAIN_ERROR from gem_omds.c4260 c'
api = RhApi(API_URL, debug = False)
data = api.json(q)
#print data

# starts parsing json data
measurements = data['data']
#print measurements
for m in measurements:
	print m


"""

datas=os.system('python rhapi.py -u http://gem-machine-a:8113 "select c.part_serial_number,c.IMON_UA, c.GAIN, c.GAIN_ERROR from gem_omds.c4260 c" -s 1000 -f csv >csv_QC5_Gain_Imon.csv')
file = open("csv_QC5_Gain_Imon.csv")
next(file)
list_IMON_UA = []
list_GAIN = []
list_GAIN_ERROR = []

PART_SERIAL_NUMBER, IMON_UA, GAIN, GAIN_ERROR = next(file).split(',')
list_IMON_UA.append(float(IMON_UA))
list_GAIN.append(float(GAIN))
list_GAIN_ERROR.append(float(GAIN_ERROR))

graphCount = 0
for line in file:
	if len(line) > 1:
		old_PART_SERIAL_NUMBER = PART_SERIAL_NUMBER
		PART_SERIAL_NUMBER, IMON_UA, GAIN, GAIN_ERROR = line.split(',')
		list_IMON_UA.append(float(IMON_UA))
		list_GAIN.append(float(GAIN))
		list_GAIN_ERROR.append(float(GAIN_ERROR))
		GAIN = float(GAIN)
		GAIN_ERROR = float(GAIN_ERROR)
		if list_IMON_UA[len(list_IMON_UA) - 1] >  list_IMON_UA[len(list_IMON_UA) - 2]:
			# plot Graph
			# all elements in the lists represent a unique set of measurement, except for the last element
			graphCount = graphCount + 1
			c = TCanvas( 'c'+str(graphCount), 'A Simple Graph Example', 200, 10, 700, 500 )
			c.SetLogy();
			c.SetGrid()
			n = len(list_IMON_UA) - 1
			x, xErr, y, yErr, logY = array('d'), array('d'), array('d'), array('d'), array('d')
			for i in range( n ):
				x.append( list_IMON_UA[i] )
				xErr.append(0.0);
				y.append( list_GAIN[i] )
				yErr.append( list_GAIN_ERROR[i] )
				logY.append( log( list_GAIN[i] ) )
			gr = TGraphErrors( n, x, y, xErr, yErr )
			
			#calculates the Pearson's correlation coefficient of (x,log y) values.
                	#i.e.: r = sum((xi - x_mean)(logYi - logY_mean)) / sqrt(sum((xi - x_mean)^2)) / sqrt(sum((logYi - logY_mean)^2))
                	logGraph = TGraph(n, x, logY)
			gr.SetTitle( old_PART_SERIAL_NUMBER )
			gr.GetXaxis().SetTitle( 'monitored current' )
			gr.GetYaxis().SetTitle( 'gain (r = ' + str(logGraph.GetCorrelationFactor()) + ')' )
			gr.Draw("AP*")
			img = TImage.Create()
			img.FromPad(c)
			img.WriteImage('gQC5_Gain_Imon' + str(graphCount) + '_' + old_PART_SERIAL_NUMBER.replace('/','-') + '.png')
			list_IMON_UA = [float(IMON_UA)]
			list_GAIN = [float(GAIN)]
			list_GAIN_ERROR = [float(GAIN_ERROR)]
			print graphCount
		
""" 


