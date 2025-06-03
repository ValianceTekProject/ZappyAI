/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#pragma once

#include <atomic>
#include <chrono>
#include <ctime>
#include <functional>

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
            Game(): _baseFreqMs(1000) {}

            ~Game() = default;

            void gameLoop();

            MapServer &getMap() { return _map; }

            void setRun(bool run) {this->_isRunning = run;};

           private:
            MapServer _map;
            std::chrono::milliseconds _baseFreqMs;
            std::atomic<bool>_isRunning = false;
        
            void _playTurn();
        };
    }  // namespace game
}  // namespace zappy
