//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include <chrono>

#include "Client.hpp"
#include "Player.hpp"
#include "Teams.hpp"
#include "ServerInventory.hpp"

namespace zappy {
    namespace game {
        class Team;

        class ServerPlayer : public Player {

           public:
            ServerPlayer(zappy::server::Client user,
                 size_t id,
                 size_t x,
                 size_t y,
                 Orientation orientation,
                 zappy::game::Team &team,
                 size_t level = 1
                )
                : Player::Player(id, x, y, orientation, level),
                _user(std::move(user)),
                _startTime(std::chrono::steady_clock::now()),
                _team(team) {}

            ~ServerPlayer() = default;

            zappy::server::Client &getClient() {return this->_user;};

            void startChrono() { _startTime = std::chrono::steady_clock::now(); }

            std::chrono::duration<double> getChrono() const {
                auto now = std::chrono::steady_clock::now();
                return now - _startTime;
            }

            bool isInAction() { return _actionStarted; }
            void setInAction(bool status) { _actionStarted = status; }
            zappy::game::Team &getTeam() { return _team; }


           private:
            zappy::server::Client _user;
            zappy::game::player::InventoryServer _inventory;
            std::chrono::steady_clock::time_point _startTime;

            bool _actionStarted = false;
            zappy::game::Team &_team;
        };
    }
}
