/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Orientation.hpp
*/

#pragma once

#include <iostream>
#include <array>

namespace zappy {
    namespace game {
        enum class Orientation {
            NORTH,
            EAST,
            SOUTH,
            WEST
        };

        Orientation operator+(const Orientation &orientation, int offset) noexcept;
        Orientation &operator+=(Orientation &orientation, int offset) noexcept;
        Orientation operator-(const Orientation &orientation) noexcept;
        Orientation operator-(const Orientation &orientation, int offset) noexcept;
        Orientation &operator-=(Orientation &orientation, int offset) noexcept;

        Orientation &operator++(Orientation &o) noexcept;
        Orientation  operator++(Orientation &o, int) noexcept;
        Orientation &operator--(Orientation &o) noexcept;
        Orientation  operator--(Orientation &o, int) noexcept;

        constexpr std::array<const char*, 4> orientationStrings = {
            "NORTH", "EAST", "SOUTH", "WEST"
        };

        Orientation convertOrientation(const std::string &orientation);

        std::ostream &operator<<(std::ostream &os, const Orientation &orientation);
    }
}

#include "Orientation.ipp"
