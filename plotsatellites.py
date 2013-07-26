# coding=utf-8
import os,sys,time,optparse
from numpy import loadtxt,sin,cos, random,log10,pi,array,arange
from matplotlib.patches import Ellipse
TWOPI = 2.0*pi
PIon2 = pi*0.5


DEBUG=False
planets={}
planets['earth']={'a':1,'r1':6378.1,'r2':6356.8,'dens':5.515,'mag':2.3,'albedo':0.367, 'color':'#6666FF'}
planets['mars']={'a':1.5,'r1':3396.2,'r2':3376.2,'dens':3.9335,'mag':2.3,'albedo':0.17, 'color':'#cc0000'         }
planets['jupiter']={'a':5.2,'r1':71492,'r2':66854,'dens':1.326,'mag':2.3,'albedo':0.343, 'color':"#FF9900"}
planets['saturn']={'a':9.5,'r1':60268,'r2':54364,'dens':0.687,'mag':1.1,'albedo':0.47, 'color':'#FFCC00'}
planets['uranus']={'a':19.6,'r1':25559,'r2':24973,'dens':1.27,'mag':5.6,'albedo':0.51, 'color':'#000099'}
planets['neptune']={'a':30.1,'r1':24764 ,'r2':24341 ,'dens':1.638 ,'mag': 7.91,'albedo':0.41, 'color':'#0099FF'}
planets['pluto']={'a':39.264 ,'r1':1153,'r2':1153,'dens':2.03,'mag':15,'albedo':0.59, 'color':'#003333'}

HEXDIG = '0123456789abcdefABCDEF'
HEXDEC = {v: int(v, 16) for v in (x+y for x in HEXDIG for y in HEXDIG)}

def rgb(rgbt):
    return (HEXDEC[rgbt[0:2]]/256., HEXDEC[rgbt[2:4]]/256., HEXDEC[rgbt[4:6]]/256.)



class satellite:
    def  __init__(self,name,host,line):
        self.name=name
        self.host=host.lower()
        self.hosta=planets[self.host]['a']
        self.attributes=['GM', 'GMerr', 'radius', 'raderr', 'dens', 'denserr', 'mag', 'magerr', 'albedo', 'alberr']
        self.readsatelliteline(line)
        self.color = rgb(planets[self.host]['color'].replace('#',''))
        self.a=300.0
        self.period=0.
        self.theta=0.0

    def printsat(self):
        print "Satellite: ",self.name,
        print " d: ",self.a, "period: ",self.period,
        print " gm: ",self.GM, "+/-", self.GMerr
        print " \t\tradius: ",self.radius, "+/-", self.raderr,
        print " density: ",self.dens, "+/-", self.denserr
        print " \t\tmagnitude: ",self.mag, "+/-", self.magerr,
        print " albedo: ",self.albedo, "+/-", self.alberr

    def printsystem(self,host):
        if self.host == host:
            print "\t",
            self.printsat()

    def plotsat(self, ax, t,size='radius'):
        if self.period == 0:
            return 
        import pylab as pl
        import matplotlib.animation as animation

        dt=t/self.period
        dt*=TWOPI
        theta = self.theta+dt
        theta = theta%TWOPI

        if self.a > 0:
            dx =0.000001*self.a*abs(sin(theta))
            y = 0.000001*self.a*abs(cos(theta))
        else:
            return#dx,y=0.05,0.05
        if theta>pi: dx *=-1
        if theta>PIon2 and theta < 3*PIon2: y *=-1
        if 'earth' in self.host:
            ax.text(self.hosta-0.2,-9, self.host, fontsize=12, rotation='vertical', verticalalignment='bottom', horizontalalignment='center', color=self.color)
        elif 'mars' in self.host:
            ax.text(self.hosta+0.2,-9, self.host, fontsize=12, rotation='vertical', verticalalignment='bottom', horizontalalignment='center', color=self.color)
        elif 'pluto' in self.host:
            ax.text(self.hosta+0.2,-9, "("+self.host+")", fontsize=12, rotation='vertical', verticalalignment='bottom', horizontalalignment='center', color=self.color)
        else:
            ax.text(self.hosta,-9, self.host, fontsize=12, rotation='vertical', verticalalignment='bottom', horizontalalignment='center', color=self.color)
        ax.scatter(self.hosta,0, facecolor='none',edgecolor='k', s=0.1*(0.5*(planets[self.host]['r1']+planets[self.host]['r2'])), alpha = 0.1)

        if size=='radius':
            ax.plot(self.hosta+dx, y,'o',markersize=log10(self.radius)*10,markerfacecolor=self.color,alpha=(26.0-self.mag)/26)
            ax.plot([self.hosta, self.hosta+dx], [0,y], 'k-',alpha=0.1)
        elif size=='ratio':
            ax.plot(self.hosta+dx, y,'o',markersize=self.sizeratio*100,markerfacecolor=self.color,alpha=(26.0-self.mag)/26)
            ax.plot([self.hosta, self.hosta+dx], [0,y], 'k-',alpha=0.1)
            
    def readsatelliteline(self,line):
        line=line.split()
        if not (self.name in line[0].lower()):
            print "error: name not consistent with line!", self.name, line[0].lower()
        attind=1            
