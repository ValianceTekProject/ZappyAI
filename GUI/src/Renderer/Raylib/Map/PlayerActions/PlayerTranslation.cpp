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
    _floor->translate(
        deltaUnits,
        this->_movement.movementVector,
        this->_movement.destination,
        player
    );
    APlayerAction::update(deltaUnits, player);
}

void zappy::gui::raylib::PlayerTranslation::finishAction(APlayerModel &player)
{
    player.setPosition(_movement.destination);
}
