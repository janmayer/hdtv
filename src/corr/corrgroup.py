#!/usr/bin/python
import math

# Angle between two detectors
def alpha(d1, d2):
	def sin(x):
		return math.sin(x / 180.0 * math.pi)
	def cos(x):
		return math.cos(x / 180.0 * math.pi)
	def acos(x):
		return math.acos(x) * 180.0 / math.pi
	
	ca = sin(d1.theta)*sin(d2.theta)*cos(d1.phi - d2.phi) + cos(d1.theta)*cos(d2.theta)
	
	return acos(ca)

class Detector:
	def __init__(self, num, theta, phi):
		self.num = num
		self.theta = theta
		self.phi = phi
		
# The algorithm is based on the following two observations:
# 1.) In the angular function, only the cosine of the angles matters (*),
#      allowing us to shift all angles into the region [0., 180.] degrees
# 2.) We can flip the sign of any _two_ of the cosines
#
# We thus define the ``normalized form'' of an angle pair as follows:
# * theta_1 and theta_2 are in the region [0., 90.] degrees
# * If one of the thetas is equal to 90. degrees, we flip phi such
#    that it also is in the region [0., 90.] degrees
#
# (*) Note that cos(n*x) = T_n(cos(x)), where T_n are the Chebyshev
#   polynomials of the first kind
		
def norm_angle(x):
	x = x % 360.
	if x > 180.:
		x = 360. - x
		
	return x
		
def norm_key(theta_1, theta_2, phi):
	theta_1 = norm_angle(theta_1)
	theta_2 = norm_angle(theta_2)
	phi = norm_angle(phi)
	
	if theta_1 > 90.:
		if theta_2 > 90.:
			theta_1 = 180. - theta_1
			theta_2 = 180. - theta_2
			flip_phi = False
		else:
			theta_1 = 180. - theta_1
			flip_phi = True
	else:
		if theta_2 > 90.:
			theta_2 = 180. - theta_2
			flip_phi = True
		else:
			flip_phi = False
			
	if theta_1 == 90. or theta_2 == 90.:
		flip_phi = (phi > 90.)
		
	if flip_phi:
		phi = 180. - phi
	
	return (theta_1, theta_2, phi)
		
def main():		
	detectors = []
	detectors.append(Detector(6, 90.0, 0.0))
	detectors.append(Detector(7, 90.0, 55.0))
	detectors.append(Detector(8, 90.0, 125.0))
	detectors.append(Detector(9, 90.0, 180.0))
	detectors.append(Detector(10, 90.0, 235.0))
	detectors.append(Detector(11, 90.0, 305.0))
	detectors.append(Detector(12, 135.0, 270.0))
	detectors.append(Detector(13, 45.0, 270.0))
	detectors.append(Detector(14, 45.0, 90.0))
	detectors.append(Detector(15, 135.0, 90.0))

	corgroups = {}

	for i in range(0, len(detectors)):
		for j in range(0, len(detectors)):
			if i != j:
				t1 = detectors[i].theta
				t2 = detectors[j].theta
				phi = detectors[i].phi - detectors[j].phi
				key = norm_key(t1, t2, phi)
	
				if not key in corgroups.keys():
					corgroups[key] = []
				corgroups[key].append([detectors[i], detectors[j]])
				
	for key in corgroups.keys():
		print key, ':',
		for dets in corgroups[key]:
			print ("(%d %d)" % (dets[0].num-6, dets[1].num-6)),
		print ''

main()
