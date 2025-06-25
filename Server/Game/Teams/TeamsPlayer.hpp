//
// EPITECH PROJECT, 2025
// Teams
// File description:
// Teams
//

#pragma once

#include "ATeams.hpp"

namespace zappy {
    namespace game {
        class ServerPlayer;
        class TeamsPlayer : public ATeams {
           public:
            TeamsPlayer(const std::string &name, int id) : ATeams(name, id) {}

            ~TeamsPlayer() = default;

            void setClientNb( const int clientNb) { _clientNb = clientNb; }
            int getClientNb() const { return this->_clientNb; }
            void allowNewPlayer();

           private:
            int _clientNb;
            std::mutex _clientNbLock;
        };
    }  // namespace game
}  // namespace zappy
