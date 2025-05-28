/*
** EPITECH PROJECT, 2025
<<<<<<< HEAD
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
=======
** B-OOP-400-BDX-4-1-gui-baptiste.blambert
>>>>>>> 205ae46 (chore: architecture)
** File description:
** AError
*/

#include "AError.hpp"

<<<<<<< HEAD
zappy::gui::AError::AError(const std::string &msg,
=======
gui::AError::AError(const std::string &msg,
>>>>>>> 205ae46 (chore: architecture)
    const std::string &where) noexcept :
    _msg(msg),
    _where(where) {}

<<<<<<< HEAD
const char *zappy::gui::AError::what() const noexcept
=======
const char *gui::AError::what() const noexcept
>>>>>>> 205ae46 (chore: architecture)
{
    return _msg.c_str();
}

<<<<<<< HEAD
const char *zappy::gui::AError::where() const noexcept
=======
const char *gui::AError::where() const noexcept
>>>>>>> 205ae46 (chore: architecture)
{
    return _where.c_str();
}
