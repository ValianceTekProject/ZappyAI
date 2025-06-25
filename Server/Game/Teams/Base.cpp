//
// EPITECH PROJECT, 2025
// Base
// File description:
// Base
//

#include "TeamsPlayer.hpp"
#include <mutex>

void zappy::game::TeamsPlayer::allowNewPlayer()
{
    std::lock_guard<std::mutex> lock(this->_clientNbLock);
    this->_clientNb += 1;
}
