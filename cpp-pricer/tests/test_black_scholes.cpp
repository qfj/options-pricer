#include "catch2/catch_test_macros.hpp"
#include "black_scholes.hpp"

TEST_CASE("Black-Scholes call and put pricing") {
    Option opt{100.0, 100.0, 1.0, 0.05, 0.2};

    double call_price = black_scholes_call(opt);
    double put_price = black_scholes_put(opt);

    REQUIRE(call_price > 0);
    REQUIRE(put_price > 0);
}