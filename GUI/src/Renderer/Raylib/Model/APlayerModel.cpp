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
    _animsCount(0),
    _animIndex(0),
    _animCurrentFrame(0),
    _modelAnimations(nullptr)
{
    look(game::Orientation::NORTH);
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

void zappy::gui::raylib::APlayerModel::update()
{
    ModelAnimation anim = _modelAnimations[_animIndex];

    _animCurrentFrame = (_animCurrentFrame + 1) % anim.frameCount;
    UpdateModelAnimation(_model, anim, _animCurrentFrame);
}

void zappy::gui::raylib::APlayerModel::_initModel(const std::string &modelPath)
{
    AModel::_initModel(modelPath);
    _modelAnimations = LoadModelAnimations(modelPath.c_str(), &_animsCount);

}
