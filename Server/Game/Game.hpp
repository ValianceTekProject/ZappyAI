/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#pragma once

#include "ITeams.hpp"
#include "TeamsPlayer.hpp"
#include "ServerMap.hpp"
#include "my_macros.hpp"
#include "ClientCommand.hpp"
#include "GuiCommand.hpp"
#include <atomic>
#include <chrono>
#include <memory>

namespace zappy {
    namespace game {

        #define TIME_BEFORE_RESPAWN 20

        class Game {

           public:
            Game(int mapWidth, int mapHeight, std::vector<std::shared_ptr<ITeams>> teamList, int &freq, int clientNb)
                : _map(mapWidth, mapHeight),
                _commandHandler(freq, _map.getWidth(), _map.getHeight(), clientNb, _map, _teamList),
                _commandHandlerGui(freq, _map.getWidth(), _map.getHeight(), clientNb, _map, _teamList),
                _teamList(teamList),
                _baseFreqMs(freq),
                _clientNb(clientNb)
            {
                for (auto &team : this->_teamList) {
                    auto teamCast = (dynamic_cast<TeamsPlayer*>(&(*team)));
                    if (teamCast)
                        teamCast->setClientNb(_clientNb);
                }
                std::srand(std::time(nullptr));
                this->_map.setEggsonMap(teamList, clientNb);
            
            }

            ~Game() = default;

            void runGame();
            void setRunningState(RunningState run) { this->_isRunning = run; };

            bool handleTeamJoin(int clientSocket, const std::string &teamName);
            void removeFromTeam(int clientSocket);

            int &getFreq() { return this->_baseFreqMs; }
            int getClientNb() const { return this->_clientNb; }
            MapServer &getMap() { return this->_map; }
            std::vector<std::shared_ptr<zappy::game::ITeams>> &getTeamList() { return this->_teamList; };

            void foodManager(std::shared_ptr<ITeams> &team);

           private:
            int _idPlayerTot = 0;
            MapServer _map;
            zappy::game::CommandHandler _commandHandler;
            zappy::game::CommandHandlerGui _commandHandlerGui;
            std::vector<std::shared_ptr<zappy::game::ITeams>> _teamList;
            std::vector<std::weak_ptr<zappy::game::Player>> _playerList;
            int &_baseFreqMs;
            int _clientNb;
            std::atomic<RunningState> _isRunning = RunningState::PAUSE;

            void _playTurn();
            bool _checkAlreadyInTeam(int clientSocket);
            void _addPlayerToTeam(std::shared_ptr<ITeams> team, int clientSocket);
        };
    }  // namespace game
}  // namespace zappy
