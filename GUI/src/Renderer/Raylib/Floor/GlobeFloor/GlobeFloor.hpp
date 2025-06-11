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
                    GlobeFloor();
                    ~GlobeFloor() = default;

                    void draw(const Map &map) const override;
            };
        }
    } // namespace gui
} // namespace zappy