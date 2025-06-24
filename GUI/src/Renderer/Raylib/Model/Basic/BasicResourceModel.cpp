/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** BasicResourceModel.cpp
*/

#include "BasicResourceModel.hpp"

zappy::gui::raylib::BasicResourceModel::BasicResourceModel(const int &id, const zappy::game::Resource &resourceType) : AResourceModel::AResourceModel(id, resourceType)
{
    constexpr float scale = 0.1;
    setScale(scale);
}

void zappy::gui::raylib::BasicResourceModel::init()
{
    AResourceModel::init();
    std::string modelPath = "";

    if (_resourceType == game::Resource::FOOD) {
        modelPath = assets::BASIC_FOOD_PATH;
    } else if (_resourceType == game::Resource::LINEMATE) {
        modelPath = assets::BASIC_LINEMATE_PATH;
    } else if (_resourceType == game::Resource::DERAUMERE) {
        modelPath = assets::BASIC_DERAUMERE_PATH;
    } else if (_resourceType == game::Resource::SIBUR) {
        modelPath = assets::BASIC_SIBUR_PATH;
    } else if (_resourceType == game::Resource::MENDIANE) {
        modelPath = assets::BASIC_MENDIANE_PATH;
    } else if (_resourceType == game::Resource::PHIRAS) {
        modelPath = assets::BASIC_PHIRAS_PATH;
    } else if (_resourceType == game::Resource::THYSTAME) {
        modelPath = assets::BASIC_THYSTAME_PATH;
    } else {
        throw RendererError(zappy::game::getName(_resourceType) + " is not a valid resource", "BasicResourceModel");
    }

    AResourceModel::_initModel(modelPath);
}

void zappy::gui::raylib::BasicResourceModel::update()
{
    AResourceModel::update();
}
