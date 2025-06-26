/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** IncantationEffectFactory.cpp
*/

#include "IncantationEffectFactory.hpp"

const std::array<zappy::gui::raylib::IncantationEffectFactory::CreateMethod, zappy::gui::raylib::INCANTATION_EFFECT_COUNT> zappy::gui::raylib::IncantationEffectFactory::_createMethods = {
    &zappy::gui::raylib::IncantationEffectFactory::createWave
};

std::unique_ptr<zappy::gui::raylib::IIncantationEffect> zappy::gui::raylib::IncantationEffectFactory::create(
    const IncantationType &type,
    const int &playerId,
    const float &duration,
    const Color &color
) {
    return _createMethods[static_cast<size_t>(type)](playerId, duration, color);
}

std::unique_ptr<zappy::gui::raylib::IIncantationEffect> zappy::gui::raylib::IncantationEffectFactory::createWave(const int &playerId, const float &duration, const Color &color)
{
    return std::make_unique<zappy::gui::raylib::WaveIncantationEffect>(playerId, duration, color);
}
