//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include <functional>
#include <string>
#include <vector>
#include <queue>

#include "Inventory.hpp"

namespace zappy {
    namespace server {

        enum class ClientState {
            WAITING_TEAM_NAME,
            CONNECTED,
        };

        class User {
            public:
                User(int socket) : _socket(socket), _state(ClientState::WAITING_TEAM_NAME) {};
                ~User() = default;

                int getSocket() const { return _socket; }

                ClientState getState() const { return _state; }
                void setState(ClientState state) { _state = state; }

                std::queue<std::string> queueMessage;
            private:
                int _socket;
                ClientState _state;
        };
    }
    namespace game {
        class Player {
            
            public:
                Player(zappy::server::User &user) : _user(user) {}
                ~Player() = default;

            private:
                zappy::server::User &_user;
                zappy::game::player::InventoryServer _inventory;
        };

        class Team {
            public:
                Team(const std::string &name) : _name(name) {}
                ~Team() = default;

                std::string getName() const { return _name; }

                const std::vector<std::reference_wrapper<Player>> getPlayerList() const
                {
                    return this->_playerList;
                }

                void addPlayer(Player &player) { this->_playerList.push_back(player); }

            private:
                const std::string _name;
                std::vector<std::reference_wrapper<Player>> _playerList;
        };
    }
}
