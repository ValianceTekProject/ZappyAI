//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include <chrono>

#include "Client.hpp"
#include "Data/Game/Player.hpp"
#include "Teams/Teams.hpp"

namespace zappy {
    namespace game {
        class ServerPlayer : public Player {

           public:
            ServerPlayer(zappy::server::Client user,
                 size_t id,
                 size_t x,
                 size_t y,
                 Orientation orientation,
                 size_t level = 1)
                : Player(id, x, y, orientation, level),
                _user(std::move(user)),
                _startTime(std::chrono::steady_clock::now()) {}

            ~ServerPlayer() = default;

            zappy::server::Client &getClient() {return this->_user;};

            void startChrono() { _startTime = std::chrono::steady_clock::now(); }

            std::chrono::duration<double> getChrono() const {
                auto now = std::chrono::steady_clock::now();
                return now - _startTime;
            }

            bool getChonoStart() { return _chronoStarted; }
            void setChronoStart(bool status) { _chronoStarted = status; }


           private:
            zappy::server::Client _user;
            zappy::game::player::InventoryServer _inventory;
            std::chrono::steady_clock::time_point _startTime;

            bool _chronoStarted = false;
        };
    }
}
