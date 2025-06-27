/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** BasicResourceModel.cpp
*/

#include "BasicResourceModel.hpp"
#include "Resource.hpp"
#include <unordered_map>

zappy::gui::raylib::BasicResourceModel::BasicResourceModel(const int &id, const zappy::game::Resource &resourceType) : AResourceModel::AResourceModel(id, resourceType)
{
    constexpr float scale = 0.1;
    setScale(scale);
}

void zappy::gui::raylib::BasicResourceModel::init()
{
    AResourceModel::init();
    _scale = 0.8f;

    static const std::unordered_map<zappy::game::Resource, std::string> modelPaths = {
        { zappy::game::Resource::FOOD, assets::BASIC_FOOD_PATH },
        { zappy::game::Resource::LINEMATE, assets::BASIC_LINEMATE_PATH },
        { zappy::game::Resource::DERAUMERE, assets::BASIC_DERAUMERE_PATH },
        { zappy::game::Resource::SIBUR, assets::BASIC_SIBUR_PATH },
        { zappy::game::Resource::MENDIANE, assets::BASIC_MENDIANE_PATH },
        { zappy::game::Resource::PHIRAS, assets::BASIC_PHIRAS_PATH },
        { zappy::game::Resource::THYSTAME, assets::BASIC_THYSTAME_PATH }
    };

    static const std::unordered_map<zappy::game::Resource, float> resourceScales = {
        { zappy::game::Resource::FOOD, 0.002f },
        { zappy::game::Resource::LINEMATE, 0.2f },
        { zappy::game::Resource::DERAUMERE, 0.05f },
        { zappy::game::Resource::SIBUR, 0.08f },
        { zappy::game::Resource::MENDIANE, 0.08f },
        { zappy::game::Resource::PHIRAS, 0.003f },
        { zappy::game::Resource::THYSTAME, 0.2f }
    };

    auto modelIt = modelPaths.find(_resourceType);
    if (modelIt == modelPaths.end()) {
        throw RendererError(zappy::game::getName(_resourceType) + " is not a valid resource", "BasicResourceModel");
    }

    AResourceModel::_initModel(modelIt->second);

    if (_scale <= 0.0f) _scale = 1.0f;

    auto scaleIt = resourceScales.find(_resourceType);
    if (scaleIt != resourceScales.end()) {
        setScale(scaleIt->second * _scale);
    } else {
        setScale(_scale);
    }
}
