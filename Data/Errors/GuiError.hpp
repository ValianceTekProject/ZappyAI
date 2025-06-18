/*
** EPITECH PROJECT, 2025
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
** File description:
** GuiError
*/

#pragma once

#include "AError.hpp"

namespace zappy {
    namespace gui {
        class GuiError : public AError
        {
            public:
                GuiError(const std::string &msg, const std::string &where)
                    noexcept : AError(msg, where) {};
        };
    }
}
