satellitesizes
==============

simple python code for the visualization of solar system satellites sizes and satellite-planet size ratios


this code creates a simple visualization of solar system satellites to get a feeling for their size, as an ensamble, 
and of the size ratio to their parent planet. 

it reads two files: satelliteslist and satellitelist2, containing satellite information 
from jpl (http://ssd.jpl.nasa.gov/?sat_phys_par)
and wikipedia (http://en.wikipedia.org/wiki/List_of_natural_satellites). both list have been minimally parsed for readability.

the animation shows:

each planet as an empty black circle. the size of the circle is proportional to the mean radius of the planet, 
the depth of the circle color is proportional to the number of satellites

each family is plotted in a different color: a differnt color identifies a different host. the color is similar to the planet true color

the distance of each satellite to the host is proportional to the semimajor axis

the intensity of the satellite color is proportional to the magnitude (V or R whichever available) of the satellite

the size of the satellite:

1) in the top plot it is proportional to the physical radius of the satellite
2) in the bottom plot it is proportional to the ratio of the radius of the satellite to the radius of its host planet  

the rotation rotational speed is proportional to the actual rotational speed of the satellite, assuming a circular orbit

the initial angular position of the satellites is however randomely chosen


