/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AEggModel.hpp
*/

#pragma once

#include "AModel.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class AEggModel : public AModel {
                public:
                    enum class State {
                        IDLE,
                        OPEN
                    };

                    AEggModel(const int &id);
                    virtual ~AEggModel() override = default;

                    virtual void init() override;

                    // Setters
                    void setGamePosition(const Vector2 &position) { this->_gamePosition = position; }

                    // Getters
                    int getId() const { return this->_id; }
                    State getState() const { return this->_state; }

                    Vector2 getGamePosition() const { return this->_gamePosition; }

                    virtual void update() override;

                    virtual void idle() { _state = State::IDLE; }
                    virtual void open() { _state = State::OPEN; }

                protected:
                    virtual void _initModel(const std::string &modelPath) override;

                    int _id;

                    State _state;

                    Vector2 _gamePosition;

                    int _animsCount;
                    unsigned int _animIndex;
                    unsigned int _animCurrentFrame;
                    ModelAnimation *_modelAnimations;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
