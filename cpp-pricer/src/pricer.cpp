#include "pricer.hpp"
#include "black_scholes.hpp"

double Pricer::call_price(const Option& opt) const {
    return black_scholes_call(opt);
}

double Pricer::put_price(const Option& opt) const {
    return black_scholes_put(opt);
}
