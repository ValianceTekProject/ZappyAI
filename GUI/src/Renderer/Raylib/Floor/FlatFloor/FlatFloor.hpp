/*
** EPITECH PROJECT, 2024
** GUI
** File description:
** FlatFloor.hpp
*/

#pragma once
#include "../AFloor.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class FlatFloor : public AFloor {
                public:
                    FlatFloor();
                    ~FlatFloor() = default;

                    void draw(const Map &map) const;
            };
        }
    } // namespace gui
} // namespace zappy
