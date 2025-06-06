/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#pragma once

#include "Teams/Teams.hpp"
#include "Map/Map.hpp"
#include "my_macros.hpp"
#include "Commands/ClientCommand.hpp"
#include <atomic>
#include <chrono>

namespace zappy {
    namespace game {

        constexpr int baseGameFreqMs = 1000;

        class Game {

           public:
            Game(
                int mapWidth, int mapHeight, std::vector<Team> teamList, int clientNb)
                : _map(mapWidth, mapHeight), _teamList(std::move(teamList)), _baseFreqMs(baseGameFreqMs), _clientNb(clientNb)
            {}

            ~Game() = default;

            void runGame();
            void setRunningState(RunningState run) { this->_isRunning = run; };

            bool handleTeamJoin(int clientSocket, const std::string &teamName);
            void removeFromTeam(int clientSocket);

            MapServer &getMap() { return this->_map; }
            std::vector<zappy::game::Team> &getTeamList() { return this->_teamList; };

           private:
            int _idTot = 0;
            MapServer _map;
            zappy::game::CommandHandler _commandHandler;
            std::vector<zappy::game::Team> _teamList;
            std::chrono::milliseconds _baseFreqMs;
            int _clientNb;
            std::atomic<RunningState> _isRunning = RunningState::PAUSE;

            void _playTurn();
            bool _checkAlreadyInTeam(int clientSocket);
            void _addPlayerToTeam(Team &team, int clientSocket);
        };
    }  // namespace game
}  // namespace zappy
