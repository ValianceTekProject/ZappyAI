/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** IIncantationEffect.hpp
*/

#pragma once

#include <iostream>
#include <raylib.h>

namespace zappy {
    namespace gui {
        namespace raylib {
            class IIncantationEffect
            {
                public:
                    virtual ~IIncantationEffect() = default;

                    virtual void update(const float &deltaUnits) = 0;
                    virtual void render(const Vector3 &position) const = 0;

                    virtual bool isFinished() const = 0;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
