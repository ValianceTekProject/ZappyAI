/*
** EPITECH PROJECT, 2025
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
** File description:
** AError
*/

#include "AError.hpp"

zappy::AError::AError(const std::string &msg,
    const std::string &where) noexcept :
    _msg(msg),
    _where(where) {}

const char *zappy::AError::what() const noexcept
{
    return _msg.c_str();
}

const char *zappy::AError::where() const noexcept
{
    return _where.c_str();
}
