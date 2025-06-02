/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#pragma once

#include <ctime>

#include "Data/Game/Map.hpp"

namespace zappy {
    namespace game {

        class MapServer : public Map {
           public:
            MapServer() = default;
            ~MapServer() = default;

            void mapInit();

           private:
        };

        class Game {

           public:
            Game() : _isRunning(false) {}

            ~Game() = default;

            void gameLoop();

            MapServer &getMap() { return _map; }

           private:
            MapServer _map;
            bool _isRunning;
        };
    }  // namespace game
}  // namespace zappy
