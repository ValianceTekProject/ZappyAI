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

                    // Setters
                    virtual void setGridSize(int size) = 0;
                    virtual void setSpacing(int spacing) = 0;

                    // Getters
                    virtual int getGridSize() const = 0;
                    virtual int getSpacing() const = 0;

            };
        }
    } // namespace gui
} // namespace zappy
