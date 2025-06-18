/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IPlayerModel.hpp
*/

#pragma once

#include "AssetPaths.hpp"

#include <iostream>
#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class IPlayerModel {
                public:
                    enum class State {
                        IDLE,
                        WALK,
                        EJECTED
                    };

                    virtual ~IPlayerModel() = default;

                    virtual void init() = 0;

                    // Setters
                    virtual void setPosition(const Vector3 &position) = 0;
                    virtual void setRotation(const Vector3 &rotation) = 0;
                    virtual void setScale(const float &scale) = 0;
                    virtual void setOrigin(const Vector3 &origin) = 0;

                    // Getters
                    virtual int getId() const = 0;
                    virtual Vector3 getPosition() const = 0;
                    virtual Vector3 getRotation() const = 0;
                    virtual float getScale() const = 0;
                    virtual Vector3 getOrigin() const = 0;
                    virtual State getState() const = 0;

                    virtual void update() = 0;

                    virtual void idle() = 0;
                    virtual void walk() = 0;
                    virtual void ejected() = 0;

                    virtual void render() = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
