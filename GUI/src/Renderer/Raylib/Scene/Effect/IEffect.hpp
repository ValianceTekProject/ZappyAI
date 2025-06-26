/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** IEffect.hpp
*/

#pragma once

#include <iostream>
#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class IEffect
            {
                public:
                    virtual ~IEffect() = default;

                    virtual void update(const float &deltaUnits) = 0;
                    virtual void render(const Vector3 &position) const = 0;

                    virtual bool hasEnded() const = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
