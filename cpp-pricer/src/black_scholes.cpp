#include "option.hpp"
#include "black_scholes.hpp"
#include <cmath>

double norm_cdf(double x) {
    return 0.5 * (1.0 + std::erf(x / std::sqrt(2.0)));
}

double black_scholes_call(const Option& opt) {
    double d1 = (std::log(opt.S / opt.K) + (opt.r + 0.5 * opt.sigma * opt.sigma) * opt.T)
              / (opt.sigma * std::sqrt(opt.T));
    double d2 = d1 - opt.sigma * std::sqrt(opt.T);
    return opt.S * norm_cdf(d1) - opt.K * std::exp(-opt.r * opt.T) * norm_cdf(d2);
}

double black_scholes_put(const Option& opt) {
    double d1 = (std::log(opt.S / opt.K) + (opt.r + 0.5 * opt.sigma * opt.sigma) * opt.T)
              / (opt.sigma * std::sqrt(opt.T));
    double d2 = d1 - opt.sigma * std::sqrt(opt.T);
    return opt.K * std::exp(-opt.r * opt.T) * norm_cdf(-d2) - opt.S * norm_cdf(-d1);
}

