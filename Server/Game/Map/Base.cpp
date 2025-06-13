//
// EPITECH PROJECT, 2025
// Map
// File description:
// Base functions for map
//

#include "Data/Game/Resource.hpp"
#include "Map.hpp"
#include <chrono>

zappy::game::MapServer::MapServer(int width, int height)
{
    std::srand(std::time({}));

    this->_width = width;
    this->_height = height;
    this->_init(width, height);
    this->_placeResources();
}

void zappy::game::MapServer::_placeResources()
{
    size_t nbResources = zappy::game::coeff.size();
    auto mapWidth = this->_width;
    auto mapHeight = this->_height;

    for (size_t resourceIdx = 0; resourceIdx < nbResources; resourceIdx += 1) {
        int totalResources = coeff[resourceIdx] * mapWidth * mapHeight;

        for (int resourceCount = 0; resourceCount < totalResources;
            resourceCount += 1) {
            int randX = std::rand() % mapWidth;
            int randY = std::rand() % mapHeight;

            zappy::game::Tile &tile = this->getTile(randX, randY);
            tile.addResource(
                static_cast<zappy::game::Resource>(resourceIdx), 1);
        }
    }
}
