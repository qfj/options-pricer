#ifndef OPTION_HPP
#define OPTION_HPP

struct Option {
    double S;     // Spot
    double K;     // Strike
    double T;     // Time to maturity
    double r;     // Risk-free rate
    double sigma; // Volatility
};

#endif // OPTION_HPP
