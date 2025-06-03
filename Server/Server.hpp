/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Server
*/

#pragma once

#include <algorithm>
#include <csignal>
#include <cstdint>
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
#include "EncapsuledFunction/Socket.hpp"
#include "Error/Error.hpp"
#include "Game.hpp"
#include "Game/Game.hpp"

namespace zappy {

#define OK 0
#define KO 84

    namespace server {

        class Server {
           public:
            Server(int argc, char const *argv[]);
            ~Server() = default;

                void serverLaunch();

            void parsingName(int &index, char const *argv[]);

            int getWidth() const { return _width; }

            int getHeight() const { return _height; }

            int getClientNb() const { return _clientNb; }

            void serverLoop();
            void handleNewConnection();
            void handleTeamJoin(int clientSocket, const std::string &teamName);
            void handleClientMessage(int clientSocket, std::string buffer);

                void stopServer(int sig);
                void closeClients();
                static void signalWrapper(int sig);
                static std::function<void(int)> takeSignal;

           private:
            zappy::game::Game _game;
            std::unique_ptr<server::Socket> _socket = nullptr;
            bool _serverRun;
            int _port;
            sockaddr_in servAddr{};
            std::vector<zappy::game::Team> _teamList;
            std::vector<pollfd> fds;

            std::unordered_map<int, zappy::server::Client> _users;

            std::mutex _socketLock;
            std::mutex _endLock;

            int _width;
            int _height;
            int _clientNb;
            int _freq;
            std::vector<std::string> _namesTeam;

            void _parseArgs(int argc, char const *argv[]);
        };

        // Encapsuled Functions
        void my_signal(int __sig, sighandler_t __handler);
    }  // namespace server
}  // namespace zappy
