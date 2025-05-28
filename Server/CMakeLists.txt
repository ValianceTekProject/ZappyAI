cmake_minimum_required(VERSION 3.14)
project(ZappyServer)

# Set output binary in root of the project
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})

# Use C++17
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable common warnings
add_compile_options(-Wall -Wextra -Werror)

# Include headers
include_directories(
    .
    Error
    Inventory
    Player
    EncapsuledFunction
    Game
)

# Add executable
add_executable(zappy_server
    Main.cpp
    Server.cpp
    ClientConnexion.cpp
    Error/Error.cpp
    Inventory/Inventory.cpp
    EncapsuledFunction/NetworkFunction.cpp
)
