/*
** EPITECH PROJECT, 2025
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
** File description:
** GUIError
*/

#pragma once

#include "AError.hpp"

namespace zappy {
    namespace gui {
        class GUIError : public AError
        {
            public:
                GUIError(const std::string &msg, const std::string &where)
                    noexcept : AError(msg, where) {};
        };
    }
}
