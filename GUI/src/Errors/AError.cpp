/*
** EPITECH PROJECT, 2025
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
** File description:
** AError
*/

#include "AError.hpp"

zappy::gui::AError::AError(const std::string &msg,
    const std::string &where) noexcept :
    _msg(msg),
    _where(where) {}

const char *zappy::gui::AError::what() const noexcept
{
    return _msg.c_str();
}

const char *zappy::gui::AError::where() const noexcept
{
    return _where.c_str();
}
