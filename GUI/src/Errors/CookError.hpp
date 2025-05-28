//
// EPITECH PROJECT, 2025
// CookError
// File description:
// CookError
//

#pragma once

#include "AError.hpp"

namespace gui {
    class CookError : public AError
    {
        public:
            CookError(const std::string &msg, const std::string &where)
                noexcept : AError(msg, where) {};
    };
}
