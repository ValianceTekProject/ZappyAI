cmake_minimum_required(VERSION 3.10)
project(zappy_server)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_BUILD_TYPE Release)
add_compile_options(-Wall -Wextra -Werror -pedantic)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -fno-gnu-unique -Wl,--export-dynamic")

# === Dossiers sources ===
set(CLIENT_DIR ${CMAKE_CURRENT_SOURCE_DIR}/Client)
set(ERROR_DIR ${CMAKE_CURRENT_SOURCE_DIR}/Error)
set(GAME_DIR ${CMAKE_CURRENT_SOURCE_DIR}/Game)
set(IVENTORY ${CMAKE_CURRENT_SOURCE_DIR}/Inventory)
set(NETWORK_DIR ${CMAKE_CURRENT_SOURCE_DIR}/Network)
set(SERVER_DIR ${CMAKE_CURRENT_SOURCE_DIR}/Server)

set(COMMANDS_DIR ${GAME_DIR}/Commands)
set(MAP_DIR ${GAME_DIR}/Map)
set(PLAYER_DIR ${GAME_DIR}/Player)
set(TEAMS_DIR ${GAME_DIR}/Teams)

set(UTILS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../Utils)
set(DATA_DIR ${CMAKE_CURRENT_SOURCE_DIR}/../Data)
set(DATA_ERRORS_DIR ${DATA_DIR}/Errors)
set(DATA_GUI_DIR ${DATA_DIR}/Gui)
set(DATA_GAME_DIR ${DATA_DIR}/Game)

# === Include paths ===
include_directories(
    ${DATA_ERRORS_DIR}
    ${DATA_GUI_DIR}
    ${DATA_GAME_DIR}

    ${CMAKE_CURRENT_SOURCE_DIR}

    ${CLIENT_DIR}
    ${ERROR_DIR}

    ${GAME_DIR}
    ${COMMANDS_DIR}
    ${MAP_DIR}
    ${PLAYER_DIR}
    ${TEAMS_DIR}
    ${UTILS_DIR}

    ${IVENTORY}
    ${NETWORK_DIR}
    ${SERVER_DIR}
)

# === Fichiers sources ===
set(SOURCES

    ${DATA_ERRORS_DIR}/AError.cpp
    
    ${DATA_GAME_DIR}/Resource.cpp
    ${DATA_GAME_DIR}/ResourceContainer.cpp
    ${DATA_GAME_DIR}/Player.cpp
    ${DATA_GAME_DIR}/Map.cpp

    ${ERROR_DIR}/Error.cpp
    ${GAME_DIR}/Game.cpp
    ${GAME_DIR}/Turn.cpp
    ${COMMANDS_DIR}/ClientCommand.cpp
    ${COMMANDS_DIR}/GuiCommand.cpp
    ${MAP_DIR}/Base.cpp
    ${TEAMS_DIR}/Base.cpp
    ${IVENTORY}/ServerInventory.cpp
    ${NETWORK_DIR}/SocketServer.cpp
    ${SERVER_DIR}/Base.cpp
    ${SERVER_DIR}/Commands.cpp
    ${SERVER_DIR}/Connexion.cpp
    ${SERVER_DIR}/Observer.cpp
    ${UTILS_DIR}/Utils.cpp

    ${CMAKE_CURRENT_SOURCE_DIR}/Main.cpp
)

# === Output binary in project root ===
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/../)
# === Exécutable principal ===
add_executable(zappy_server ${SOURCES})
