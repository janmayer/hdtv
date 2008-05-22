#include <iostream>
#include <math.h>
#include <gsl/gsl_sf_coupling.h>
#include <gsl/gsl_sf_legendre.h>

// References:
// [KSW73]: K. S. Krane, R. M. Steffen and R. M. Wheeler,
//          Directionals Correlations of Gamma Radiations Emitted from Nuclear
//          States Oriented by Nuclear Reactions or Cryogenic Methods,
//          Nuclear Data Tables, 11, 351-406 (1973)
//
// [SA75]:  R. M. Steffen and K. Alder,
//          Angular Distribution and Correlation of Gamma Rays,
//          in: W. D. Hamilton (Ed.), The Electromagnetic Interaction
//          in Nuclear Spectroscopy, North-Holland, Amsterdam 1975

double rel_pop(int two_m, double sigma);

// Calculates (-1)^x for integer x
inline int minus_one_pow(int x)
{
  return 1 - ((x & 1) << 1);
}

// Calculates the minimum of x and y
inline int min(int x, int y)
{
  return (x < y) ? x : y;
}

// Calculates the maximum of x and y
inline int max(int x, int y)
{
  return (x > y) ? x : y;
}

// Calculates the absolute value of x
inline int abs(int x)
{
  return (x < 0) ? -x : x;
}

// Calculates delta(x, y)
inline int d(int x, int y)
{
  return (x == y) ? 1 : 0;
}

// Converts degrees to radians
inline double deg2rad(double deg)
{
  return deg * M_PI / 180.0;
}

// Calculates the Clebsch-Gordan coefficient from a Wigner 3j-symbol
// WARNING: only valid for ja - jb + mc integer!!!
double clebsch(int two_ja, int two_jb, int two_jc, int two_ma, int two_mb, int two_mc)
{
  double res;
  
  res  = minus_one_pow((two_ja - two_jb + two_mc) / 2);
  res *= sqrt(two_jc + 1);
  res *= gsl_sf_coupling_3j( two_ja, two_jb, two_jc, 
                             two_ma, two_mb, -two_mc );
                             
  return res;
}

// Calculate the F-coefficients, as defined in Eqn. 12.168 of [SA75]
// WARNING: Only valid for I_2 + I_1 integer!!!
double F_coeff(int lambda,
               int L, int L_prime,
               int two_I_2, int two_I_1)
{
  double res;
  res = sqrt((double) (2*lambda + 1) * (2*L + 1) * (2*L_prime + 1) * (two_I_1 + 1));
  res *= (double) minus_one_pow((two_I_2 + two_I_1) / 2 - 1);
  
  // Note that the GSL coupling functions take two_J as input parameters
  res *= gsl_sf_coupling_3j(2*L, 2*L_prime, 2*lambda,
                              2,        -2,        0);
  res *= gsl_sf_coupling_6j(     2*L, 2*L_prime, 2*lambda,
                             two_I_1,   two_I_1,  two_I_2 );
                             
  return res;
}

// Calculate the generalized F-coefficients, as defined in Eqn. 46 of [KSW73]
double gen_F_coeff(int lambda, int lambda_2, int lambda_1,
                   int L, int L_prime,
                   int two_I_2, int two_I_1)
{
  double res;
  res = sqrt((double) ( (two_I_1 + 1) * (two_I_2 + 1) * (2*L + 1) * (2*L_prime + 1)
                          * (2*lambda + 1) * (2*lambda_1 + 1) * (2*lambda_2 + 1)));
  res *= (double) minus_one_pow(L_prime + lambda + lambda_2 + 1);
  
  // Note that the GSL coupling functions take two_J as input parameters
  res *= gsl_sf_coupling_3j( 2*L, 2*L_prime, 2*lambda,
                               2,        -2,        0 );
  res *= gsl_sf_coupling_9j(    two_I_2,       2*L,    two_I_1,
                                two_I_2, 2*L_prime,    two_I_1,
                             2*lambda_2,  2*lambda, 2*lambda_1 );
  
  return res;
}

// Calculate the directional distribution coefficent for a mixed multipole
// $\pi L$ and $\pi^\prime L^\prime$ gamma transition (Eqn. 44 of [KSW73])
double dd_coeff(int lambda,
                int L, int L_prime,
                int two_I_3, int two_I_2,
                double delta)
{
  double res;
  
  res  =                 F_coeff(lambda, L,       L,       two_I_3, two_I_2);
  res += 2. * delta *    F_coeff(lambda, L,       L_prime, two_I_3, two_I_2);
  res += delta * delta * F_coeff(lambda, L_prime, L_prime, two_I_3, two_I_2);
  
  res /= (1. + delta * delta);
  
  return res;
}

// Calculate the ``generalized'' directional distribution coefficent for a
// mixed multipole $\pi L$ and $\pi^\prime L^\prime$ gamma transition
// (Eqn. 60 of [KSW73])

// Warning: only valid for even values of lambda + lambda_1 + lambda_2 !!!
double gen_dd_coeff(int lambda, int lambda_2, int lambda_1,
                    int L, int L_prime,
                    int two_I_2, int two_I_1,
                    double delta)
{
  double res;
  
  res  =                 gen_F_coeff(lambda, lambda_2, lambda_1, L,       L,       two_I_2, two_I_1);
  res += 2. * delta *    gen_F_coeff(lambda, lambda_2, lambda_1, L,       L_prime, two_I_2, two_I_1);
  res += delta * delta * gen_F_coeff(lambda, lambda_2, lambda_1, L_prime, L_prime, two_I_2, two_I_1);
  
  res /= (1. + delta * delta);
  
  return res;
}

