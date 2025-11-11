#ifndef PRICER_HPP
#define PRICER_HPP

#include "option.hpp"

class Pricer {
public:
    double call_price(const Option& opt) const;
    double put_price(const Option& opt) const;
};

#endif // PRICER_HPP
