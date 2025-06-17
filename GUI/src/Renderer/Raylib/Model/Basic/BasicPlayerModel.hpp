/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** BasicPlayerModel.hpp
*/

#pragma once

#include "APlayerModel.hpp"

namespace zappy {
    namespace gui {
        namespace raylib {
            class BasicPlayerModel : public APlayerModel {
                public:
                    BasicPlayerModel(const int &id);
                    ~BasicPlayerModel() override = default;

                    void init() override;

                    void update() override;

                    void render() override;

                private:
                    void _initModel() override;
            };
        } // namespace raylib
    } // namespace gui
} // namespace zappy
