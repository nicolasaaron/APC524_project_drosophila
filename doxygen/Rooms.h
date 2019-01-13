/**
 * \file
 *
 * \brief Deal with rooms in a house
 *
 * Here we have lots of architectural detail
 */
#ifndef ROOMS_H_
#define ROOMS_H_
/**
 * \brief Base class for rooms
 */
class Room {
public:
    /// ctor
    Room();
    /// dtor
    ~Room() {}
    /// Add a door
    void addDoor();
    // ...
};
#endif // ROOMS_H_
