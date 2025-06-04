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
                Map(const size_t &width, const size_t &height) { init(width, height); }
                ~Map() = default;

                const size_t &getWidth() const { return this->_width; }
                const size_t &getHeight() const { return this->_height; }

                Tile &getTile(const size_t &x, const size_t &y) { return this->_map[x][y]; }
                const Tile &getTile(const size_t &x, const size_t &y) const { return this->_map[x][y]; }

                void clearTile(const size_t &x, const size_t &y);
                void clear();

                void setTile(const size_t &x, const size_t &y, const Tile &tile);

            private:
                void init(const size_t &width, const size_t &height);

                size_t _width;
                size_t _height;

                std::vector<std::vector<Tile>> _map;
        };
    }
}
