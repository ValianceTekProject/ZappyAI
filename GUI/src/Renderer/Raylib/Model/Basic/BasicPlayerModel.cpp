/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BasicPlayerModel.cpp
*/

#include "BasicPlayerModel.hpp"

#include <raylib.h>
#include <stdio.h>

zappy::gui::raylib::BasicPlayerModel::BasicPlayerModel(const int &id) : APlayerModel::APlayerModel(id)
{
    constexpr float scale = 0.2;
    setScale(scale);
}

void zappy::gui::raylib::BasicPlayerModel::init()
{
    _initModel();
}

void zappy::gui::raylib::BasicPlayerModel::update()
{
    ModelAnimation anim = _modelAnimations[_animIndex];

    _animCurrentFrame = (_animCurrentFrame + 1) % anim.frameCount;
    UpdateModelAnimation(_model, anim, _animCurrentFrame);
}

void zappy::gui::raylib::BasicPlayerModel::render()
{
    DrawModel(_model, _position, getScale(), WHITE);
}

void zappy::gui::raylib::BasicPlayerModel::_initModel()
{
    _model = LoadModel(assets::BASIC_PLAYER_PATH.c_str());
    if (_model.meshCount == 0) {
        // erreur chargement modèle
        std::cout << assets::BASIC_PLAYER_PATH.c_str() << "Modele non chargé" << std::endl;
    }
    _modelAnimations = LoadModelAnimations(assets::BASIC_PLAYER_PATH.c_str(), &_animsCount);
}
