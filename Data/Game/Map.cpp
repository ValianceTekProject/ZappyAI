/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameMap.cpp
*/

#include "Map.hpp"

void zappy::game::Map::init(int width, int height)
{
    _width = width;
    _height = height;

    _map.resize(width);
    for (int i = 0; i < width; i++) {
        _map[i].resize(height);
        for (int j = 0; j < height; j++)
            _map[i][j] = Tile();
    }
}

void zappy::game::Map::clearTile(int x, int y)
{
    _map[x][y].clear();
}

void zappy::game::Map::clear()
{
    for (int i = 0; i < _width; i++)
        for (int j = 0; j < _height; j++)
            clearTile(i, j);
}

void zappy::game::Map::setTile(int x, int y, Tile &tile)
{
    _map[x][y] = tile;
}
