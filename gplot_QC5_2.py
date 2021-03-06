
from array import *
from math import exp, log
from ROOT import *
from rhapi import RhApi
API_URL = 'http://gem-machine-a:8113'
q = 'select c.part_serial_number, c.VDRIFT_VLT, c.GAIN, c.GAIN_ERROR, c.RATE_HZ, c.RATE_ERROR_HZ from gem_omds.c4260 c'
api = RhApi(API_URL, debug = False)
print (api.csv(q))
data = api.json(q)

# initializes lists of parameters
list_VDRIFT_VLT = []
list_GAIN = []
list_GAIN_ERROR = []
list_RATE_HZ = []
list_RATE_ERROR_HZ = []
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
	list_VDRIFT_VLT.append( m[1] )
	list_GAIN.append( m[2] )
	list_GAIN_ERROR.append( m[3] )
	list_RATE_HZ.append( m[4] )
	list_RATE_ERROR_HZ.append( m [5] )
	if (measurementCount > 0 and  list_VDRIFT_VLT[len(list_VDRIFT_VLT) - 1] >  list_VDRIFT_VLT[len(list_VDRIFT_VLT) - 2]):
		# if the measurement just read is from a new set of measurements
		# all elements in the lists represent a unique set of measurement, except for the last element
		graphCount += 1
		# create graph
		c = TCanvas( 'c'+str(graphCount), 'Gain Uniformity', 200, 10, 700, 500 )
		#c = TCanvas( 'c', 'c', 200, 10, 700, 500 )
		c.DrawFrame(2299, 9.999, 3501, 1000000)
		# in this particular case we use a mono-log graph
		c.SetLogy()
		c.SetGrid()
		# n is the number of point in the graph
		n = len(list_VDRIFT_VLT) - 1
		x, xErr, y, yErr, logY, y2, y2Err = array('d'), array('d'), array('d'), array('d'), array('d'), array('d'), array('d')
		
		for i in range( n ):
			x.append( list_VDRIFT_VLT[i] )
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
                legend = TLegend(0.3, 0.3)
                legend.AddEntry(gr,"","P")
                legend.AddEntry(gr2,"","P")
                legend.AddEntry("r", "Expon. (Gain)", "l")
                blank = TGraph(n, x, x)
                blank.SetMarkerColor(kWhite)
                legend.AddEntry(blank,"y = "+str(round(r.Parameter(0), 8))+" e^{"+str(round(r.Parameter(1), 4))+"x}", "p")
                legend.AddEntry(blank,"R^{2} ="+str(round(logGraph.GetCorrelationFactor() * logGraph.GetCorrelationFactor(), 5)), "p")
                legend.Draw()
		# -- DRAWS AXIS --
 		rightAxis =  TGaxis(3500,10,3500,1000000,0,4000,50510,"+L")
  		rightAxis.SetLabelSize(0.03)
		rightAxis.SetTitleSize(0.02)
		rightAxis.Draw()
		# -- WRITES DESCRIPTION --
                description = TLatex()
                description.SetTextSize(0.05);
                description.SetTextAngle(0.0);
                description.DrawLatex(2700, 3, "Drift Voltage (V)")
                description.SetTextAngle(90.0)
                description.DrawLatex(2230, 400, "Effective Gain")
                description.DrawLatex(3630, 800, "Rate (Hz)")
		# -- CREATES FINAL IMAGE --
		img = TImage.Create()
		img.FromPad(c)
		img.WriteImage('gQC5_second_' + str(graphCount) + '_' + old_PART_SERIAL_NUMBER.replace('/','-') + '.png')
		# updates the lists to only have the values of the last measurement
                list_VDRIFT_VLT  = [ m[1] ]
                list_GAIN = [ m[2] ]
                list_GAIN_ERROR = [ m[3] ]
                list_RATE_HZ = [ m[4] ]
                list_RATE_ERROR_HZ = [m[5] ]

# prints information on analyzed data. This information is generated with negligible processing cost.
print 'data retrieved from '+str(measurementCount)+' measurements,'
print 'distributed in '+str(graphCount)+' sets.'

