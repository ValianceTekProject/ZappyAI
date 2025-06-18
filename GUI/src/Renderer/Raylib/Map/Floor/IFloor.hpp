/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IFloor.hpp
*/

#pragma once

#include "Map.hpp"
#include "raylib.h"
#include "AssetPaths.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class IFloor {
                public:
                    virtual ~IFloor() = default;

                    virtual void init() = 0;
                    virtual void update() const = 0;
                    virtual void render() const = 0;

                    // Setters
                    virtual void setWidth(const size_t &width) = 0;
                    virtual void setHeight(const size_t &height) = 0;
                    virtual void setTileSize(const float &tileSize) = 0;

                    // Getters
                    virtual size_t getWidth() const = 0;
                    virtual size_t getHeight() const = 0;
                    virtual float getTileSize() const = 0;

                    virtual Vector3 get3DCoords(const size_t &x, const size_t &y) const = 0;
            };
        }
    } // namespace gui
} // namespace zappy