// Calculate the orientation parameters B_\lambda(I_1)
// (Eqn. 1 of [KSW73])
// We do not require the relative populations P(m, sigma) to be normalized,
// so we have to include a normalization factor.
double orient_par(int lambda, int two_I_1, double sigma)
{
  int two_m;
  double sum = 0.0;
  double norm = 0.0;
  double P, x;
  
  for(two_m = -two_I_1; two_m <= two_I_1; two_m += 2) {
    P = rel_pop(two_m, sigma);
    
    x  = minus_one_pow((two_I_1 + two_m) / 2);
    x *= clebsch( two_I_1, two_I_1, 2*lambda,
                   -two_m,   two_m,        0 );
    x *= P;
    
    norm += P;
    sum += x;
  }
  
  return sqrt(two_I_1 + 1) * sum / norm;
}

// Relative population of magnetic substates.
// We assume a Gaussian population (as in [EN91]).
double rel_pop(int two_m, double sigma)
{
  double m = (double) two_m / 2.;
  
  return exp(-(m*m) / (2. * sigma*sigma));
}

// Calculate the angular function
// (Eq. 24 of [KSW73])
// Note that GSL provides normalized associated Legendre polynomials,
// Pnorm_l^m = \sqrt{(2l+1)/(4\pi)} \sqrt{(l-m)!/(l+m)!} P_l^m(x)
// which are used here and result in an expression that
// looks different from the equation in the literature
double ang_func(int lambda_1, int lambda, int lambda_2,
                double cos_theta_1, double cos_theta_2, double cos_phi)
{
  int lambda_prime, q;
  lambda_prime = min(lambda, lambda_2);
  double x;
  double sum = 0.0;
  
  // We calculate cos(q * phi) via cos(q * phi) = T_q(cos(q)),
  // where T_q are the Chebyshev polynomials of the first kind.
  // They fulful:
  // T_0(x) = 1
  // T_1(x) = x
  // T_{n+1}(x) = 2xT_n(x) - T_{n-1}(x)
  // or equivalently
  // T_{-1}(x) = x
  // T_0(x) = 1
  double T_2;
  double T_1 = cos_phi;
  double T = 1.;
  
  // Calculates \sum_{q = 0}^{lambda_prime}
  for(q=0;;)
  {
    x  = (2. - (double) d(q, 0));
    x *= clebsch( 2*lambda_1, 2*lambda, 2*lambda_2,
                           0,      2*q,        2*q );
    x *= (4 * M_PI) / (2*lambda_2 + 1);
    x *= gsl_sf_legendre_sphPlm(lambda,   q, cos_theta_1);
    x *= gsl_sf_legendre_sphPlm(lambda_2, q, cos_theta_2);
    x *= T;
        
    sum += x;
    
    if(++q > lambda_prime)
      break;
    
    T_2 = T_1;
    T_1 = T;
    T = 2 * cos_phi * T_1 - T_2;
  }
  
  return sum;
}

// Calculate the full directional correlation (DCO) function
// (Eq. 11 in [KSW73])
double dco_func(int two_I_1, int two_I_2, int two_I_3,
                double sigma, double delta_1, double delta_2,
                double theta_1, double theta_2, double phi)
{
  const int lambda_max = 6;   // arbitrary choice (?), value taken from CORLEONE
  int lambda_1, lambda, lambda_2;
  
  double cos_theta_1 = cos(theta_1);
  double cos_theta_2 = cos(theta_2);
  double cos_phi = cos(phi);
  
  int L_1, L_2;
  
  // Multipolarity of the radiation:
  // L for the first, L_prime for the second transition
  // We assume that the two lowest allowed multipolarities
  // contribute, with their relative contributions
  // given by delta
  // CHECKME: correct for half-integer spins???
  L_1 = max(1, abs(two_I_1 - two_I_2) / 2);
  L_2 = max(1, abs(two_I_2 - two_I_3) / 2);
  
  double B, A_3, A_1, H;
  double sum = 0.0;
  
  // CHECKME: Is lambda += 2 always correct? Why?
  for(lambda = 0; lambda <= lambda_max; lambda += 2) {
    for(lambda_2 = 0; lambda_2 <= lambda_max; lambda_2 += 2) {
      for(lambda_1 = abs(lambda - lambda_2);
          lambda_1 <= min(lambda_max, lambda + lambda_2);
          lambda_1 += 2) {
        B = orient_par(lambda_1, two_I_1, sigma);
        A_3 = gen_dd_coeff(lambda, lambda_2, lambda_1,
                           L_1, L_1 + 1,
                           two_I_2, two_I_1,
                           delta_1);
        A_1 = dd_coeff(lambda_2,
                       L_2, L_2 + 1,
                       two_I_3, two_I_2,
                       delta_2);
        H = ang_func(lambda_1, lambda, lambda_2,
                     cos_theta_1, cos_theta_2, cos_phi);
        sum += B * A_3 * A_1 * H;
      }
    }
  }
  
  return sum;
}

int main()
{
  double dco = dco_func(8, 4, 0, 2.5, 0.5, 0.0, deg2rad(90.0), deg2rad(45.0), deg2rad(90.0));
  std::cout << dco << std::endl;
  
  return 0;
}
