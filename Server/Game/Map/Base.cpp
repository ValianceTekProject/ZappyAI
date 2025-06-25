//
// EPITECH PROJECT, 2025
// Map
// File description:
// Base functions for map
//

#include "ServerMap.hpp"
#include <chrono>

zappy::game::MapServer::MapServer(int width, int height)
{
    std::srand(std::time({}));

    this->_width = width;
    this->_height = height;
    this->_init(width, height);
    this->_placeResources();
}

void zappy::game::MapServer::setEggsonMap(
    std::vector<std::shared_ptr<ITeams>> &teamList, int clientNb)
{
    std::srand(std::time(nullptr));
    for (int i = 0; i < static_cast<int>(clientNb * teamList.size()); i += 1) {
        size_t x = std::rand() % this->getWidth();
        size_t y = std::rand() % this->getHeight();
        zappy::game::Egg newEgg(this->_idEggTot, SERVER_FATHER_ID, x, y);
        this->_idEggTot += 1;
        this->_eggList.push(newEgg);
        this->addNewEgg(SERVER_FATHER_ID, x, y);
    }
}

void zappy::game::MapServer::addNewEgg(int teamId, int x, int y)
{
    zappy::game::Egg newEgg(this->_idEggTot, teamId, x, y);
    this->_idEggTot += 1;
    this->_eggList.push(newEgg);
}

zappy::game::Egg zappy::game::MapServer::popEgg()
{
    auto egg = this->_eggList.front();
    this->_eggList.pop();
    return egg;
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
