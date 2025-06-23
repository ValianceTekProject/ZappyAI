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
            Team(const std::string &name, int id) : _name(name), _teamId(id) {}

            ~Team() = default;

            Team(const Team&& other);
            std::string getName() const { return this->_name; }
            void setClientNb( const int clientNb) { _clientNb = clientNb; }
            int getClientNb() const { return this->_clientNb; }
            void allowNewPlayer();
            void removePlayer(int playerSocket);

            const std::vector<std::shared_ptr<ServerPlayer>> &getPlayerList() const;

            void addPlayer(std::shared_ptr<ServerPlayer> player);
            int getTeamId() const {return this->_teamId;}

           private:
            const std::string _name;
            int _teamId;
            int _clientNb;
            std::vector<std::shared_ptr<ServerPlayer>> _playerList;
            std::mutex _clientNbLock;
            std::mutex _playerListLock;
        };
    }  // namespace game
}  // namespace zappy
