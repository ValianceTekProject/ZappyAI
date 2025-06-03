/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#include "Game.hpp" 
#include "Server.hpp"
#include <thread>

void zappy::game::Game::gameLoop()
{
    this->_map.init(_map.getWidth(), _map.getHeight());
    this->_map.mapInit();
    this->_isRunning = RunningState::RUN;
    auto lastUpdate = std::chrono::steady_clock::now();

    while (this->_isRunning != RunningState::STOP) {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            now - lastUpdate);
        for (auto &team : this->getTeamList()) {
            for (auto &player : team.getPlayerList()) {
                if (!player->getClient().queueMessage.empty()) {
                    this->_commandHandler.processClientInput(player->getClient().queueMessage.front(), *player);
                    player->getClient().queueMessage.pop();
                }
            }
        }
        if (elapsed >= static_cast<std::chrono::seconds>(this->_baseFreqMs)) {
            this->_playTurn();
            lastUpdate = now;
            continue;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1)); // temporaire
    }
}
