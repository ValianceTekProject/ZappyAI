/*
** EPITECH PROJECT, 2024
** zappyGood
** File description:
** APlayerModel.hpp
*/

#pragma once

#include "IPlayerModel.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class APlayerModel : public IPlayerModel {
                public:
                    APlayerModel();
                    virtual ~APlayerModel() override = default;

                    virtual void init() override = 0;

                    // Setters
                    virtual void setPosition(const Vector3 &position) { _position = position; }
                    virtual void setRotation(const Vector3 &rotation) { _rotation = rotation; }
                    virtual void setScale(const Vector3 &scale) { _scale = scale; }
                    virtual void setOrigin(const Vector3 &origin) { _origin = origin; }

                    // Getters
                    virtual Vector3 getPosition() const { return _position; }
                    virtual Vector3 getRotation() const { return _rotation; }
                    virtual Vector3 getScale() const { return _scale; }
                    virtual Vector3 getOrigin() const { return _origin; }
                    virtual State getState() const { return _state; }

                    virtual void update() override = 0;

                    virtual void idle() override { _state = State::IDLE; }
                    virtual void walk() override { _state = State::WALK; }
                    virtual void ejected() override { _state = State::EJECTED; }

                    virtual void render() override = 0;

                protected:
                    virtual void _initModel() = 0;

                    State _state;

                    Model _model;

                    Vector3 _position;
                    Vector3 _rotation;
                    Vector3 _scale;

                    Vector3 _origin;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
