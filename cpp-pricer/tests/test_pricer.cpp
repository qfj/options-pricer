#include <catch2/catch_test_macros.hpp>
#include "pricer.hpp"
#include "option.hpp"

// Hint: reuse the same parameters we used in main()
TEST_CASE("Pricer computes correct call and put prices", "[pricer]") {
    Option opt{100.0, 100.0, 1.0, 0.05, 0.2};
    Pricer pricer;

    double call = pricer.call_price(opt);
    double put  = pricer.put_price(opt);

    // Replace with expected values (from your earlier run)
    double expected_call = 10.4506;
    double expected_put  = 5.57353;

    REQUIRE(std::abs(call - expected_call) < 1e-4);
    REQUIRE(std::abs(put - expected_put) < 1e-4);
}