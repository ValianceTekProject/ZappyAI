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
    _animsCount(0),
    _animIndex(0),
    _animCurrentFrame(0),
    _modelAnimations(nullptr)
{}

void zappy::gui::raylib::AEggModel::init()
{
    AModel::init();
}

void zappy::gui::raylib::AEggModel::update()
{
    ModelAnimation anim = _modelAnimations[_animIndex];

    _animCurrentFrame = (_animCurrentFrame + 1) % anim.frameCount;
    UpdateModelAnimation(_model, anim, _animCurrentFrame);
}

void zappy::gui::raylib::AEggModel::_initModel(const std::string &modelPath)
{
    AModel::_initModel(modelPath);
    _modelAnimations = LoadModelAnimations(modelPath.c_str(), &_animsCount);

}
