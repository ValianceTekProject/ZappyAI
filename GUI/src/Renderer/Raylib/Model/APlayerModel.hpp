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
                    APlayerModel(const int &id);
                    virtual ~APlayerModel() override = default;

                    virtual void init() override = 0;

                    // Setters
                    void setPosition(const Vector3 &position) override { _position = position; }
                    void setRotation(const Vector3 &rotation) override { _rotation = rotation; }
                    void setScale(const Vector3 &scale) override { _scale = scale; }
                    void setOrigin(const Vector3 &origin) override { _origin = origin; }

                    // Getters
                    int getId() const override { return _id; }
                    Vector3 getPosition() const override { return _position; }
                    Vector3 getRotation() const override { return _rotation; }
                    Vector3 getScale() const override { return _scale; }
                    Vector3 getOrigin() const override { return _origin; }
                    State getState() const override { return _state; }

                    virtual void update() override = 0;

                    virtual void idle() override { _state = State::IDLE; }
                    virtual void walk() override { _state = State::WALK; }
                    virtual void ejected() override { _state = State::EJECTED; }

                    virtual void render() override = 0;

                protected:
                    virtual void _initModel() = 0;

                    int _id;

                    State _state;

                    Model _model;

                    Vector3 _position;
                    Vector3 _rotation;
                    Vector3 _scale;

                    Vector3 _origin;

                    int _animsCount;
                    unsigned int _animIndex;
                    unsigned int _animCurrentFrame;
                    ModelAnimation *_modelAnimations;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
