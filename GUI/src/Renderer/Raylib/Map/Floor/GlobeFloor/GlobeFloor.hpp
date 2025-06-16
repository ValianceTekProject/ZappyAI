/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** GlobeFloor.hpp
*/

#pragma once
#include "../AFloor.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class GlobeFloor : public AFloor {
                public:
                    GlobeFloor(const zappy::game::Map &map, int radius = 10);
                    ~GlobeFloor() = default;

                    void draw() const override;

                    int getRadius() const {return _radius;}
                    void setRadius(int radius) {_radius = radius;}

                private:
                    int _radius;
            };
        }
    } // namespace gui
} // namespace zappy