"""
Pathing module
"""

from typing import List
from dataclasses import dataclass
import time


@dataclass
class Point:
    x: int
    y: int


@dataclass
class Obstacle:
    """
    Obstacle class
    """
    # putting obstacles in landscape as visited
    start: Point
    width: int
    height: int

    @property
    def end(self):
        return Point(self.start.x + self.width, self.start.y + self.height)


# unused class...
# class Collision:
#     """
#     Utility class for collision detection
#     """
#
#     @staticmethod
#     def check_collision(obstacle: Obstacle, observer_position: Point):
#         return (
#                 obstacle.start.x <= observer_position.x <= obstacle.end.x and
#                 obstacle.start.y <= observer_position.y <= obstacle.end.y
#         )


@dataclass
class Landscape:
    """
    Landscape class
    """

    land: List[List[int]]
    obstacles: List[Obstacle]

    # stores 1's to grid to denote obstacles in path (using obstacle class)

    def __init__(self, dim_x, dim_y):
        # initialize an empy grid representing the landscape
        self.land = [[0] * dim_y for _ in range(dim_x)]
        self.obstacles = []

    def add_obstacle(self, obstacle: Obstacle):
        # add an obstacle to the landscape and mark its cells as obstacles
        self.obstacles.append(obstacle)

        for i in range(max(0, obstacle.start.x), min(len(self.land), obstacle.end.x + 1)):
            for j in range(max(0, obstacle.start.y), min(len(self.land[0]), obstacle.end.y + 1)):
                self.land[i][j] = 2  # Use 2 to represent obstacles

    def __str__(self) -> str:
        # print the landscape for visualization
        return "\n".join("".join(map(str, row)) for row in self.land)


