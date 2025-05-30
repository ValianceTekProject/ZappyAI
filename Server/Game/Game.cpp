/*
** EPITECH PROJECT, 2025
** Zappy
** File description:
** Game
*/

#include "Game.hpp"


void zappy::game::MapServer::mapInit()
{
    std::srand(std::time({}));
    int randX = 0;
    int randY = 0;
    int width = getWidth();
    int height = getHeight();

    for (int i = 0; i < coeff.size(); i += 1) {
        for (int j = 0; j < (coeff[i] * width * height); j += 1) {
            randX = std::rand() % width;
            randY = std::rand() % height;
            zappy::game::Tile tileTmp = getTile(randX, randY);
            tileTmp.addResource(static_cast<zappy::game::Ressource>(i), 1);
        }
    }
}

void zappy::game::Game::gameLoop()
{
    _map.init(_map.getWidth(), _map.getHeight());
    _map.mapInit();
    _isRunning = true;

    while (_isRunning) {
        
    }
}