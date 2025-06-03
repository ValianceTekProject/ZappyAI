/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#include "Game.hpp" 
#include <thread>

void zappy::game::Game::gameLoop()
{
    this->_map.init(_map.getWidth(), _map.getHeight());
    this->_map.mapInit();
    this->_isRunning = true;
    auto lastUpdate = std::chrono::steady_clock::now();

    while (this->_isRunning) {
        auto now = std::chrono::steady_clock::now();
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            now - lastUpdate);

        if (elapsed >= this->_baseFreqMs) {
            this->_playTurn();
            lastUpdate = now;
            continue;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}
