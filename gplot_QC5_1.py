
from array import *
from math import exp, log
from ROOT import *
from rhapi import RhApi
API_URL = 'http://gem-machine-a:8113'
#q = 'select c.part_serial_number, c.IMON_UA, c.GAIN, c.GAIN_ERROR, c.RATE_HZ, c.RATE_ERROR_HZ from gem_omds.c4260 c'
q = 'select c.CHMBR_SER_NUMBR, c.RUN_TYPE, c.RUN_NUMBER, c.IMON_UA, c.GAIN, c.GAIN_ERROR, c.RATE_HZ, c.RATE_ERROR_HZ from gem_omds.gem_chmbr_qc5_effgain_v c'
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
	old_RUN_TYPE = RUN_TYPE
	old_RUN_NUMBER = RUN_NUMBER
	PART_SERIAL_NUMBER = m[0]
	RUN_TYPE = m[1]
	RUN_NUMBER = m[2]
	list_IMON_UA.append( m[3] )
	list_GAIN.append( m[4] )
	list_GAIN_ERROR.append( m[5] )
	list_RATE_HZ.append( m[6] )
	list_RATE_ERROR_HZ.append( m [7] )
	#if (measurementCount > 1 and  list_IMON_UA[len(list_IMON_UA) - 1] >  list_IMON_UA[len(list_IMON_UA) - 2]):
	if (measurementCount > 1 and  (old_RUN_NUMBER != RUN_NUMBER or old_PART_SERIAL_NUMBER != PART_SERIAL_NUMBER)):
		# if the measurement just read is from a new set of measurements
		# all elements in the lists represent a unique set of measurement, except for the last element
		graphCount += 1
		# create graph
		c = TCanvas( 'c'+str(graphCount), 'Gain Uniformity', 200, 10, 700, 500 )
		#c = TCanvas( 'c', 'c', 200, 10, 700, 500 )
		c.DrawFrame(500, 9.999, 750, 1000000)
		# in this particular case we use a mono-log graph
		c.SetLogy()
		c.SetGrid()
		# n is the number of point in the graph
		n = len(list_IMON_UA) 
		x, xErr, y, yErr, logY, y2, y2Err = array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d')
		
		for i in range( n ):
			x.append( list_IMON_UA[i] )
			xErr.append(0.0);
			y.append( list_GAIN[i] )
			yErr.append( list_GAIN_ERROR[i] )
			logY.append( log( list_GAIN[i] ) )
			y2.append(10.0 ** (1.0 + list_RATE_HZ[i] / 800.0))
			y2Err.append( list_RATE_ERROR_HZ[i] )
		# -- Draws graph 1 --
		gr = TGraphErrors( n, x, y, xErr, yErr )
		# calculates the Pearson's correlation coefficient of (x,log y) values.
		# i.e.: r = sum((xi - x_mean)(logYi - logY_mean)) / sqrt(sum((xi - x_mean)^2)) / sqrt(sum((logYi - logY_mean)^2))
		logGraph = TGraph(n, x, logY)
		gr.SetTitle( 'Gain' )
		gr.SetMarkerColor(kAzure+9)
		gr.SetMarkerStyle(20)
		gr.Draw("P")
		c.cd()
		# -- Draws graph 2 --
		gr2 = TGraph( n, x, y2)
		gr2.SetTitle( 'Rate' )
		gr2.SetMarkerColor(kOrange+1)
		gr2.SetMarkerStyle(20)
		gr2.Draw("P")
		c.cd()
 		# -- FITS GAIN IN EXPONENCIAL MODEL --
		f = TF1("f", "[0] * exp (x * [1])")
		f.SetLineStyle(1)
		f.SetLineWidth(1)
		f.SetLineColor(kBlack)
		r = gr.Fit(f, "S")
		c.cd()
		# -- DRAWS LEGEND --
		legend = TLegend(0.3, 0.7,0.1,0.9)
		legend.AddEntry(gr,"","P")
		legend.AddEntry(gr2,"","P")
		legend.AddEntry("r", "Expon. (Gain)", "l")
		blank = TGraph(n, x, x)
		blank.SetMarkerColor(kWhite)
		legend.AddEntry(blank,"y = "+str(round(r.Parameter(0), 8))+" e^{"+str(round(r.Parameter(1), 4))+"x}", "p")
		legend.AddEntry(blank,"R^{2} ="+str(round(logGraph.GetCorrelationFactor() * logGraph.GetCorrelationFactor(), 5)), "p")
		legend.Draw()
		# -- DRAWS AXIS --
		rightAxis =  TGaxis(750,10,750,1000000,0,4000,50510,"+L")
		rightAxis.SetLabelSize(0.03)
		rightAxis.SetTitleSize(0.02)
		rightAxis.Draw()
		# -- WRITES DESCRIPTION --
		description = TLatex()
		description.SetTextSize(0.05);
		description.SetTextAngle(0.0);
		description.DrawLatex(580, 3, "Divider current (#muA)")
		description.DrawLatex(580, 1002000, old_PART_SERIAL_NUMBER)
		description.SetTextAngle(90.0)
		description.DrawLatex(480, 400, "Effective Gain")
		description.DrawLatex(775, 800, "Rate (Hz)")
		# -- CREATES FINAL IMAGE --
		img = TImage.Create()
		img.FromPad(c)
		img.WriteImage('gQC5_' + str(graphCount) + '_' + old_PART_SERIAL_NUMBER.replace('/','-') + '.png')
		# updates the lists to only have the values of the last measurement
		list_IMON_UA = [ m[3] ]
		list_GAIN = [ m[4] ]
		list_GAIN_ERROR = [ m[5] ]
		list_RATE_HZ = [ m[6] ]
		list_RATE_ERROR_HZ = [m[7] ]

# prints information on analyzed data. This information is generated with negligible processing cost.
print 'data retrieved from '+str(measurementCount)+' measurements,'
print 'distributed in '+str(graphCount)+' sets.'

