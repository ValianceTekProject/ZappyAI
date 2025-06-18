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
                Map(const size_t &width = 0, const size_t &height = 0) { _init(width, height); }
                ~Map() = default;

                const size_t &getWidth() const { return this->_width; }
                const size_t &getHeight() const { return this->_height; }

                Tile &getTile(const size_t &x, const size_t &y) { return this->_map[x][y]; }
                const Tile &getTile(const size_t &x, const size_t &y) const { return this->_map[x][y]; }

                size_t getResourceQuantity(const Resource &type) const;

                void clearTile(const size_t &x, const size_t &y);
                void clear();

                void setTile(const size_t &x, const size_t &y, const Tile &tile);

            protected:
                void _init(const size_t &width, const size_t &height);

                size_t _width;
                size_t _height;

                std::vector<std::vector<Tile>> _map;
        };
    }
}