#line must contain: GM(km3/sec2) [±] [err] [ref] Meanradius(km) [±] [err] [ref] Meandensity(g/cm3)	MagnitudeV0/R [±] [err] [ref] 	GeometricAlbedo [±] [err] [ref] 

#gm
        self.GM=float(line[attind])
        attind+=1
        if line[attind].startswith('±'):
            attind+=1
            self.GMerr=float(line[attind])
            attind+=1
        else:
            self.GMerr=0.0            
        if line[attind].startswith("["):
            attind+=1
#radius
        self.radius=float(line[attind])
        attind+=1
        if line[attind].startswith('±'):
            attind+=1
            self.raderr=float(line[attind])
            attind+=1    
        else:
            self.raderr=0.0            
        if line[attind].startswith("["):
            attind+=1
#density
        self.dens=float(line[attind])
        attind+=1
        if line[attind].startswith('±'):
            attind+=1
            self.denserr=float(line[attind])
            attind+=1
        else:
            self.denserr=0.0                
        if line[attind].startswith("["):
            attind+=1
#magnitude
        try: 
            self.mag=float(line[attind].replace('R',''))
            attind+=1
            if line[attind].startswith('±'):
                attind+=1
                self.magerr=float(line[attind])
                attind+=1
            else:
                self.magerr=0.0                
            if line[attind].startswith("["):
                attind+=1
#albedo
            self.albedo=float(line[attind])
            attind+=1
            try:
                if line[attind].startswith('±'):
                    attind+=1
                    self.alberr=float(line[attind])
                    attind+=1    
                else:
                    self.alberr=0.0            
                if line[attind].startswith("["):
                    attind+=1
            except IndexError: 
                self.albedo=0.0
                self.alberr=0.0
                pass
        except ValueError:
            self.mag=0.0
            self.albedo=0.0
            self.magerr=0.0
            self.alberr=0.0
        self.hostr=(planets[self.host]['r1']+planets[self.host]['r2'])*0.5
        self.sizeratio=self.radius/self.hostr
            

                
