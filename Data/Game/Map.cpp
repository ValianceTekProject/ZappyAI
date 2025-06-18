/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameMap.cpp
*/

#include "Map.hpp"

void zappy::game::Map::_init(const size_t &width, const size_t &height)
{
    this->_width = width;
    _height = height;

    this->_map.resize(width, std::vector<Tile>(height));
}

size_t zappy::game::Map::getResourceQuantity(const Resource &type) const
{
    size_t quantity = 0;

    for (auto &row : this->_map) {
        for (auto &tile : row)
            quantity += tile.getResourceQuantity(type);
    }
    return quantity;
}

void zappy::game::Map::clearTile(const size_t &x, const size_t &y)
{
    if (x >= this->_width || y >= _height)
        return;
    this->_map[x][y].clear();
}

void zappy::game::Map::clear()
{
    for (auto &row : this->_map) {
        for (auto &tile : row)
            tile.clear();
    }
}

void zappy::game::Map::setTile(const size_t &x, const size_t &y, const Tile &tile)
{
    this->_map[x][y] = tile;
}
