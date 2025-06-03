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

            void runGame();
            void setRunningState(RunningState run) { this->_isRunning = run; };

            bool handleTeamJoin(int clientSocket, const std::string &teamName);
            void removeFromTeam(int clientSocket);

            void setRun(bool run) { this->_isRunning = run; };

           private:
            int _idTot = 0;
            MapServer _map;
            std::chrono::milliseconds _baseFreqMs;
            std::atomic<bool> _isRunning = false;

            void _playTurn();
            bool _checkAlreadyInTeam(int clientSocket);
            void _addPlayerToTeam(Team &team, int clientSocket);
        };
    }  // namespace game
}  // namespace zappy
