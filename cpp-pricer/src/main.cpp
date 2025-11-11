#include "pricer.hpp"
#include "option.hpp"
#include "black_scholes.hpp"
#include <iostream>

// Command line test main.

int main(){
    Option opt{100.0, 100.0, 1.0, 0.05, 0.2};
    Pricer pricer;

    std::cout << "Call price: " << pricer.call_price(opt) << "\n";
    std::cout << "Put price: "  << pricer.put_price(opt) << "\n";

    return 0;
}