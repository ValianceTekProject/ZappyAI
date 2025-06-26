/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** PlayerRotation.hpp
*/

#pragma once


#include "APlayerAction.hpp"
#include "IFloor.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class PlayerRotation : public APlayerAction
            {
                public:
                    PlayerRotation(
                        const int &playerId,
                        const ActionType &actionType,
                        const Rotation &movement,
                        const float &timeUnit,
                        const float &elapsedTime = 0.f
                    );
                    ~PlayerRotation() override = default;

                    void update(const float &deltaUnits, APlayerModel &player);

                    void finishAction(const float &deltaUnits, APlayerModel &player);

                private:
                    Movement _movement;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
