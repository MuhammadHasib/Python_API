
from array import *
from math import exp, log
from ROOT import *
from rhapi import RhApi
API_URL = 'http://gem-machine-a:8113'
#q = 'select c.part_serial_number, c.IMON_UA, c.VMON_VLT, c.RATE_HZ, c.ERR_RATE_HZ from gem_omds.c1920 c'
q = 'select c.CHMBR_SER_NUMBR,c.RUN_TYPE,c.RUN_NUMBER,c.IMON_UA,c.VMON_VLT,c.RATE_HZ,c.ERR_RATE_HZ from gem_omds.gem_chmbr_qc6_hvtest_v c'
api = RhApi(API_URL, debug = False)
data = api.json(q)
print api.csv(q) # uncomment to debug
#print data

# initializes lists of parameters
list_IMON_UA = []
list_VMON_VLT = []
list_RATE_HZ = []
list_ERR_RATE_HZ = []
# starts parsing json data
measurements = data['data']
#print measurements
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
	old_RUN_TYPE =  RUN_TYPE
	PART_SERIAL_NUMBER = m[0]
	RUN_TYPE = m[1]
	RUN_NUMBER = m[2]
	list_IMON_UA.append( m[3] )
	list_VMON_VLT.append( m[4] )
	list_RATE_HZ.append( m[5] * 200.0 )
	list_ERR_RATE_HZ.append( m[6] * 200.0 )
	# print m # uncomment to debug
	if (measurementCount > 1 and  (old_RUN_NUMBER != RUN_NUMBER or old_PART_SERIAL_NUMBER != PART_SERIAL_NUMBER)):
		graphCount += 1
		# prints information on the analyzed data
		#print graphCount, old_PART_SERIAL_NUMBER, old_RUN_NUMBER
		# if the measurement just read is from a new set of measurements
		# all elements in the lists represent a unique set of measurement, except for the last element
		# create graph
		c = TCanvas( 'c'+str(graphCount),str(old_PART_SERIAL_NUMBER), 200, 10, 700, 500 )
		c.DrawFrame(0, 0, 1000, 6000)
		#c.SetGrid()
		# n is the number of points in the graph
		n = len(list_IMON_UA)
		print n
		x, y, y2, y2err, zeros = array('d'), array('d'), array('d'), array('d'), array('d')
		for i in range( n ):
			x.append( list_IMON_UA[i] )
			y.append( list_VMON_VLT[i] )
			y2.append( list_RATE_HZ[i] )
			y2err.append( list_ERR_RATE_HZ[i] )
			zeros.append( 0.0 )
			# -- DRAWS GRAPH 1 --
		gr = TGraph( n, x, y )
		gr.SetTitle( 'IV Curve' )
		gr.SetMarkerColor(kGreen-6)
		gr.SetMarkerStyle(20)
		gr.Draw("P")
		c.cd()
		# -- DRAWS GRAPH 2 --
		gr2 = TGraphErrors( n, x, y2, zeros, y2err )
		gr2.SetTitle( 'Rate' )
		gr2.SetMarkerColor(kAzure-7)
		gr2.SetMarkerStyle(20)
		gr2.Draw("P")
		c.cd()
		# -- FITS IV CURVE IN LINEAR MODEL --
		f = TF1("f", "[0] * x + [1]")
		f.SetLineStyle(3)
		f.SetLineWidth(3)
		f.SetLineColor(kGreen-6)
		r = gr.Fit(f, "S")
		# -- DRAWS LEGEND --
		legend = TLegend(0.3, 0.7,0.1,0.9)
		legend.AddEntry(gr,"","P")
		legend.AddEntry(gr2,"","P")
		legend.AddEntry("r", "Linear (IV Curve)", "l")
		blank = TGraph(n, x, x)
		blank.SetMarkerColor(kWhite)
		legend.AddEntry(blank,"V = "+str(round(r.Parameter(1), 4))+"i + "+str(round(r.Parameter(0), 4)), "p")
		legend.AddEntry(blank,"R ="+str(round(gr.GetCorrelationFactor(), 5)), "p")
		legend.Draw()
		# -- DRAWS AXIS --
		rightAxis =  TGaxis(1000,0,1000,6000,0,30,50510,"+L")
		rightAxis.SetLabelSize(0.03)
		rightAxis.SetTitleSize(0.02)
		rightAxis.Draw()
		# -- WRITES DESCRIPTION --
		description = TLatex()
		description.SetTextSize(0.03);
		description.SetTextAngle(0.0);
		description.DrawLatex(380, -600, "Current Drawn (#muA)")
		description.DrawLatex(380, 6500, old_PART_SERIAL_NUMBER)
		description.SetTextAngle(90.0)	
		description.DrawLatex(-100, 2100, "Applied Voltage (V)")
		description.DrawLatex(1070, 2600, "Rate (Hz)")
		# -- CREATES FINAL IMAGE --
		img = TImage.Create()
		img.FromPad(c)
		img.WriteImage('gQC6_' + str(graphCount) + '_' + old_PART_SERIAL_NUMBER.replace('/','-') + '.png')
		# updates the lists to only have the values of the last measurement
		list_IMON_UA = [ m[3] ]
		list_VMON_VLT = [ m[4] ]
		list_RATE_HZ = [ m[5] * 200.0 ]
		list_ERR_RATE_HZ = [ m[6] * 200.0]
		c.Close()		

# prints information on analyzed data. This information is generated with negligible processing cost.
print 'data retrieved from '+str(measurementCount)+' measurements,'
print 'distributed in '+str(graphCount)+' sets.'

