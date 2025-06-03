//
// EPITECH PROJECT, 2025
// Map
// File description:
// Base functions for map
//

#include "Data/Game/Resource.hpp"
#include "Map.hpp"
#include <chrono>

void zappy::game::MapServer::mapInit()
{
    std::srand(std::time({}));

    int mapWidth = this->getWidth();
    int mapHeight = this->getHeight();
    size_t nbResources = zappy::game::coeff.size();

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
