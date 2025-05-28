/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** GameMap.hpp
*/

#pragma once

#include "Tile.hpp"

#include <vector>

namespace gui {
    class GameMap
    {
        public:
            GameMap() = default;
            ~GameMap() = default;

            void init(int width, int height);

            int getWidth() const { return _width; }
            int getHeight() const { return _height; }

            Tile &getTile(int x, int y) { return _map[x][y]; }
            const Tile &getTile(int x, int y) const { return _map[x][y]; }

            void clear();
            void setTile(int x, int y, Tile &tile);
            void clearTile(int x, int y);

        private:
            int _width;
            int _height;

            std::vector<std::vector<Tile>> _map;
    };
}
