/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IFloor.hpp
*/

#pragma once

#include "raylib.h"

namespace zappy {
    namespace gui {
        namespace raylib {
            class IFloor {
                public:
                    virtual ~IFloor() = default;

                    // Setters
                    virtual void setSpacing(int spacing) = 0;
                    virtual void setWidth(int width) = 0;
                    virtual void setHeight(int height) = 0;

                    // Getters
                    virtual int getSpacing() const = 0;
                    virtual int getWidth() const = 0;
                    virtual int getHeight() const = 0;

                    // Draw
                    virtual void draw() const = 0;

            };
        }
    } // namespace gui
} // namespace zappy
