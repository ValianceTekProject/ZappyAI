/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AEggModel.hpp
*/

#pragma once

#include "AModel.hpp"

#include <map>

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

                    virtual void update(const float &deltaUnits) override;

                    void idle();
                    void open();

                protected:
                    virtual void _initModel(const std::string &modelPath) override;

                    int _id;

                    State _state;

                    Vector2 _gamePosition;

                    ModelAnimation *_modelAnimations;

                    int _animsCount;
                    unsigned int _animCurrentFrame;
                    float _frameAccumulator;

                    std::map<State, int> _animationIndexMap;
                    std::map<State, float> _animationFrameSpeedMap;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
