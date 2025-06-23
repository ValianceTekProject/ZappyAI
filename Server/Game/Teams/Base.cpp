//
// EPITECH PROJECT, 2025
// Base
// File description:
// Base
//

#include "Teams.hpp"
#include <mutex>

zappy::game::Team::Team(const Team &&other) : _name(other._name)
{
    this->_teamId = other._teamId;
    this->_clientNb = other._clientNb;
    this->_playerList = other._playerList;
}

void zappy::game::Team::allowNewPlayer()
{
    std::lock_guard<std::mutex> lock(this->_clientNbLock);
    this->_clientNb += 1;
}

const std::vector<std::shared_ptr<zappy::game::ServerPlayer>> &zappy::game::Team::getPlayerList() const
{
    return this->_playerList;
}

void zappy::game::Team::addPlayer(std::shared_ptr<ServerPlayer> player)
{
    std::lock_guard<std::mutex> lock(this->_playerListLock);
    this->_playerList.push_back(std::move(player));
}

void zappy::game::Team::removePlayer(int clientSocket)
{
    std::lock_guard<std::mutex> lock(this->_playerListLock);
    for (auto it = this->_playerList.begin(); it != this->_playerList.end(); it += 1) {
        if ((*it)->getClient().getSocket() == clientSocket) {
            this->_playerList.erase(it);
            return;
        }
    }
}
