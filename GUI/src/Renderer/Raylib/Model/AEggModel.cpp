/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AEggModel.cpp
*/

#include "AEggModel.hpp"

zappy::gui::raylib::AEggModel::AEggModel(const int &id) :
    AModel::AModel(),
    _id(id),
    _state(State::IDLE),
    _gamePosition(Vector2{0, 0}),
    _modelAnimations(nullptr),
    _animsCount(0),
    _animCurrentFrame(0)
{
    this->_animationIndexMap[State::IDLE] = 0;
    this->_animationIndexMap[State::OPEN] = 0;

    this->_animationIndexMap[State::IDLE] = 0;
    this->_animationIndexMap[State::OPEN] = 0;
}

void zappy::gui::raylib::AEggModel::init()
{
    AModel::init();
}

void zappy::gui::raylib::AEggModel::update(const float &deltaUnits)
{
    ModelAnimation anim = this->_modelAnimations[this->_animationIndexMap[this->_state]];
    float speed = (this->_animationFrameSpeedMap[this->_state]);

    this->_frameAccumulator += deltaUnits * speed;

    while (this->_frameAccumulator >= 1.0f) {
        this->_animCurrentFrame = (this->_animCurrentFrame + 1) % anim.frameCount;
        this->_frameAccumulator -= 1.0f;
    }

    UpdateModelAnimation(this->_model, anim, this->_animCurrentFrame);
}

void zappy::gui::raylib::AEggModel::idle()
{
    this->_state = State::IDLE;
    this->_animCurrentFrame = 0;
}

void zappy::gui::raylib::AEggModel::open()
{
    this->_state = State::OPEN;
    this->_animCurrentFrame = 0;
}

void zappy::gui::raylib::AEggModel::_initModel(const std::string &modelPath)
{
    AModel::_initModel(modelPath);
    this->_modelAnimations = LoadModelAnimations(modelPath.c_str(), &this->_animsCount);
}
