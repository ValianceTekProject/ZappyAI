/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#include "Game.hpp"
#include <chrono>
#include <csignal>
#include <cstdlib>
#include <thread>
#include "Data/Game/Resource.hpp"
#include "Server.hpp"

void zappy::game::MapServer::mapInit()
{
    std::srand(std::time({}));
    int randX = 0;
    int randY = 0;
    int width = getWidth();
    int height = getHeight();

    for (unsigned i = 0; i < zappy::game::coeff.size(); i += 1) {
        for (int j = 0; j < (coeff[i] * width * height); j += 1) {
            randX = std::rand() % width;
            randY = std::rand() % height;
            zappy::game::Tile tileTmp = getTile(randX, randY);
            tileTmp.addResource(static_cast<zappy::game::Resource>(i), 1);
        }
    }
}

void zappy::game::Game::gameLoop()
{
    this->_map.init(_map.getWidth(), _map.getHeight());
    this->_map.mapInit();
    this->_isRunning = true;

    while (this->_isRunning) {
        // à enlever plus tard
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
}
