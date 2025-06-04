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
#include "Player/Player.hpp"
#include <memory>
#include <mutex>
#include <queue>
#include <string>

namespace zappy {
    namespace game {
        class Team {
           public:
            Team(const std::string &name) : _name(name) {}

            ~Team() = default;

            Team(Team&&) noexcept = default;
            std::string getName() const { return _name; }

            const std::vector<std::unique_ptr<ServerPlayer>> &getPlayerList() const
            {
                return this->_playerList;
            }

            void addPlayer(std::unique_ptr<ServerPlayer> player)
            {
                this->_playerList.push_back(std::move(player));
            }

           private:
            const std::string _name;
            std::vector<std::unique_ptr<ServerPlayer>> _playerList;
        };
    }  // namespace game
}  // namespace zappy
