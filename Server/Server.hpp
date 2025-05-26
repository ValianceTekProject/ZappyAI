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

#include "Player.hpp"

namespace ZappyServer {

    class Server {
        public:
            Server();
            ~Server();

        private:
            std::size_t _port;
            int servSocket;
            sockaddr_in servAddr{};
            std::vector<Team> _clientList;
            std::vector<pollfd> fds;
    };
}