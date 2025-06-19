/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** AEggModel.cpp
*/

#include "AEggModel.hpp"

zappy::gui::raylib::AEggModel::AEggModel(const int &id) :
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
{}

void zappy::gui::raylib::AEggModel::init()
{

}

Vector3 zappy::gui::raylib::AEggModel::getHeadOrigin() const
{
    return Vector3{
        _position.x + _headOrigin.x * _scale,
        _position.y + _headOrigin.y * _scale,
        _position.z + _headOrigin.z * _scale
    };
}

void zappy::gui::raylib::AEggModel::rotate(const Vector3 &rotation)
{
    // rotate Model with rotation vector
    (void)rotation;
}