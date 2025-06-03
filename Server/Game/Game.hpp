/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#pragma once

#include "Map/Map.hpp"
#include <atomic>
#include <chrono>

namespace zappy {
    namespace game {

        constexpr int baseGameFreqMs = 1000;

        class Game {

           public:
            Game() : _baseFreqMs(baseGameFreqMs) {}

            ~Game() = default;

            void gameLoop();

            MapServer &getMap() { return _map; }

            void setRun(bool run) { this->_isRunning = run; };

           private:
            MapServer _map;
            std::chrono::milliseconds _baseFreqMs;
            std::atomic<bool> _isRunning = false;

            void _playTurn();
        };
    }  // namespace game
}  // namespace zappy
