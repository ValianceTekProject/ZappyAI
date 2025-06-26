/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerActionFactory.cpp
*/

#include "PlayerActionFactory.hpp"

ssize_t zappy::gui::raylib::PlayerActionFactory::_newId = 0;

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
    const EffectType &type,
    const Color &color,
    const float &timeUnit,
    const float &elapsedTime
) {
    auto effect = EffectFactory::create(type, playerId, timeUnit, color);

    return std::make_unique<PlayerBroadcast>(
        _newId++,
        playerId,
        ActionType::BROADCAST,
        std::move(effect),
        timeUnit,
        elapsedTime
    );
}

std::shared_ptr<zappy::gui::raylib::IPlayerAction> zappy::gui::raylib::PlayerActionFactory::createIncantation(
    const int &playerId,
    const EffectType &type,
    const Color &color,
    const Vector2 &pos,
    const float &timeUnit,
    const float &elapsedTime
) {
    auto effect = EffectFactory::create(type, playerId, timeUnit, color);

    return std::make_unique<PlayerIncantation>(
        _newId++,
        playerId,
        ActionType::INCANTATION,
        std::move(effect),
        pos,
        timeUnit,
        elapsedTime
    );
}
