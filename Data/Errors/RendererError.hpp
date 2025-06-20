/*
** EPITECH PROJECT, 2025
** B-OOP-400-BDX-4-1-zappy-baptiste.blambert
** File description:
** RendererError
*/

#pragma once

#include "AError.hpp"

namespace zappy {
    namespace gui {
        class RendererError : public AError
        {
            public:
                RendererError(const std::string &msg, const std::string &where)
                    noexcept : AError(msg, where) {};
        };
    }
}
