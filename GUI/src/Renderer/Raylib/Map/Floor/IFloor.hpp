/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IFloor.hpp
*/

#pragma once

#include "Map.hpp"
#include "raylib.h"

namespace zappy {
    namespace gui {
        namespace raylib {
            class IFloor {
                public:
                    virtual ~IFloor() = default;

                    virtual void init() = 0;

                    // Setters
                    virtual void setWidth(size_t width) = 0;
                    virtual void setHeight(size_t height) = 0;
                    virtual void setTileSize(size_t tileSize) = 0;

                    // Getters
                    virtual size_t getWidth() const = 0;
                    virtual size_t getHeight() const = 0;
                    virtual size_t getTileSize() const = 0;

                    virtual void render() const = 0;
            };
        }
    } // namespace gui
} // namespace zappy
