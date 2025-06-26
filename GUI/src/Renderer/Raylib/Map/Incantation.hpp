/*
** EPITECH PROJECT, 2024
** zappy
** File description:
** Incantation.hpp
*/

#pragma once
#include <raylib.h>
#include <cmath>
#include "IFloor.hpp"
#include <algorithm>

namespace zappy {
    namespace gui {
        namespace raylib {
            class Incantation {
                public:
                    Incantation(Vector2 tile);

                    void update(float deltaTime);

                    void render(class IFloor *floor) const;

                    bool isAt(int x, int y) const;

                private:
                    Vector2 _tile;
                    float _animationTime;
                    void _renderSpiralParticles(const Vector3& center, float progress) const;
            };
        }
    }
}