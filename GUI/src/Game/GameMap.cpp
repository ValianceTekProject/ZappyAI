/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameMap.cpp
*/

#include "GameMap.hpp"

void gui::GameMap::init(int width, int height)
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
