/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** ATeams
*/

#include "ATeams.hpp"

void zappy::game::ATeams::removePlayer(int clientSocket)
{
    std::lock_guard<std::mutex> lock(this->_playerListLock);
    for (auto it = this->_playerList.begin(); it != this->_playerList.end(); it += 1) {
        if ((*it)->getClient().getSocket() == clientSocket) {
            this->_playerList.erase(it);
            return;
        }
    }
}

const std::vector<std::shared_ptr<zappy::game::ServerPlayer>> &zappy::game::ATeams::getPlayerList() const
{
    return this->_playerList;
}

void zappy::game::ATeams::addPlayer(std::shared_ptr<ServerPlayer> player)
{
    std::lock_guard<std::mutex> lock(this->_playerListLock);
    this->_playerList.push_back(std::move(player));
}