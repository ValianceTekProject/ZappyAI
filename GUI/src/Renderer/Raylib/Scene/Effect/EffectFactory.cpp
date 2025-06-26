/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BroadcastEffectFactory.cpp
*/

#include "EffectFactory.hpp"

const std::array<zappy::gui::raylib::EffectFactory::CreateMethod, zappy::gui::raylib::EFFECT_COUNT> zappy::gui::raylib::EffectFactory::_createMethods = {
    &zappy::gui::raylib::EffectFactory::createWave
};

std::unique_ptr<zappy::gui::raylib::IEffect> zappy::gui::raylib::EffectFactory::create(
    const EffectType &type,
    const int &playerId,
    const float &duration,
    const Color &color
) {
    return _createMethods[static_cast<size_t>(type)](playerId, duration, color);
}

std::unique_ptr<zappy::gui::raylib::IEffect> zappy::gui::raylib::EffectFactory::createWave(const int &playerId, const float &duration, const Color &color)
{
    return std::make_unique<WaveBroadcastEffect>(playerId, duration, color);
}

std::unique_ptr<zappy::gui::raylib::IEffect> zappy::gui::raylib::EffectFactory::createIncantation(const int &playerId, const float &duration, const Color &color)
{
    return std::make_unique<SpiralIncantationEffect>(playerId, duration, color);
}
