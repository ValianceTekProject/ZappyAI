/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#pragma once

#include "Teams.hpp"
#include "ServerMap.hpp"
#include "my_macros.hpp"
#include "ClientCommand.hpp"
#include "GuiCommand.hpp"
#include <atomic>
#include <chrono>

namespace zappy {
    namespace game {


        class Game {

           public:
            Game(int mapWidth, int mapHeight, std::vector<Team> teamList, int freq, int clientNb)
                : _map(mapWidth, mapHeight),
                _commandHandler(freq, _map.getWidth(), _map.getHeight(), clientNb, _map, _teamList),
                _commandHandlerGui(freq, _map.getWidth(), _map.getHeight(), clientNb, _map, _teamList),
                _teamList(std::move(teamList)),
                _baseFreqMs(freq),
                _clientNb(clientNb)
            {
                for (auto &team : this->_teamList)
                    team.setClientNb(_clientNb);
                this->_map.setEggsonMap(this->_teamList, clientNb);
            }

            ~Game() = default;

            void runGame();
            void setRunningState(RunningState run) { this->_isRunning = run; };

            bool handleTeamJoin(int clientSocket, const std::string &teamName);
            void removeFromTeam(int clientSocket);

            int getFreq() { return this->_baseFreqMs; }
            int getClientNb() const { return this->_clientNb; }
            MapServer &getMap() { return this->_map; }
            std::vector<zappy::game::Team> &getTeamList() { return this->_teamList; };

           private:
            int _idPlayerTot = 0;
            MapServer _map;
            zappy::game::CommandHandler _commandHandler;
            zappy::game::CommandHandlerGui _commandHandlerGui;
            std::vector<zappy::game::Team> _teamList;
            std::vector<std::weak_ptr<zappy::game::Player>> _playerList;
            int _baseFreqMs;
            int _clientNb;
            std::atomic<RunningState> _isRunning = RunningState::PAUSE;

            void _playTurn();
            bool _checkGraphicalFull(const std::string &teamName);
            bool _checkAlreadyInTeam(int clientSocket);
            void _addPlayerToTeam(Team &team, int clientSocket);
        };
    }  // namespace game
}  // namespace zappy
