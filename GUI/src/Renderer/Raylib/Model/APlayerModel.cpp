/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** APlayerModel.cpp
*/

#include "APlayerModel.hpp"

zappy::gui::raylib::APlayerModel::APlayerModel(const int &id) :
    _id(id),
    _state(State::IDLE),
    _gamePosition(Vector2{0, 0}),
    _orientation(game::Orientation::NORTH),
    _position(Vector3{0, 0, 0}),
    _headOrigin(Vector3{0, 1, 0}),
    _scale(1),
    _model(),
    _animsCount(0),
    _animIndex(0),
    _animCurrentFrame(0),
    _modelAnimations()
{
    look(game::Orientation::NORTH);
}

void zappy::gui::raylib::APlayerModel::init()
{

}

Vector3 zappy::gui::raylib::APlayerModel::getHeadOrigin() const
{
    return Vector3{
        _position.x + _headOrigin.x * _scale,
        _position.y + _headOrigin.y * _scale,
        _position.z + _headOrigin.z * _scale
    };
}

void zappy::gui::raylib::APlayerModel::rotate(const Vector3 &rotation)
{
    // rotate Model with rotation vector
    (void)rotation;
}

void zappy::gui::raylib::APlayerModel::look(const game::Orientation &orientation)
{
    _orientation = orientation;
    // reotate model
}

void zappy::gui::raylib::APlayerModel::lookLeft()
{
    _orientation--;
    look(_orientation);
}

void zappy::gui::raylib::APlayerModel::lookRight()
{
    _orientation++;
    look(_orientation);
}
