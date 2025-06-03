/*
** EPITECH PROJECT, 2024
** Zappy
** File description:
** ResourceContainer.hpp
*/

#pragma once

#include "Resource.hpp"

namespace zappy {
    namespace game {
        class ResourceContainer
        {
            public:
                ResourceContainer() { clear(); }
                ResourceContainer(const ResourceContainer &other) = default;
                ~ResourceContainer() = default;

                void clear();

                void addResource(Resource resource, size_t quantity = 1);
                void addSingleResource(Resource resource);

                void removeResource(Resource resource, size_t quantity = 1);

                size_t getResourceQuantity(Resource resource) const;
                const std::array<size_t, RESOURCE_QUANTITY> &getResources() const { return _resources; }

            private:
                std::array<size_t, RESOURCE_QUANTITY> _resources;
        };
    }
}
