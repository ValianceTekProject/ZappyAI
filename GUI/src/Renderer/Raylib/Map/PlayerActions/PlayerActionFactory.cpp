/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerActionFactory.cpp
*/

#include "PlayerActionFactory.hpp"

std::shared_ptr<zappy::gui::raylib::IPlayerAction> zappy::gui::raylib::PlayerActionFactory::createTranslation(
    const int &playerId,
    const Translation &translation,
    std::shared_ptr<IFloor> floor,
    const float &timeUnit,
    const float &elapsedTime
) {
    return std::make_unique<zappy::gui::raylib::PlayerTranslation>(
        playerId,
        ActionType::TRANSLATION,
        translation,
        floor,
        timeUnit,
        elapsedTime
    );
}

std::shared_ptr<zappy::gui::raylib::IPlayerAction> zappy::gui::raylib::PlayerActionFactory::createRotation(
    const int &playerId,
    const Rotation &rotation,
    const float &timeUnit,
    const float &elapsedTime
) {
    return std::make_unique<zappy::gui::raylib::PlayerRotation>(
        playerId,
        ActionType::ROTATION,
        rotation,
        timeUnit,
        elapsedTime
    );
}

std::shared_ptr<zappy::gui::raylib::IPlayerAction> zappy::gui::raylib::PlayerActionFactory::createBroadcast(
    const int &playerId,
    const BroadcastType &type,
    const Color &color,
    const float &timeUnit,
    const float &elapsedTime
) {
    auto effect = BroadcastEffectFactory::create(type, playerId, timeUnit, color);

    return std::make_unique<PlayerBroadcast>(
        playerId,
        ActionType::BROADCAST,
        std::move(effect),
        timeUnit,
        elapsedTime
    );
}
