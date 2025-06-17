//
// EPITECH PROJECT, 2025
// Teams
// File description:
// Teams
//

#pragma once

#include "Client.hpp"
#include "Player.hpp"
#include "Inventory.hpp"
#include "ServerPlayer.hpp"
#include <memory>
#include <mutex>
#include <queue>
#include <string>

namespace zappy {
    namespace game {
        class ServerPlayer;
        class Team {
           public:
            Team(const std::string &name) : _name(name) {}

            ~Team() = default;

            Team(Team&&) noexcept = default;
            std::string getName() const { return this->_name; }
            void setClientNb( const int clientNb) { _clientNb = clientNb; }
            int &getClientNb() { return this->_clientNb; }
            void removePlayer(int playerSocket);

            const std::vector<std::shared_ptr<ServerPlayer>> &getPlayerList() const;

            void addPlayer(std::shared_ptr<ServerPlayer> player);

           private:
            const std::string _name;
            int _clientNb;
            std::vector<std::shared_ptr<ServerPlayer>> _playerList;
        };
    }  // namespace game
}  // namespace zappy
