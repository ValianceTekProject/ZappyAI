/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** BasicEggModel.cpp
*/

#include "BasicEggModel.hpp"

#include <raylib.h>
#include <stdio.h>

zappy::gui::raylib::BasicEggModel::BasicEggModel(const int &id) : AEggModel::AEggModel(id)
{
    constexpr float scale = 0.2;
    setScale(scale);
}

void zappy::gui::raylib::BasicEggModel::init()
{
    _initModel();
}

void zappy::gui::raylib::BasicEggModel::update()
{
    ModelAnimation anim = _modelAnimations[_animIndex];
    _animCurrentFrame = (_animCurrentFrame + 1)%anim.frameCount;
    UpdateModelAnimation(_model, anim, _animCurrentFrame);
}

void zappy::gui::raylib::BasicEggModel::render()
{
    DrawModel(_model, _position, getScale(), WHITE);
}

void zappy::gui::raylib::BasicEggModel::_initModel()
{
    _model = LoadModel(assets::BASIC_EGG_PATH.c_str());
    if (_model.meshCount == 0) {
        // erreur chargement modèle
        std::cout << assets::BASIC_EGG_PATH.c_str() << "Modele non chargé" << std::endl;
    }
    _modelAnimations = LoadModelAnimations(assets::BASIC_EGG_PATH.c_str(), &_animsCount);
}
