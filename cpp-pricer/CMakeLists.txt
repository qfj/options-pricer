cmake_minimum_required(VERSION 3.15)
project(OptionsPricer LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ------------------------
# Pricing library
# ------------------------
add_library(pricing STATIC
    src/black_scholes.cpp
    src/pricer.cpp
)

target_include_directories(pricing PUBLIC
    ${CMAKE_SOURCE_DIR}/include
)

# Compiler warnings
target_compile_options(pricing PRIVATE -Wall -Wextra -Wpedantic)

# ------------------------
# Fetch dependencies
# ------------------------
include(FetchContent)

# Catch2
FetchContent_Declare(
  catch2
  GIT_REPOSITORY https://github.com/catchorg/Catch2.git
  GIT_TAG v3.4.0
)

# cpp-httplib
FetchContent_Declare(
  cpp_httplib
  GIT_REPOSITORY https://github.com/yhirose/cpp-httplib.git
  GIT_TAG v0.15.3  # or latest stable tag
)

FetchContent_MakeAvailable(catch2 cpp_httplib)

# ------------------------
# Main CLI executable
# ------------------------
add_executable(pricer src/main.cpp)
target_link_libraries(pricer PRIVATE pricing)

# ------------------------
# HTTP server executable
# ------------------------
add_executable(pricer_server src/server.cpp)
target_include_directories(pricer_server PRIVATE ${cpp_httplib_SOURCE_DIR})
target_link_libraries(pricer_server PRIVATE pricing)


# ------------------------
# Tests (auto-discover and register individually)
# ------------------------
file(GLOB TEST_SOURCES ${CMAKE_SOURCE_DIR}/tests/test_*.cpp)

foreach(TEST_FILE ${TEST_SOURCES})
    get_filename_component(TEST_NAME ${TEST_FILE} NAME_WE)
    add_executable(${TEST_NAME} ${TEST_FILE})
    target_link_libraries(${TEST_NAME} PRIVATE pricing Catch2::Catch2WithMain)
    add_test(NAME ${TEST_NAME} COMMAND ${TEST_NAME})
endforeach()

enable_testing()
