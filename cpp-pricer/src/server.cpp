#include "pricer.hpp"
#include "option.hpp"
#include "metrics.hpp"
#include "black_scholes.hpp"

#include <httplib.h>
#include <sstream>
#include <iomanip>
#include <string>
#include <map>
#include <csignal>
#include <atomic>
#include <iostream>
#include <thread>
#include <chrono>
#include <random>

std::atomic<bool> stop_requested{false};
std::atomic<int> in_flight_requests{0};
std::atomic<int> demo_gauge{0}; // synthetic metric for jumping line

void handle_signal(int signal) {
    std::cout << "\nReceived signal " << signal << ", shutting down server..." << std::endl;
    stop_requested = true;
}

double get_param_or_default(const httplib::Params& params, const std::string& key, double default_val) {
    auto range = params.equal_range(key);
    if (range.first == range.second) {
        return default_val;
    }

    try {
        return std::stod(range.first->second);
    } catch (const std::exception&) {
        return default_val;
    }
}


int main() {
    httplib::Server svr;

    // Launch a detached thread that updates a synthetic "demo gauge" metric every 500ms
    // with random values from 0 to 100, purely for Prometheus/demo visualization.
    std::thread([]{
        std::mt19937 rng(std::random_device{}());
        std::uniform_int_distribution<int> dist(0, 100);
        while (!stop_requested) {
            demo_gauge = dist(rng);
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
    }).detach();

    svr.Get("/price", [](const httplib::Request& req, httplib::Response& res) {
        auto start = std::chrono::high_resolution_clock::now();
        metrics.requests_total++;
        in_flight_requests++;

        try {
            double spot   = get_param_or_default(req.params, "spot", 0.0);
            double strike = get_param_or_default(req.params, "strike", 0.0);
            double rate   = get_param_or_default(req.params, "rate", 0.0);
            double vol    = get_param_or_default(req.params, "vol", 0.0);
            double expiry = get_param_or_default(req.params, "expiry", 0.0);

            Option opt{spot, strike, expiry, rate, vol};
            Pricer pricer;

            double call_price = pricer.call_price(opt);
            double put_price  = pricer.put_price(opt);

            std::ostringstream oss;
            oss << std::fixed << std::setprecision(6);
            oss << R"({"call": )" << call_price
                << R"(, "put": )" << put_price
                << "}" << "\n";

            res.set_content(oss.str(), "application/json");

        } catch (const std::exception& e) {
            metrics.errors_total++;
            res.status = 400;
            res.set_content(R"({"error": ")" + std::string(e.what()) + "\"}" + "\n", "application/json");
        }

        auto end = std::chrono::high_resolution_clock::now();
        metrics.request_duration_seconds = std::chrono::duration<double>(end - start).count();
        in_flight_requests--;
    });

    svr.Get("/metrics", [](const httplib::Request&, httplib::Response &res) {
        std::ostringstream out;

        out << "# HELP requests_total Total number of pricing requests handled\n"
            << "# TYPE requests_total counter\n"
            << "requests_total " << metrics.requests_total.load() << "\n\n";

        out << "# HELP errors_total Total failed requests\n"
            << "# TYPE errors_total counter\n"
            << "errors_total " << metrics.errors_total.load() << "\n\n";

        out << "# HELP request_duration_seconds Duration of last request in seconds\n"
            << "# TYPE request_duration_seconds gauge\n"
            << "request_duration_seconds " << metrics.request_duration_seconds.load() << "\n\n";

        out << "# HELP in_flight_requests Currently active requests\n"
            << "# TYPE in_flight_requests gauge\n"
            << "in_flight_requests " << in_flight_requests.load() << "\n\n";

        out << "# HELP demo_gauge Synthetic gauge for demo/jumping line\n"
            << "# TYPE demo_gauge gauge\n"
            << "demo_gauge " << demo_gauge.load() << "\n";

        res.set_content(out.str(), "text/plain");
    });

    svr.Get("/healthz", [](const httplib::Request&, httplib::Response &res) {
        res.status = 200;
        res.set_content("ok\n", "text/plain");
    });

    std::signal(SIGINT, handle_signal);
    std::signal(SIGTERM, handle_signal);

    std::cout << "Server listening on http://localhost:8080\n";

    std::thread server_thread([&]() {
        svr.listen("0.0.0.0", 8080);
    });

    while (!stop_requested) {
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

    svr.stop();
    
    server_thread.join();
    std::cout << "Server stopped gracefully.\n";
}