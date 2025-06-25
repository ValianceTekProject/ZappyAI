/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IBroadcastEffect.hpp
*/

#pragma once

#include <iostream>

namespace zappy {
    namespace gui {
        namespace raylib {
            class IBroadcastEffect
            {
                public:
                    virtual ~IBroadcastEffect() = default;

                    virtual bool isFinished() const = 0;
                    virtual void update(const float &deltaUnits) = 0;

                    virtual void render() const = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
