/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ABroadcastEffect.hpp
*/

#pragma once

#include "IBroadcastEffect.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class ABroadcastEffect : public IBroadcastEffect
            {
                public:
                    virtual ~ABroadcastEffect() = default;

                    virtual bool isFinished() const = 0;
                    virtual void update(float deltaTime) = 0;

                    virtual void render() const = 0;

                protected:
                    int playerId;

                    float elapsed;
                    float duration;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
