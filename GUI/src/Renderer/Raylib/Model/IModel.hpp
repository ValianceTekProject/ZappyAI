/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IModel.hpp
*/

#pragma once

#include "AssetPaths.hpp"

#include <iostream>
#include <raylib.h>
#include <raymath.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class IModel {
                public:
                    virtual ~IModel() = default;

                    virtual void init() = 0;

                    // Setters
                    virtual void setPosition(const Vector3 &position) = 0;

                    virtual void setScale(const float &scale) = 0;
                    virtual void setRotation(const Vector3 &rotation) = 0;

                    virtual void setColor(const Color &color) = 0;

                    // Getters
                    virtual Vector3 getPosition() const = 0;

                    virtual float getScale() const = 0;
                    virtual Vector3 getRotation() const = 0;

                    virtual Color getColor() const = 0;

                    virtual void update(const float &deltaUnits) = 0;

                    virtual void scale(const float &scale) = 0;
                    virtual void translate(const Vector3 &translation) = 0;
                    virtual void rotate(const Vector3 &rotation) = 0;

                    virtual void render() = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
