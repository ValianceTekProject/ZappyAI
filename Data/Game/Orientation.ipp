/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** Orientation.ipp
*/

#include "Orientation.hpp"

inline zappy::game::Orientation zappy::game::operator+(const zappy::game::Orientation &orientation, int offset) noexcept
{
    return static_cast<zappy::game::Orientation>((static_cast<int>(orientation) + offset + 4) % 4);
}

inline zappy::game::Orientation &zappy::game::operator+=(zappy::game::Orientation &orientation, int offset) noexcept
{
    orientation = orientation + offset;
    return orientation;
}

inline zappy::game::Orientation zappy::game::operator-(const zappy::game::Orientation &orientation) noexcept
{
    Orientation newOrientation = orientation + 2;
    return newOrientation;
}

inline zappy::game::Orientation zappy::game::operator-(const zappy::game::Orientation &orientation, int offset) noexcept
{
    return orientation + (-offset);
}

inline zappy::game::Orientation &zappy::game::operator-=(zappy::game::Orientation &orientation, int offset) noexcept
{
    orientation = orientation - offset;
    return orientation;
}

inline zappy::game::Orientation &zappy::game::operator++(zappy::game::Orientation &orientation) noexcept
{
    orientation = orientation + 1;
    return orientation;
}

inline zappy::game::Orientation zappy::game::operator++(zappy::game::Orientation &orientation, int) noexcept
{
    Orientation oldOrientation = orientation;
    orientation = orientation + 1;
    return oldOrientation;
}

inline zappy::game::Orientation &zappy::game::operator--(zappy::game::Orientation &orientation) noexcept
{
    orientation = orientation - 1;
    return orientation;
}

inline zappy::game::Orientation zappy::game::operator--(zappy::game::Orientation &orientation, int) noexcept
{
    Orientation oldOrientation = orientation;
    orientation = orientation - 1;
    return oldOrientation;
}

inline zappy::game::Orientation zappy::game::convertOrientation(const std::string &orientation)
{
    if (orientation == "NORTH" || orientation == "N")
        return zappy::game::Orientation::NORTH;
    if (orientation == "EAST" || orientation == "E")
        return zappy::game::Orientation::EAST;
    if (orientation == "SOUTH" || orientation == "S")
        return zappy::game::Orientation::SOUTH;
    if (orientation == "WEST" || orientation == "W")
        return zappy::game::Orientation::WEST;
    throw std::invalid_argument("Bad orientation: " + orientation);
}

inline std::ostream &zappy::game::operator<<(std::ostream &os, const zappy::game::Orientation &orientation)
{
    os << orientationStrings[static_cast<int>(orientation)];
    return os;
}
