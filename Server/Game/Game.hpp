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
            Game() : _baseFreqMs(baseGameFreqMs) {}

            ~Game() = default;

            void gameLoop();
            void setRunningState(RunningState run) { this->_isRunning = run; };

            bool handleTeamJoin(int clientSocket, const std::string &teamName);
            void removeFromTeam(int clientSocket);

           private:
            int _idTot = 0;
            MapServer _map;
            // std::vector<zappy::game::Team> _teamList;
            std::chrono::milliseconds _baseFreqMs;
            std::atomic<RunningState> _isRunning = RunningState::PAUSE;

            void _playTurn();
            bool _checkAlreadyInTeam(int clientSocket);
            void _addPlayerToTeam(Team &team, int clientSocket);
        };
    }  // namespace game
}  // namespace zappy
