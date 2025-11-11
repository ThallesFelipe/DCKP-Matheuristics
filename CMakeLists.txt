# CMake configuration for DCKP-Matheuristics project
cmake_minimum_required(VERSION 3.15)
project(DCKP_Matheuristics VERSION 1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Compiler flags
if(MSVC)
    add_compile_options(/W4 /O2)
else()
    add_compile_options(-Wall -Wextra -Wpedantic -O3)
endif()

# Include directories
include_directories(${CMAKE_SOURCE_DIR}/src)

# Source files for utilities
set(UTILS_SOURCES
    src/utils/instance_reader.cpp
    src/utils/solution.cpp
    src/utils/validator.cpp
)

# Source files for constructive heuristics
set(CONSTRUCTIVE_SOURCES
    src/constructive/greedy.cpp
    src/constructive/grasp.cpp
)

# Main executable
add_executable(dckp_solver
    src/main.cpp
    ${UTILS_SOURCES}
    ${CONSTRUCTIVE_SOURCES}
)

# Enable compiler warnings
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(dckp_solver PRIVATE -Wall -Wextra -Wpedantic)
elseif(MSVC)
    target_compile_options(dckp_solver PRIVATE /W4)
endif()

# Output directory
set_target_properties(dckp_solver PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

# Installation
install(TARGETS dckp_solver DESTINATION bin)

# Print configuration summary
message(STATUS "")
message(STATUS "=== DCKP-Matheuristics Configuration ===")
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "C++ compiler: ${CMAKE_CXX_COMPILER}")
message(STATUS "C++ standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Install prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "========================================")
message(STATUS "")
