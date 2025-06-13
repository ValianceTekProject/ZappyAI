//
// EPITECH PROJECT, 2025
// Teams
// File description:
// Teams
//

#pragma once

#include "Client.hpp"
#include "Data/Game/Player.hpp"
#include "Inventory.hpp"
#include "Player/ServerPlayer.hpp"
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
            void removePlayer(int playerSocket);

            const std::vector<std::unique_ptr<ServerPlayer>> &getPlayerList() const;

            void addPlayer(std::unique_ptr<ServerPlayer> player);

           private:
            const std::string _name;
            std::vector<std::unique_ptr<ServerPlayer>> _playerList;
        };
    }  // namespace game
}  // namespace zappy
