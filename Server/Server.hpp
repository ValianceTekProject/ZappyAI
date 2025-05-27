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
#include <algorithm>

#include "Error/Error.hpp"
#include "Client/Client.hpp"
#include <csignal>
#include <algorithm>

#include "Error.hpp"
#include "Player.hpp"

namespace zappy {

    #define OK 0
    #define KO 84

    #define OK 0
    #define KO 84

    class Server {
        public:
            Server() : _serverRun(true), _port(-1), _width(-1), _height(-1), _clientNb(-1), _freq(-1) {}
            ~Server() = default;

            void serverLaunch();

            void parsing(int argc, char const *argv[]);
            void parsingName(int &index, char const *argv[]);

            int getWidth() const { return _width; }
            int getHeight() const { return _height; }
            int getClientNb() const { return _clientNb; }

            void serverLoop();
            void handleNewConnection();
            void handleTeamJoin(int clientSocket, const std::string &teamName);

            void stopServer(int sig);
            void closeClients();
            static void signalWrapper(int sig);
            static std::function<void(int)> takeSignal;

            void sendMessage(int clientSocket, char const *message) { write(clientSocket, message, std::string(message).size()); }

        private:

            bool _serverRun;
            int _port;
            int _servSocket;
            sockaddr_in servAddr{};
            std::vector<zappy::game::Team> _teamList;
            std::vector<pollfd> fds;

            std::unordered_map<int, zappy::server::User> _users;

            int _width;
            int _height;
            int _clientNb;
            int _freq;
            std::vector<std::string> _namesTeam;
    };

    // Encapsuled Functions
    int my_socket(int __domain, int __type, int __protocol);
    int my_bind(int __fd, const sockaddr *__addr, socklen_t __len);
    int my_listen(int __fd, int __n);
    int my_poll(pollfd *__fds, nfds_t __nfds, int __timeout);
    int my_accept(int __fd, sockaddr *__restrict__ __addr, socklen_t *__restrict__ __addr_len);
    sighandler_t my_signal(int __sig, sighandler_t __handler);
}
