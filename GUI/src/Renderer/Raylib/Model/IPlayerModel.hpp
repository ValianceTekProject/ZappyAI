/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IPlayerModel.hpp
*/

#pragma once

#include "AssetPaths.hpp"
#include "Player.hpp"

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
                    virtual void setGamePosition(const Vector2 &position) = 0;
                    virtual void setPosition(const Vector3 &position) = 0;

                    virtual void setScale(const float &scale) = 0;
                    virtual void setHeadOrigin(const Vector3 &origin) = 0;

                    // Getters
                    virtual int getId() const = 0;
                    virtual State getState() const = 0;

                    virtual Vector2 getGamePosition() const = 0;
                    virtual Vector3 getPosition() const = 0;
                    virtual game::Orientation getOrientation() const = 0;
                    virtual Vector3 getHeadOrigin() const = 0;

                    virtual float getScale() const = 0;

                    virtual void rotate(const Vector3 &rotation) = 0;

                    virtual void look(const game::Orientation &orientation) = 0;
                    virtual void lookLeft() = 0;
                    virtual void lookRight() = 0;

                    virtual void update() = 0;

                    virtual void idle() = 0;
                    virtual void walk() = 0;
                    virtual void ejected() = 0;

                    virtual void render() = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