@dataclass
class Observer:
    """
    Observer class
    """
    # length, width, pick what position represents
    position: Point

    def move(self, direction):
        # move the observer in the specified direction
        if direction == "up":
            self.position = Point(self.position.x, self.position.y + 1)
        elif direction == "down":
            self.position = Point(self.position.x, self.position.y - 1)
        elif direction == "right":
            self.position = Point(self.position.x + 1, self.position.y)
        elif direction == "left":
            self.position = Point(self.position.x - 1, self.position.y)
        # elif direction == "stay":
        #     self.position = Point(self.position.x, self.position.y)

    def calc_direction(self, target: Point) -> str:
        if self.position.x < target.x:
            return "right"
        elif self.position.x > target.x:
            return "left"
        elif self.position.y < target.y:
            return "up"
        elif self.position.y > target.y:
            return "down"
        # else:
        #     return "stay"  # TODO: implement a case? -- come back after image recognition is implemented

    def move_to(self, target: Point, landscape: Landscape):
        # move to specified target position

        # while self.position.x < target.y:
        #     self.move("up")
        #     print(landscape)
        # while self.position.x > target.y:
        #     self.move("down")
        #     print(landscape)
        # while self.position.x < target.x:
        #     self.move("right")
        #     print(landscape)
        # while self.position.x > target.x:
        #     self.move("left")
        #     print(landscape)

        while self.position != target:
            direction = self.calc_direction(target)
            self.move(direction)
            # time.sleep(2)
            # print("----------------------")
            # print(landscape)
            # print("----------------------")

    @staticmethod
    def find_obstacle_at(position: Point, landscape: Landscape):
        # find obstacle at specified position
        for obstacle in landscape.obstacles:
            if (
                    obstacle.start.x <= position.x <= obstacle.end.x and
                    obstacle.start.y <= position.y <= obstacle.end.y
            ):
                return obstacle
        return None

    def calculate_next_position(self, direction: str) -> Point:
        # Calculate the next position based on the specified direction
        if direction == "up":
            return Point(self.position.x, self.position.y + 1)
        elif direction == "down":
            return Point(self.position.x, self.position.y - 1)
        elif direction == "right":
            return Point(self.position.x + 1, self.position.y)
        elif direction == "left":
            return Point(self.position.x - 1, self.position.y)
        # else:
        #     return self.position  # Handle the "stay" case

    def navigate_around_obstacle(self, landscape: Landscape, collision_point: Point):
        original_position = self.position
        print(1)

        # Initialize perpendicular directions
        if self.position.x != collision_point.x:
            perpendicular_directions = ["up", "down"]
        else:
            perpendicular_directions = ["left", "right"]

        for direction in perpendicular_directions:
            print(2)
            next_position = self.calculate_next_position(direction)
            if (
                    not self.find_obstacle_at(next_position, landscape)
                    and landscape.land[next_position.x][next_position.y] == 0
            ):
                print(3)
                # while self.position != next_position:
                while (
                    # self.position.x == collision_point.x and
                    (
                        landscape.land[self.position.x][self.position.y - 1] == 2 or
                        landscape.land[self.position.x][self.position.y + 1] == 2
                    )  # or
                    # self.position.x != collision_point.x and (
                    #     landscape.land[self.position.x - 1][self.position.y] == 2 or
                    #     landscape.land[self.position.x + 1][self.position.y] == 2
                    # )
                ):
                    print(direction)
                    self.move(direction)
                    landscape.land[self.position.x][self.position.y] = 1  # Mark the traversed path
                    print(f"\n\nDIRECTION: {direction}\n\n")
                    time.sleep(0.5)
                    print("--------------------")
                    print(landscape)
                    print("--------------------")

                # Move back to the original position
                self.move_to(original_position, landscape)

                # Rotate one more time to face the original direction
                self.move("left")
                break

        # if landscape.land[self.position.x][self.position.y] == 2:
        if self.position.x == original_position.x and self.position.y == original_position.y:
            print(4)
            # Move back to the opposite side of the collision point
            opposite_side = Point(collision_point.x, collision_point.y)
            self.move_to(opposite_side, landscape)

    # *****************************************
    def traverse(self, landscape: Landscape):
        for i in range(len(landscape.land)):
            if i % 2 == 0:
                j = 0
                while j < len(landscape.land[0]):
                    if landscape.land[i][j] == 0:
                        self.move_to(Point(i, j), landscape)
                        print("mowing...")
                        landscape.land[i][j] = 1  # mark now explored cell as 1
                        time.sleep(0.05)
                        print("--------------------")
                        print(landscape)
                        print("--------------------")
                        j += 1
                    elif landscape.land[i][j] == 2:
                        # object detected, navigate around obstacle
                        self.navigate_around_obstacle(landscape, Point(i, j))

                        # Continue mowing in the same row after navigating around
                        while j < len(landscape.land[0]) and landscape.land[i][j] != 0:
                            j += 1
                            if j < len(landscape.land[0]) and landscape.land[i][j] == 2:
                                self.navigate_around_obstacle(landscape, Point(i, j))
                    else:
                        j += 1
            else:
                j = len(landscape.land[0]) - 1
                while j >= 0:
                    if landscape.land[i][j] == 0:
                        self.move_to(Point(i, j), landscape)
                        print("mowing...")
                        landscape.land[i][j] = 1  # mark now explored cell as 1
                        time.sleep(0.05)
                        print("--------------------")
                        print(landscape)
                        print("--------------------")
                        j -= 1
                    elif landscape.land[i][j] == 2:
                        # object detected, navigate around obstacle
                        self.navigate_around_obstacle(landscape, Point(i, j))

                        # Continue mowing in the same row after navigating around
                        while j >= 0 and landscape.land[i][j] != 0:
                            j -= 1
                            if j >= 0 and landscape.land[i][j] == 2:
                                self.navigate_around_obstacle(landscape, Point(i, j))
                    else:
                        j -= 1


def main():
    """
    Main function
    """
    # initialize the landscape
    landscape = Landscape(10, 20)
    # adding obstacles for testing
    obstacle1 = Obstacle(Point(2, 5), 2, 3)
    obstacle2 = Obstacle(Point(7, 12), 3, 4)
    landscape.add_obstacle(obstacle1)
    landscape.add_obstacle(obstacle2)

    # initialize the observer at the starting position
    observer = Observer(Point(0, 0))
    # traverse the landscape
    observer.traverse(landscape)

    print(f"Explored Landscape: \n {landscape}")


if __name__ == "__main__":
    main()
