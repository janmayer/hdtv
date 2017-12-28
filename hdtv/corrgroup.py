# -*- coding: utf-8 -*-

class Detector(object):
    """
    Class describing a single detector. Theta and phi are angles
    (FIXME), name is an arbitrary Python object used to identify
    the detector.
    """

    def __init__(self, name, theta, phi):
        self.fName = name
        self.fTheta = theta
        self.fPhi = phi


class CorrelationGroup(object):
    """
    Class describing a correlation group, i.e. a number of detector
    pairs with the same value of the correlation function.
    """

    def __init__(self, theta1, theta2, phi, detpairs):
        self.fTheta1 = theta1
        self.fTheta2 = theta2
        self.fPhi = phi
        self.fDetectorPairs = detpairs

    def IsSymmetric(self):
        """
        Tests whether the correlation group is symmetric, i.e.
        remains unchanged if all the detector pairs are
        transposed.
        """
        # We simply test if the correlation group *should* be
        # symmetric, not if it actually is.
        return (self.fTheta1 == self.fTheta2)

    def GetPairs(self):
        """
        Returns a list of lists of Detector objects describing all
        detector pairs in the correlation group.
        """
        return self.fDetectorPairs


class CorrelationGroups(object):
    """
    Class for determining all correlation groups that arise from a
    given arrangement of detectors.
    """

    def __init__(self):
        self.fGroups = None
        self.fDetectors = list()

    def AddDetector(self, num, theta, phi):
        """
        Add a detector. Note that fCorrelGroups will not reflect the
        change until CalcGroups has been called.
        """
        self.fDetectors.append(Detector(num, theta, phi))

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
    #
    # Literature reference: L. Peter Ekström and Anders Nordlund,
    # Gamma-gamma correlations with detector arrays,
    # NIM A313 (1992) 421-428

    def NormAngle(self, x):
        "Internal use only."
        # Calculate an angle x_prime in the range [0, 180] such
        # that cos(x_prime) = cos(x)
        x = x % 360.
        if x > 180.:
            x = 360. - x

        return x

    def NormKey(self, theta1, theta2, phi):
        "Internal use only."
        # Calculate the normalized form, as defined above, of an
        # (theta1, theta2, phi) pair
        theta1 = self.NormAngle(theta1)
        theta2 = self.NormAngle(theta2)
        phi = self.NormAngle(phi)

        if theta1 > 90.:
            if theta2 > 90.:
                theta1 = 180. - theta1
                theta2 = 180. - theta2
                flipPhi = False
            else:
                theta1 = 180. - theta1
                flipPhi = True
        else:
            if theta2 > 90.:
                theta2 = 180. - theta2
                flipPhi = True
            else:
                flipPhi = False

        if theta1 == 90. or theta2 == 90.:
            flipPhi = (phi > 90.)

        if flipPhi:
            phi = 180. - phi

        return (theta1, theta2, phi)

    def CalcGroups(self):
        """
        Update fCorrelGroups to contain a list of all correlation
        groups possible with the current set of detectors.
        """
        corgroups = dict()

        for i in range(0, len(self.fDetectors)):
            for j in range(0, len(self.fDetectors)):
                if i != j:
                    t1 = self.fDetectors[i].fTheta
                    t2 = self.fDetectors[j].fTheta
                    phi = self.fDetectors[i].fPhi - self.fDetectors[j].fPhi
                    key = self.NormKey(t1, t2, phi)

                    if key not in list(corgroups.keys()):
                        corgroups[key] = []
                    corgroups[key].append(
                        [self.fDetectors[i], self.fDetectors[j]])

        self.fGroups = list()
        for (k, v) in corgroups.items():
            self.fGroups.append(CorrelationGroup(k[0], k[1], k[2], v))
