/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** AResourceModel.cpp
*/

#include "AResourceModel.hpp"

zappy::gui::raylib::AResourceModel::AResourceModel(const int &id, const zappy::game::Resource &resourceType) :
    AModel::AModel(),
    _id(id),
    _gamePosition(Vector2{0, 0}),
    _resourceType(resourceType)
{}

void zappy::gui::raylib::AResourceModel::init()
{
    AModel::init();
}

void zappy::gui::raylib::AResourceModel::_initModel(const std::string &modelPath)
{
    AModel::_initModel(modelPath);
}
