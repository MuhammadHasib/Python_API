
from array import *
from math import exp, log
from ROOT import *
from rhapi import RhApi
API_URL = 'http://gem-machine-a:8113'
#q = 'select c.part_serial_number,c.IMON_UA, c.GAIN, c.GAIN_ERROR from gem_omds.c4260 c'
q = 'select c.part_serial_number, c.incrmnt_sec, c.AMB_PRSR_MBAR, c.MANF_PRSR_MBAR, c.TEMP_DEGC from gem_omds.c1840 c'
#q = 'select * from gem_omds.gem_chmbr_qc4_hvtest_v  c'
api = RhApi(API_URL, debug = False)
data = api.json(q)
# print api.csv(q) # uncomment to debug

#print data
# initializes lists of parameters

list_incrmnt_sec = []
list_AMB_PRSR_MBAR = []
list_MANF_PRSR_MBAR = []
list_TEMP_DEGC = []
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
        list_incrmnt_sec.append( m[1] )
        list_AMB_PRSR_MBAR.append( 35.0 / 100.0 * (m[2] - 900.0) )
	list_MANF_PRSR_MBAR.append( m[3] )
	list_TEMP_DEGC.append( m[4] )
	# print m # uncomment to debug
        if (measurementCount > 1 and  list_incrmnt_sec[len(list_incrmnt_sec) - 1] <  list_incrmnt_sec[len(list_incrmnt_sec) - 2]):
                graphCount += 1
		# prints information on the analyzed data
		print graphCount, old_PART_SERIAL_NUMBER
		# if the measurement just read is from a new set of measurements
                # all elements in the lists represent a unique set of measurement, except for the last element
                # create graph
                c = TCanvas( 'c'+str(graphCount),'c'+ str(graphCount), 200, 10, 700, 500 )
                c.DrawFrame(0, 0, 3500, 35)
		c.SetGrid()
                # n is the number of points in the graph
                n = len(list_incrmnt_sec) - 1
                x, y, y2, y3 = array('d'), array('d'), array('d'), array('d')
                for i in range( n ):
                        x.append( list_incrmnt_sec[i] )
                        y.append( list_AMB_PRSR_MBAR[i] )
			y2.append( list_MANF_PRSR_MBAR[i] )
			y3.append( list_TEMP_DEGC[i] )
                # -- DRAWS GRAPH 1 --
		gr = TGraph( n, x, y )
                gr.SetTitle( 'Atm Pressure (mBar)' )
                gr.SetMarkerColor(kGray+1)
                gr.SetMarkerStyle(20)
		gr.GetXaxis().SetTitle( 'time' )
                gr.GetYaxis().SetTitle( 'ambient pressure'  )
                gr.Draw("LP")
                c.cd()
		# -- DRAWS GRAPH 2 --
		gr2 = TGraph (n, x, y2)
		gr2.SetTitle( 'Pressure (mBar)' )
		gr2.SetMarkerColor(kAzure+9)
		gr2.SetMarkerStyle(20)
		gr2.Draw("LP")
		c.cd()
		# -- DRAWS GRAPH 3 --
		gr3 = TGraph (n, x, y3)
		gr3.SetTitle( 'Temperature (C)' )
		gr3.SetMarkerColor(kOrange+7)
		gr3.SetMarkerStyle(20)
		gr3.Draw("LP")
		# -- FITS PRESSURE INTO EXPONENCIAL MODEL --
  		f = TF1("f", "[1] * exp(x * [0])")
		f.SetLineStyle(1)
		f.SetLineWidth(1)
		f.SetLineColor(kAzure+9)
		r = gr2.Fit(f, "S")
		# -- DRAWS LEGEND --
		legend = TLegend(0.3, 0.3)
		legend.AddEntry(gr2,"","LP")
		legend.AddEntry(gr3,"","LP")
		legend.AddEntry(gr,"","LP")
		legend.AddEntry("r", "Expon. (Pressure (mBar))", "l")
		blank = TGraph(n, x, x)
		blank.SetMarkerColor(kWhite)
		legend.AddEntry(blank,"p = "+str(round(r.Parameter(1), 3))+" e^{"+str(round(r.Parameter(0), 6))+" t}", "p")
		legend.AddEntry(blank,"#chi^{2} ="+str(round(r.Chi2(), 5)), "p")
		legend.Draw()
		# -- DRAWS AXIS --
		rightAxis =  TGaxis(3500,0,3500,35,900,1000,50510,"+L")
                rightAxis.SetLabelSize(0.03)
                rightAxis.SetTitleSize(0.02)
                rightAxis.Draw()
		# -- WRITES DESCRIPTION --
		description = TLatex()
		description.SetTextSize(0.03);
		description.SetTextAngle(0.0);
		description.DrawLatex(1700, -3, "Time (s)")
		description.SetTextAngle(90.0)	
		description.DrawLatex(-250, 10.7, "Internal pressure (mBar)")
		description.DrawLatex(-150, 12.8, "Temperature (C)")
		description.DrawLatex(3800, 11.5, "Atm pressure (mBar)")
		# -- CREATES FINAL IMAGE --
		img = TImage.Create()
                img.FromPad(c)
                img.WriteImage('gQC3_' + str(graphCount) + '_' + old_PART_SERIAL_NUMBER.replace('/','-') + '.png')
                # updates the lists to only have the values of the last measurement
                list_incrmnt_sec = [ m[1] ]
                list_AMB_PRSR_MBAR = [ 35.0 / 100.0 * (m[2] - 900.0) ]
		list_MANF_PRSR_MBAR = [ m[3] ]
		list_TEMP_DEGC = [ m[4] ]
		c.Close()		

# prints information on analyzed data. This information is generated with negligible processing cost.
print 'data retrieved from '+str(measurementCount)+' measurements,'
print 'distributed in '+str(graphCount)+' sets.'
