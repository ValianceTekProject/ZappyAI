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
    _model(),
    _position(Vector3{0, 0, 0}),
    _rotation(Vector3{0, 0, 0}),
    _scale(1),
    _origin(Vector3{0, 0, 0}),
    _animsCount(0),
    _animIndex(0),
    _animCurrentFrame(0),
    _modelAnimations()
{}

void zappy::gui::raylib::APlayerModel::init()
{

}