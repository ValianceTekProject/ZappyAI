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
set(NETWORK_DIR ${SRC_DIR}/Network)
set(GAME_DIR ${SRC_DIR}/Game)
set(RENDERER_DIR ${SRC_DIR}/Renderer)
set(RAYLIB_DIR ${RENDERER_DIR}/Raylib)
set(RAYLIB_SCENE_DIR ${RAYLIB_DIR}/Scene)
set(RAYLIB_FLOOR_DIR ${RAYLIB_DIR}/Floor)
set(RAYLIB_MODEL_DIR ${RAYLIB_DIR}/Model)

set(DATA_DIR ${CMAKE_SOURCE_DIR}/../Data)
set(DATA_ERRORS_DIR ${DATA_DIR}/Errors)
set(DATA_GUI_DIR ${DATA_DIR}/Gui)
set(DATA_GAME_DIR ${DATA_DIR}/Game)

# === Include paths ===
include_directories(
    ${DATA_ERRORS_DIR}
    ${DATA_GUI_DIR}
    ${DATA_GAME_DIR}

    ${SRC_DIR}

    ${NETWORK_DIR}
    ${GAME_DIR}
    ${RENDERER_DIR}
    ${RAYLIB_DIR}
    ${RAYLIB_SCENE_DIR}
    ${RAYLIB_FLOOR_DIR}
    ${RAYLIB_MODEL_DIR}
)

# === Fichiers sources ===
set(SOURCES
    ${DATA_ERRORS_DIR}/AError.cpp

    ${DATA_GAME_DIR}/Resource.cpp
    ${DATA_GAME_DIR}/ResourceContainer.cpp
    ${DATA_GAME_DIR}/Player.cpp
    ${DATA_GAME_DIR}/Map.cpp

    ${SRC_DIR}/main.cpp

    ${DATA_GAME_DIR}/Resource.cpp
    ${DATA_GAME_DIR}/ResourceContainer.cpp
    ${DATA_GAME_DIR}/Player.cpp
    ${DATA_GAME_DIR}/Map.cpp

    ${SRC_DIR}/Gui.cpp

    ${NETWORK_DIR}/NetworkManager.cpp
    ${NETWORK_DIR}/Protocol.cpp

    ${GAME_DIR}/GameState.cpp

    ${RENDERER_DIR}/ARenderer.cpp
    ${RENDERER_DIR}/DebugRenderer.cpp
    ${RENDERER_DIR}/NcursesRenderer.cpp

    ${RAYLIB_DIR}/RaylibRenderer.cpp
    ${RAYLIB_SCENE_DIR}/InputManager.cpp
    ${RAYLIB_SCENE_DIR}/AScene.cpp
    ${RAYLIB_SCENE_DIR}/BasicScene.cpp
)

# === Exécutable principal ===
add_executable(zappy_gui ${SOURCES})

# === Dépendances ===

# Raylib via pkg-config
find_package(PkgConfig REQUIRED)
pkg_check_modules(RAYLIB REQUIRED raylib)

include_directories(${RAYLIB_INCLUDE_DIRS})
link_directories(${RAYLIB_LIBRARY_DIRS})
target_link_libraries(zappy_gui PRIVATE ${RAYLIB_LIBRARIES})

## Ncurses
find_package(Curses REQUIRED)
include_directories(${CURSES_INCLUDE_DIR})
target_link_libraries(zappy_gui PRIVATE ${CURSES_LIBRARIES})

# === Dossier de sortie du binaire ===
set_target_properties(zappy_gui PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR})
