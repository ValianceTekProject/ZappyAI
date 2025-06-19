/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AEggModel.hpp
*/

#pragma once

#include "IEggModel.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class AEggModel : public IEggModel {
                public:
                    AEggModel(const int &id);
                    virtual ~AEggModel() override = default;

                    virtual void init() override = 0;

                    // Setters
                    void setGamePosition(const Vector2 &position) override { _gamePosition = position; }
                    void setPosition(const Vector3 &position) override { _position = position; }

                    void setScale(const float &scale) override { _scale = scale; }
                    void setHeadOrigin(const Vector3 &origin) override { _headOrigin = origin; }

                    // Getters
                    int getId() const override { return _id; }
                    State getState() const override { return _state; }

                    Vector2 getGamePosition() const override { return _gamePosition; }
                    Vector3 getPosition() const override { return _position; }

                    game::Orientation getOrientation() const override { return _orientation; }

                    float getScale() const override { return _scale; }
                    Vector3 getHeadOrigin() const override;

                    void rotate(const Vector3 &rotation) override;

                    virtual void update() override = 0;

                    virtual void idle() override { _state = State::IDLE; }
                    virtual void opened() override { _state = State::OPENED; }

                    virtual void render() override = 0;

                protected:
                    virtual void _initModel() = 0;

                    int _id;

                    State _state;

                    Vector2 _gamePosition;
                    game::Orientation _orientation;

                    Vector3 _position;
                    Vector3 _headOrigin;
                    float _scale;

                    Model _model;

                    int _animsCount;
                    unsigned int _animIndex;
                    unsigned int _animCurrentFrame;
                    ModelAnimation *_modelAnimations;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