if __name__=='__main__':

    parser = optparse.OptionParser(usage="python plotsatellites.py  ", conflict_handler="resolve")
    parser.add_option('-d','--days', default=1000, type="float",
                      help='days for the timeline of the visualization')
    parser.add_option('-t','--steps', default=5, type="float",
                      help='step (in days) for the timeline of the visualization')
    parser.add_option('-i','--interactive', default=False ,action="store_true" ,
                      help='show plots as they are made') 

    parser.add_option('-p','--printall', default=False ,action="store_true" ,
                      help='prints systems characteristics') 
    parser.add_option('-e','--earth', default=False ,action="store_true" ,
                      help='prints earth system characteristics')
    parser.add_option('-m','--mars', default=False, action="store_true" ,
                      help='prints mars system characteristics')
    parser.add_option('-j','--jupiter', default=False, action="store_true" ,
                      help='prints jupiter system characteristics')
    parser.add_option('-s','--saturn', default=False ,action="store_true" ,
                      help='prints saturn system characteristics')
    parser.add_option('-n','--neptune', default=False ,action="store_true" ,
                      help='prints neptune system characteristics')
    parser.add_option('-l','--pluto', default=False, action="store_true" ,
                      help='prints pluto system characteristics')
    parser.add_option('--debug', default=False, action="store_true" ,
                      help='debug statements are printed')

    options,  args = parser.parse_args()


    if len(args)!=0 :
        sys.argv.append('--help')    
        options,  args = parser.parse_args()
        sys.exit(0)
    
    DEBUG = options.debug

    timescale = options.days
    timestep = options.steps
    filein = "satellitelist"
    filein2= "satellitelist2"
    if DEBUG: 
        print "timescale : ",timescale,"days"
        print "timestep  : ",timestep,"days"
        print "inputfiles :", filein, filein2

    allplanets={"Martian":'mars',"Earth's":'earth',"Jovian":'jupiter',"Saturnian":'saturn',"Uranian":"uranus","Neptunian":"neptune","Pluto's":'pluto'}

    
    sats={}
            
    f=open(filein,"r")
    f.readline()

    for l in f:
        if l.startswith('#'):
            host=allplanets[l.split()[0].replace('#','')]
            continue
        name=l.split()[0].lower()
        sats[name]=satellite(name,host,l)
            
    f=open(filein2)
    for l in f:
        l=l.strip().split()
        if l:
            host=l[-1].lower()
            name=l[1].lower()
            if name in sats.keys():
                if not host == sats[name].host:
                    if DEBUG:
                        print "host and satellite pair wrong: ",name,host, "is not :",sats[name].name,sats[name].host
                    continue
                attind = 3
                if l[attind].startswith("±"):
                    attind =5
                sats[name].a=float(l[attind].replace(',',''))
                sats[name].period=float(l[attind+1].replace(',',''))

    for host in allplanets.itervalues():
        if options.printall or DEBUG:
            print "Host: ",host, "a: ",planets[host]['a'],"(AU) mean radius: ",(planets[host]['r1']+planets[host]['r2'])*0.5,
            print "dens: ",planets[host]['dens'], "mag: ",planets[host]['mag'], "albedo: ",planets[host]['albedo']
            for s in sats.iterkeys():
                sats[s].printsystem(host)
        elif options.earth and host == 'earth':
                print "host: ",host, "a: ",planets[host]['a'],"r: ",(planets[host]['r1']+planets[host]['r2'])*0.5,
                print "dens: ",planets[host]['dens'], "mag: ",planets[host]['mag'], "albedo: ",planets[host]['albedo']  
                for s in sats.iterkeys():
                    sats[s].printsystem(host)

        elif options.mars and host == 'mars':
                print "host: ",host, "a: ",planets[host]['a'],"r: ",(planets[host]['r1']+planets[host]['r2'])*0.5,
                print "dens: ",planets[host]['dens'], "mag: ",planets[host]['mag'], "albedo: ",planets[host]['albedo']  
                for s in sats.iterkeys():
                    sats[s].printsystem(host)
        elif options.jupiter and host == 'jupiter':
                print "host: ",host, "a: ",planets[host]['a'],"r: ",(planets[host]['r1']+planets[host]['r2'])*0.5,
                print "dens: ",planets[host]['dens'], "mag: ",planets[host]['mag'], "albedo: ",planets[host]['albedo']  
                for s in sats.iterkeys():
                    sats[s].printsystem(host)
        elif options.saturn and host == 'saturn':
                print "host: ",host, "a: ",planets[host]['a'],"r: ",(planets[host]['r1']+planets[host]['r2'])*0.5,
                print "dens: ",planets[host]['dens'], "mag: ",planets[host]['mag'], "albedo: ",planets[host]['albedo']  
                for s in sats.iterkeys():
                    sats[s].printsystem(host)
        elif options.neptune and host == 'neptune':
                print "host: ",host, "a: ",planets[host]['a'],"r: ",(planets[host]['r1']+planets[host]['r2'])*0.5,
                print "dens: ",planets[host]['dens'], "mag: ",planets[host]['mag'], "albedo: ",planets[host]['albedo']  
                for s in sats.iterkeys():
                    sats[s].printsystem(host)
        elif options.pluto and host == 'pluto':
                print "host: ",host, "a: ",planets[host]['a'],"r: ",(planets[host]['r1']+planets[host]['r2'])*0.5,
                print "dens: ",planets[host]['dens'], "mag: ",planets[host]['mag'], "albedo: ",planets[host]['albedo']  
                for s in sats.iterkeys():
                    sats[s].printsystem(host)


    import pylab as pl
    if options.interactive:
        pl.ion()

    for s in sats.iterkeys():
        sats[s].theta=random.uniform(0,TWOPI)

    fig = pl.figure()
    for t in arange(0,timescale, timestep):
        print "plotting day ",t
        if DEBUG:
            print "plotting day ",t
#        if not options.interactive:
#            fig = pl.figure()
        pl.clf()

        ax1 = fig.add_subplot(211)
        pl.xlabel (" ")
        pl.ylabel (" ")
        ax2 = fig.add_subplot(212)
        pl.xlabel ("host semimajos axis (AU)")
        pl.ylabel (" ")
        
        
        ax1.set_xlim(-25, 55)
        ax2.set_xlim(-25, 55)
        ax1.set_ylim(-10,10)
        ax2.set_ylim(-10,10)
        ax1.text(20,8, "satellite radius (arbitrary units)")
        ax2.text(25,8, "satellite-host size ratio")
        ax1.text(45,-8, "t = %03d days"%t,fontsize = 8,horizontalalignment='left')
        ax2.text(45,-8, "t = %03d days"%t,fontsize = 8,horizontalalignment='left')

        ax1.yaxis.set_visible(False) 
        ax2.yaxis.set_visible(False) 

        for s in sats.iterkeys():        
            sats[s].plotsat(ax1, t,size='radius')
            sats[s].plotsat(ax2, t,size='ratio')

        if options.interactive:
            pl.draw()
        else:
            pl.savefig("satellites.%04d.png"%t)
    if not options.interactive:
        os.system("convert -loop -1 satellites.????.png satellites.gif")
        os.system("rm satellites.????.png")

#    pl.show()
#    time.sleep(10)
