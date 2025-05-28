cmake_minimum_required(VERSION 3.10)
project(zappy_gui)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_BUILD_TYPE Release)
add_compile_options(-Wall -Wextra -Werror -pedantic)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -fno-gnu-unique -Wl,--export-dynamic")

# === Dossiers sources ===
set(SRC_DIR ${CMAKE_SOURCE_DIR}/src)
set(GAME_DIR ${SRC_DIR}/Game)
set(RENDERER_DIR ${SRC_DIR}/Renderer)

set(DATA_DIR ${CMAKE_SOURCE_DIR}/../Data)
set(DATA_ERRORS_DIR ${DATA_DIR}/Errors)
set(DATA_GAME_DIR ${DATA_DIR}/Game)

# === Include paths ===
include_directories(
    ${DATA_ERRORS_DIR}
    ${DATA_GAME_DIR}

    ${SRC_DIR}

    ${GAME_DIR}
    ${RENDERER_DIR}
    ${DATA_GAME_DIR}
)

# === Fichiers sources ===
set(SOURCES
    ${DATA_ERRORS_DIR}/AError.cpp

    ${DATA_GAME_DIR}/Resource.cpp
    ${DATA_GAME_DIR}/ResourceContainer.cpp
    ${DATA_GAME_DIR}/Player.cpp
    ${DATA_GAME_DIR}/Map.cpp

    ${SRC_DIR}/main.cpp

    ${DATA_GAME_DIR}/Ressource.cpp
    ${DATA_GAME_DIR}/RessourceContainer.cpp
    ${DATA_GAME_DIR}/Player.cpp
    ${DATA_GAME_DIR}/Map.cpp

    ${SRC_DIR}/Gui.cpp

    ${GAME_DIR}/GameState.cpp

    ${RENDERER_DIR}/NcursesRenderer.cpp
    ${RENDERER_DIR}/OpenGLRenderer.cpp
)

# === Exécutable principal ===
add_executable(zappy_gui ${SOURCES})

# === Dépendances ===

## OpenGL
find_package(OpenGL REQUIRED)
target_link_libraries(zappy_gui PRIVATE OpenGL::GL)

## GLEW
find_package(GLEW REQUIRED)
include_directories(${GLEW_INCLUDE_DIRS})
target_link_libraries(zappy_gui PRIVATE GLEW::GLEW)

## Ncurses
find_package(Curses REQUIRED)
include_directories(${CURSES_INCLUDE_DIR})
target_link_libraries(zappy_gui PRIVATE ${CURSES_LIBRARIES})

# === Dossier de sortie du binaire ===
set_target_properties(zappy_gui PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
