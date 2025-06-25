/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerActionFactory.cpp
*/

#include "PlayerActionFactory.hpp"

std::unique_ptr<zappy::gui::raylib::IPlayerAction> zappy::gui::raylib::PlayerActionFactory::createTranslation(
    const int &playerId,
    const ActionType &actionType,
    const Translation &translation,
    std::shared_ptr<IFloor> floor,
    const float &timeUnit,
    const float &elapsedTime
)
{
    return std::make_unique<zappy::gui::raylib::PlayerTranslation>(playerId, actionType, translation, floor, timeUnit, elapsedTime);
}

std::unique_ptr<zappy::gui::raylib::IPlayerAction> zappy::gui::raylib::PlayerActionFactory::createRotation(
    const int &playerId,
    const ActionType &actionType,
    const Rotation &rotation,
    const float &timeUnit,
    const float &elapsedTime
)
{
    return std::make_unique<zappy::gui::raylib::PlayerRotation>(playerId, actionType, rotation, timeUnit, elapsedTime);
}
