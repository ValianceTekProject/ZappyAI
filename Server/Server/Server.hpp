/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Server
*/

#pragma once

#include <csignal>
#include <functional>
#include <iostream>
#include <mutex>
#include <netinet/in.h>
#include <poll.h>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

#include "Client/Client.hpp"
#include "Socket.hpp"
#include "Error/Error.hpp"
#include "Game.hpp"
#include "my_macros.hpp"

namespace zappy {

    namespace server {

        class Server {
           public:
            Server(int argc, char const *argv[]);
            ~Server() = default;

            void runServer();

            int getWidth() const { return this->_width; }
            int getHeight() const { return this->_height; }
            int getClientNb() const { return this->_clientNb; }

            void runLoop();
            void handleTeamJoin(int clientSocket, const std::string &teamName);
            void handleClientMessage(int clientSocket, std::string buffer);

            void stopServer(int sig);
            void closeClients();
            static void signalWrapper(int sig);
            static std::function<void(int)> takeSignal;

           private:
            std::unique_ptr<zappy::game::Game> _game;
            std::unique_ptr<server::Socket> _socket = nullptr;

            RunningState _serverRun = RunningState::RUN;

            std::vector<zappy::game::Team> _teamList;
            std::vector<pollfd> _fds;

            std::unordered_map<int, zappy::server::Client> _users;
            std::unordered_map<std::string, std::function<void(int)>> _flags;

            std::mutex _socketLock;
            std::mutex _endLock;

            int _port = noValue;
            int _width = noValue;
            int _height = noValue;
            int _clientNb = noValue;
            int _freq = noValue;
            std::vector<std::string> _namesTeam;

            void _parseFlags(int argc, char const *argv[]);
            void _parseName(int &index, char const *argv[]);
            void _parseFlagsInt(int &index, std::string arg, std::string value);
        };

        // Encapsuled Functions
        void my_signal(int __sig, sighandler_t __handler);
    }  // namespace server
}  // namespace zappy
