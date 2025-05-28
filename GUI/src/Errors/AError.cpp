/*
** EPITECH PROJECT, 2025
** B-OOP-400-BDX-4-1-gui-baptiste.blambert
** File description:
** AError
*/

#include "AError.hpp"

gui::AError::AError(const std::string &msg,
    const std::string &where) noexcept :
    _msg(msg),
    _where(where) {}

const char *gui::AError::what() const noexcept
{
    return _msg.c_str();
}

const char *gui::AError::where() const noexcept
{
    return _where.c_str();
}
