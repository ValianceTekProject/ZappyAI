//
// EPITECH PROJECT, 2025
// Base
// File description:
// Base
//

#include "Teams.hpp"
const std::vector<std::shared_ptr<zappy::game::ServerPlayer>> &zappy::game::Team::getPlayerList() const
{
    return this->_playerList;
}

void zappy::game::Team::addPlayer(std::shared_ptr<ServerPlayer> player)
{
    this->_playerList.push_back(std::move(player));
}

void zappy::game::Team::removePlayer(int clientSocket)
{
    for (auto it = this->_playerList.begin(); it != this->_playerList.end(); it += 1) {
        if ((*it)->getClient().getSocket() == clientSocket) {
            this->_playerList.erase(it);
            return;
        }
    }
}
