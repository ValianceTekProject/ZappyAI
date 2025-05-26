/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Server
*/

#pragma once

#include <vector>
#include <cstdint>
#include <netinet/in.h>
#include <poll.h>
#include <string>
#include <iostream>
#include <sstream>

#include "Error.hpp"
#include "Player.hpp"

namespace ZappyServer {

    class Server {
        public:
            Server() : _port(-1), _width(-1), _height(-1), _clientNb(-1), _freq(-1) {}
            ~Server() = default;

            void parsing(int argc, char const *argv[]);
            void parsingName(int &index, char const *argv[]);

            const int getWidth() { return _width; }
            const int getHeight() { return _height; }
            const int getClientNb() { return _clientNb; }

        private:

            int _port;
            int _servSocket;
            sockaddr_in servAddr{};
            std::vector<ZappyPlayer::Team> _clientList;
            std::vector<pollfd> fds;

            int _width;
            int _height;
            int _clientNb;
            int _freq;
            std::vector<std::string> _namesTeam;
    };
}