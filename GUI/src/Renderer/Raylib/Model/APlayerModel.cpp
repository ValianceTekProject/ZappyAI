/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** APlayerModel.cpp
*/

#include "APlayerModel.hpp"

zappy::gui::raylib::APlayerModel::APlayerModel(const int &id) :
    AModel::AModel(),
    _id(id),
    _state(State::IDLE),
    _gamePosition(Vector2{0, 0}),
    _orientation(game::Orientation::NORTH),
    _headOrigin(Vector3{0, 1, 0}),
    _modelAnimations(nullptr),
    _animsCount(0),
    _animCurrentFrame(0)
{
    this->_animationIndexMap[State::IDLE] = 0;
    this->_animationIndexMap[State::WALK] = 0;
    this->_animationIndexMap[State::EJECT] = 0;

    this->_animationIndexMap[State::IDLE] = 0;
    this->_animationIndexMap[State::WALK] = 0;
    this->_animationIndexMap[State::EJECT] = 0;
}

void zappy::gui::raylib::APlayerModel::init()
{
    AModel::init();
}

Vector3 zappy::gui::raylib::APlayerModel::getHeadOrigin() const
{
    return Vector3{
        this->_position.x + this->_headOrigin.x * this->_scale,
        this->_position.y + this->_headOrigin.y * this->_scale,
        this->_position.z + this->_headOrigin.z * this->_scale
    };
}

void zappy::gui::raylib::APlayerModel::look(const game::Orientation &orientation)
{
    if (this->_orientation == orientation)
        return;

    if (orientation - 1 == this->_orientation) {
        AModel::rotate(Vector3{0, -90, 0});
    } else if (orientation + 1 == this->_orientation) {
        AModel::rotate(Vector3{0, 90, 0});
    } else {
        AModel::rotate(Vector3{0, 180, 0});
    }
    this->_orientation = orientation;
}

void zappy::gui::raylib::APlayerModel::lookLeft()
{
    this->_orientation--;
}

void zappy::gui::raylib::APlayerModel::lookRight()
{
    this->_orientation++;
}

void zappy::gui::raylib::APlayerModel::update(const float &deltaUnits)
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

void zappy::gui::raylib::APlayerModel::idle()
{
    this->_state = State::IDLE;
    this->_animCurrentFrame = 0;
}

void zappy::gui::raylib::APlayerModel::walk()
{
    this->_state = State::WALK;
}

void zappy::gui::raylib::APlayerModel::eject()
{
    this->_state = State::EJECT;
}

void zappy::gui::raylib::APlayerModel::_initModel(const std::string &modelPath)
{
    AModel::_initModel(modelPath);
    this->_modelAnimations = LoadModelAnimations(modelPath.c_str(), &this->_animsCount);
}
