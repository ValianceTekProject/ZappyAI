/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** NetworkManager.hpp
*/

#pragma once

#include "NetworkError.hpp"

#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <poll.h>
#include <unistd.h>

#include <memory>
#include <functional>
#include <sstream>
#include <queue>
#include <mutex>
#include <cstring>

namespace zappy {
    namespace network {
    struct ServerMessage {
        std::string command;
        std::vector<std::string> params;
        std::string raw;
    };

    class NetworkManager {
        public:
            NetworkManager();
            ~NetworkManager();

            bool connect(const std::string &host, int port);
            void disconnect();
            bool isConnected() const;

            bool sendCommand(const std::string &command);
            std::vector<ServerMessage> receiveMessages();
            void setMessageCallback(std::function<void(const ServerMessage &)> callback);

        private:
            int _socket;
            bool _connected;
            std::string _buffer;
            std::queue<ServerMessage> _messageQueue;
            std::function<void(const ServerMessage &)> _messageCallback;
            mutable std::mutex _mutex;

            ServerMessage parseMessage(const std::string &raw);
            void processBuffer();

        };
    } // namespace network
} // namespace zappy
