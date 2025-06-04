//
// EPITECH PROJECT, 2025
// Player
// File description:
// Player
//

#pragma once

#include "Client.hpp"

namespace zappy {
    namespace game {
        class ServerPlayer {

           public:
            explicit ServerPlayer(zappy::server::Client user) : _user(std::move(user)) {}
            ~ServerPlayer() = default;

            zappy::server::Client &getClient() {return this->_user;};

           private:
            zappy::server::Client _user;
            zappy::game::player::InventoryServer _inventory;
        };
    }
}
