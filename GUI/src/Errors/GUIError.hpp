/*
** EPITECH PROJECT, 2025
<<<<<<< HEAD
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
=======
** B-OOP-400-BDX-4-1-gui-baptiste.blambert
>>>>>>> 205ae46 (chore: architecture)
** File description:
** GUIError
*/

#pragma once

#include "AError.hpp"

<<<<<<< HEAD
namespace zappy {
    namespace gui {
        class GUIError : public AError
        {
            public:
                GUIError(const std::string &msg, const std::string &where)
                    noexcept : AError(msg, where) {};
        };
    }
=======
namespace gui {
    class GUIError : public AError
    {
        public:
            GUIError(const std::string &msg, const std::string &where)
                noexcept : AError(msg, where) {};
    };
>>>>>>> 205ae46 (chore: architecture)
}
