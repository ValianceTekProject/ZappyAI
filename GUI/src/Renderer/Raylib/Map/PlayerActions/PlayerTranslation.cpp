/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerTranslation.cpp
*/

#include "PlayerTranslation.hpp"

zappy::gui::raylib::PlayerTranslation::PlayerTranslation(
    const int &playerId,
    const ActionType &actionType,
    const Translation &movement,
    std::shared_ptr<IFloor> floor,
    const float &timeUnit,
    const float &elapsedTime
) :
    APlayerAction(playerId, actionType, timeUnit, elapsedTime),
    _movement(movement),
    _floor(floor)
{}

void zappy::gui::raylib::PlayerTranslation::update(const float &deltaUnits, APlayerModel &player)
{
    APlayerModel::State actionType = player.getState();

    if (actionType != APlayerModel::State::WALK &&
        this->_actionType == ActionType::FORWARD)
            player.walk();
    else if (actionType != APlayerModel::State::EJECT ||
        this->_actionType == ActionType::EXPULSION)
        player.eject();

    _floor->translate(
        deltaUnits,
        this->_movement.movementVector,
        this->_movement.destination,
        player
    );
    APlayerAction::update(deltaUnits, player);
}

void zappy::gui::raylib::PlayerTranslation::finishAction(const float &deltaUnits, APlayerModel &player)
{
    APlayerAction::finishAction(deltaUnits, player);
    player.setPosition(_movement.destination);
}
