#ifndef BLACK_SCHOLES_HPP
#define BLACK_SCHOLES_HPP

#include "option.hpp"

double norm_cdf(double x);
double black_scholes_call(const Option& opt);
double black_scholes_put(const Option& opt);

#endif // BLACK_SCHOLES_HPP
