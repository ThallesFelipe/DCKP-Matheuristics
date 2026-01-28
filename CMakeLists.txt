cmake_minimum_required(VERSION 3.25)
project(DCKP VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

if(MSVC)
    add_compile_options(/W4 /O2 /std:c++latest)
else()
    add_compile_options(-Wall -Wextra -O3 -pedantic)
endif()

set(SOURCES
    src/main.cpp
    src/utils/instance_reader.cpp
    src/utils/solution.cpp
    src/utils/validator.cpp
    src/constructive/greedy.cpp
    src/constructive/grasp.cpp
)

add_executable(dckp_solver ${SOURCES})
target_include_directories(dckp_solver PRIVATE ${CMAKE_SOURCE_DIR}/src)

set_target_properties(dckp_solver PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
)

install(TARGETS dckp_solver DESTINATION bin)
