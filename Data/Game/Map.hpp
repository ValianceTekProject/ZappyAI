/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Map.hpp
*/

#pragma once

#include "Tile.hpp"

#include <vector>

namespace zappy {
    namespace game {
        class Map
        {
            public:
                Map() = default;
                ~Map() = default;

                void init(int width, int height);

                int getWidth() const { return _width; }
                int getHeight() const { return _height; }

                Tile &getTile(int x, int y) { return _map[x][y]; }
                const Tile &getTile(int x, int y) const { return _map[x][y]; }

                void clearTile(int x, int y);
                void clear();

                void setTile(int x, int y, Tile &tile);

            private:
                int _width;
                int _height;

                std::vector<std::vector<Tile>> _map;
        };
    }
}
