//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include <functional>
#include <memory>
#include <mutex>
#include <queue>
#include <string>
#include <vector>

#include "Inventory.hpp"

namespace zappy {
    namespace server {

        enum class ClientState {
            WAITING_TEAM_NAME,
            CONNECTED,
        };

        class Client {
           public:
            Client(int socket)
                : _socket(socket), _state(ClientState::WAITING_TEAM_NAME)
            {
                this->queueMutex = std::make_unique<std::mutex>();
            };

            ~Client() = default;

            int getSocket() const { return this->_socket; }
            ClientState getState() const { return this->_state; }

            void setState(ClientState state) { this->_state = state; }

            std::queue<std::string> queueMessage;
            std::shared_ptr<std::mutex> queueMutex = nullptr;

           private:
            int _socket;
            ClientState _state;
        };
    }  // namespace server
}  // namespace zappy
