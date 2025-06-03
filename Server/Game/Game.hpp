/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#pragma once

#include "Client.hpp"
#include "Map/Map.hpp"
#include <atomic>
#include <chrono>
#include "my_macros.hpp"

namespace zappy {
    namespace game {

        constexpr int baseGameFreqMs = 1000;

        class Game {

           public:
            Game(int mapWidth, int mapHeight) : _map(mapWidth, mapHeight), _baseFreqMs(baseGameFreqMs) {}

            ~Game() = default;

            void gameLoop();
            void setRunningState(RunningState run) { this->_isRunning = run; };

            MapServer &getMap() { return _map; }

           private:
            MapServer _map;
            // std::vector<zappy::game::Team> _teamList;
            std::chrono::milliseconds _baseFreqMs;
            std::atomic<RunningState> _isRunning = RunningState::PAUSE;

            void _playTurn();
        };
    }  // namespace game
}  // namespace zappy
