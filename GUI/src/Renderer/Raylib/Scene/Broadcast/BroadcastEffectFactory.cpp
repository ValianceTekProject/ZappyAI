/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BroadcastEffectFactory.cpp
*/

#include "BroadcastEffectFactory.hpp"

const std::array<zappy::gui::raylib::BroadcastEffectFactory::CreateMethod, zappy::gui::raylib::BROADCAST_EFFECT_COUNT> zappy::gui::raylib::BroadcastEffectFactory::_createMethods = {
    &zappy::gui::raylib::BroadcastEffectFactory::createWave
};

std::unique_ptr<zappy::gui::raylib::IBroadcastEffect> zappy::gui::raylib::BroadcastEffectFactory::create(
    const BroadcastType &type,
    const int &playerId,
    const float &duration,
    const Color &color
) {
    return _createMethods[static_cast<size_t>(type)](playerId, duration, color);
}

std::unique_ptr<zappy::gui::raylib::IBroadcastEffect> zappy::gui::raylib::BroadcastEffectFactory::createWave(const int &playerId, const float &duration, const Color &color)
{
    return std::make_unique<zappy::gui::raylib::WaveBroadcastEffect>(playerId, duration, color);
}
