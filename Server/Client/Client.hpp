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
#include <unistd.h>
#include <vector>
#include <sys/socket.h>

#include "Inventory.hpp"
#include "my_macros.hpp"

namespace zappy {
    namespace server {

        enum class ClientState {
            WAITING_TEAM_NAME,
            CONNECTED,
            DISCONNECTED,
            UNDEFINED
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

            void sendMessage(const std::string &buf) { send(this->_socket, buf.c_str(), buf.size(), 0); }

            std::queue<std::string> queueMessage;
            std::shared_ptr<std::mutex> queueMutex = nullptr;

           private:
            int _socket;
            ClientState _state;
        };
    }  // namespace server

    namespace game {
        class Player {

           public:
            Player(zappy::server::Client &user) : _user(user) {}

            ~Player() = default;

           private:
            zappy::server::Client &_user;
            zappy::game::player::InventoryServer _inventory;
        };

        class Team {
           public:
            Team(const std::string &name) : _name(name) {}

            ~Team() = default;

            std::string getName() const { return _name; }

            const std::vector<std::reference_wrapper<Player>>
            getPlayerList() const
            {
                return this->_playerList;
            }

            void addPlayer(Player &player)
            {
                this->_playerList.push_back(player);
            }

           private:
            const std::string _name;
            std::vector<std::reference_wrapper<Player>> _playerList;
        };
    }  // namespace game
}  // namespace zappy
