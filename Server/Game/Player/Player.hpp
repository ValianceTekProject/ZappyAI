//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include <chrono>

#include "Client.hpp"

namespace zappy {
    namespace game {
        class ServerPlayer {

           public:
            explicit ServerPlayer(zappy::server::Client user) : _user(std::move(user)), _startTime(std::chrono::steady_clock::now()) {}
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
