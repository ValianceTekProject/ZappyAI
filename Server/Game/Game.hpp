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
#include <atomic>
#include <chrono>

namespace zappy {
    namespace game {

        #define SERVER_FATHER_ID -1

        class Game {

           public:
            Game(int mapWidth, int mapHeight, std::vector<Team> teamList, int freq, int clientNb)
                : _map(mapWidth, mapHeight),
                _commandHandler(freq, _map.getWidth(), _map.getHeight()),
                _teamList(std::move(teamList)),
                _baseFreqMs(freq),
                _clientNb(clientNb)
            { 
                std::srand(std::time(nullptr));
                setEggsonMap();
            
            }


            ~Game() = default;

            void runGame();
            void setRunningState(RunningState run) { this->_isRunning = run; };

            bool handleTeamJoin(int clientSocket, const std::string &teamName);
            void removeFromTeam(int clientSocket);

            int getFreq() { return this->_baseFreqMs; }
            MapServer &getMap() { return this->_map; }
            std::vector<zappy::game::Team> &getTeamList() { return this->_teamList; };

            void setEggsonMap();

           private:
            int _idPlayerTot = 0;
            int _idEggTot = 0;
            MapServer _map;
            zappy::game::CommandHandler _commandHandler;
            std::vector<zappy::game::Team> _teamList;
            std::queue<zappy::game::Egg> _eggList;
            std::vector<std::shared_ptr<zappy::game::Player>> _playerList;
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
