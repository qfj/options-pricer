#ifndef METRICS_HPP
#define METRICS_HPP

#include <atomic>

struct Metrics {
    std::atomic<int> requests_total{0};
    std::atomic<int> errors_total{0};
    std::atomic<double> request_duration_seconds{0.0};
};

inline Metrics metrics;

#endif