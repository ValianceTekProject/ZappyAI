cmake_minimum_required(VERSION 3.10)

project(Zappy CXX)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/lib)
set(CMAKE_CXX_STANDARD 17)

add_subdirectory(Server)
# add_subdirectory(Client)
# add_subdirectory(GUI)
