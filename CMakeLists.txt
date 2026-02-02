# ==============================================================================
# DCKP Solver - Heurísticas e Metaheurísticas
# ==============================================================================
# CMake Build Configuration
# Suporta: Windows (MinGW/MSVC) e Linux (GCC/Clang)
# ==============================================================================

cmake_minimum_required(VERSION 3.25)
project(DCKP
    VERSION 2.0
    DESCRIPTION "DCKP Solver - Heurísticas e Metaheurísticas para o Problema da Mochila com Restrições de Conflitos"
    LANGUAGES CXX
)

# ==============================================================================
# Configuração do Padrão C++
# ==============================================================================

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# ==============================================================================
# Opções de Build
# ==============================================================================

option(DCKP_ENABLE_LTO "Enable Link Time Optimization" ON)
option(DCKP_ENABLE_WARNINGS "Enable comprehensive warnings" ON)

# ==============================================================================
# Flags de Compilação por Plataforma
# ==============================================================================

if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
    # MSVC (Visual Studio)
    set(DCKP_COMPILE_OPTIONS
        /W4                 # Warning level 4
        /O2                 # Maximum optimization
        /std:c++latest      # Latest C++ standard
        /permissive-        # Strict conformance
        /Zc:__cplusplus     # Correct __cplusplus macro
        /EHsc               # Exception handling
    )
elseif(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    # GCC / Clang / MinGW
    set(DCKP_COMPILE_OPTIONS
        -Wall               # All warnings
        -Wextra             # Extra warnings
        -Wpedantic          # ISO conformance
        -Wconversion        # Type conversion warnings
        -Wshadow            # Shadow variable warnings
        -Wnon-virtual-dtor  # Non-virtual destructor warnings
        -O3                 # Maximum optimization
        -march=native       # Target CPU architecture
    )

    # Link Time Optimization
    if(DCKP_ENABLE_LTO AND NOT CMAKE_BUILD_TYPE STREQUAL "Debug")
        list(APPEND DCKP_COMPILE_OPTIONS -flto)
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -flto")
    endif()
endif()

# ==============================================================================
# Arquivos Fonte
# ==============================================================================

set(DCKP_SOURCES
    src/main.cpp
    src/utils/instance_reader.cpp
    src/utils/solution.cpp
    src/utils/validator.cpp
    src/constructive/greedy.cpp
    src/constructive/grasp.cpp
    src/local_search/hill_climbing.cpp
    src/local_search/vnd.cpp
)

set(DCKP_HEADERS
    src/utils/instance_reader.h
    src/utils/solution.h
    src/utils/validator.h
    src/constructive/greedy.h
    src/constructive/grasp.h
    src/local_search/hill_climbing.h
    src/local_search/vnd.h
)

# ==============================================================================
# Target Executável
# ==============================================================================

add_executable(dckp_solver ${DCKP_SOURCES} ${DCKP_HEADERS})

target_include_directories(dckp_solver
    PRIVATE
        ${CMAKE_SOURCE_DIR}/src
)

target_compile_options(dckp_solver
    PRIVATE
        ${DCKP_COMPILE_OPTIONS}
)

set_target_properties(dckp_solver PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin
    OUTPUT_NAME dckp_solver
    CXX_STANDARD 23
    CXX_STANDARD_REQUIRED ON
)

# ==============================================================================
# Instalação
# ==============================================================================

install(TARGETS dckp_solver
    RUNTIME DESTINATION bin
)

# ==============================================================================
# Informações de Build
# ==============================================================================

message(STATUS "=== DCKP Solver Configuration ===")
message(STATUS "Version: ${PROJECT_VERSION}")
message(STATUS "C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "Compiler: ${CMAKE_CXX_COMPILER_ID} ${CMAKE_CXX_COMPILER_VERSION}")
message(STATUS "Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "LTO Enabled: ${DCKP_ENABLE_LTO}")
message(STATUS "===================================")
