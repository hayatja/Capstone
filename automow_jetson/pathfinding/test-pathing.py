"""
Pathing module
"""
from time import sleep
from typing import List, Tuple, Optional, Deque
from dataclasses import dataclass, field
from collections import deque
from enum import Enum


@dataclass
class Point:
    x: int
    y: int


@dataclass
class D(Enum):
    N = 0
    E = 1
    S = 2
    W = 3


@dataclass
class UltrasonicSensor:
    @staticmethod
    def get_distance() -> float:
        # Simulate getting distance data from the sensor
        # Replace this with actual code to read from your ultrasonic sensor
        return 15.0  # Placeholder value


@dataclass
class Observer:
    """
    Observer class
    """

    position: Point
    width: int
    height: int
    direction: D
    mock_sensor_data: List[Tuple[int, int, int]] = field(default_factory=list)

    # need to pull each sensor data before using get function
    # front_sensor: UltrasonicSensor
    # left_sensor: UltrasonicSensor
    # right_sensor: UltrasonicSensor

    def get_all_sensor_data(self, mock_index: Optional[int] = None) -> Tuple[int, int, int]:
        if mock_index is not None:
            return self.mock_sensor_data[mock_index]

        # add code to pull sensor data
        front_sensor = 0
        left_sensor = 0
        right_sensor = 0

        return left_sensor, front_sensor, right_sensor


@dataclass
class Obstacle:
    """
    Obstacle class
    """

    start: Point
    width: int
    height: int

    @property
    def end(self):
        return Point(self.start.x + self.width, self.start.y + self.height)


@dataclass
class Landscape:
    """
    Landscape class
    """

    length: int
    width: int
    obstacles: List[Obstacle] = field(default_factory=list)
    observer: Observer = None

    def add_obstacle(self, obstacle: Obstacle):
        self.obstacles.append(obstacle)

    def set_observer(self, observer: Observer):
        # NOTE: does not account for width and height of observer
        self.observer = observer

    def generate_land(self) -> List[List[int]]:
        land = []
        for _ in range(self.length):
            temp_l = []
            for _ in range(self.width):
                temp_l.append(0)
            land.append(temp_l)

        # insert obstacles into land representation
        for obstacle in self.obstacles:
            for x in range(obstacle.width):
                for y in range(obstacle.height):
                    land[obstacle.start.y + y][obstacle.start.x + x] = 2

        # insert observer into land representation
        # if self.observer:
        #     for x in range(self.observer.width):
        #         for y in range(self.observer.height):
        #             land[self.observer.position.y + y][self.observer.position.x + x] = 3

        return land

    @staticmethod
    def generate_empty_land(length: int, width: int) -> List[List[int]]:
        land = []
        for _ in range(length):
            temp_l = []
            for _ in range(width):
                temp_l.append(-1)
            land.append(temp_l)

        return land

    def __repr__(self):
        return "\n".join("".join(map(str, row)) for row in self.generate_land())

    @staticmethod
    def land_str(land: List[List[int]]) -> str:
        ascii_ref = {
            -1: " ",
            0: "░",
            1: "X",
            2: "▓",
            3: "~"
        }

        return (
            "\n".join(
                str(index) + " " + "".join(
                    ascii_ref[cell] for cell in row
                ) for index, row in enumerate(land)
            )
        )

    def __str__(self) -> str:
        return Landscape.land_str(self.generate_land())


class Mowing:
    # ensure that land is fully initialized before running mow
    @staticmethod
    def is_valid_move(row, col, matrix, visited):
        return (
            0 <= row < len(matrix)
            and 0 <= col < len(matrix[0])
            and matrix[row][col] == 0
            and not visited[row][col]
        )

    @staticmethod
    def traverse(land_array: List[List[int]], observer: Observer) -> List[Tuple[int, int]]:
        rows, cols = len(land_array), len(land_array[0])
        visited = [[False] * cols for _ in range(rows)]
        path = []
        stack = [(observer.position.y, observer.position.x)]

        while stack:
            row, col = stack.pop()

            if not visited[row][col]:
                visited[row][col] = True
                path.append((row, col))

            neighbors = [(row, col + 1), (row + 1, col), (row, col - 1), (row - 1, col)]
            for neighbor_row, neighbor_col in neighbors:
                if Mowing.is_valid_move(neighbor_row, neighbor_col, land_array, visited):
                    stack.append((neighbor_row, neighbor_col))

        # print(Landscape.land_str(land_array))

        return path

    # ----------

    @staticmethod
    def is_valid_sensor_move(
        current_map: List[List[int]],
        row: int,
        col: int,
        threshold: Tuple[int, int],
        sensor_data: Tuple[int, int, int]
    ):
        return (
            0 <= row < len(current_map)
            and 0 <= col < len(current_map[0])
            and not (threshold[0] <= sensor_data[1] <= threshold[1])
            and (current_map[row][col] == 0 or current_map[row][col] == -1)  # Valid move (free space or unvisited)
        )

    @staticmethod
    def closest_unmowed_space(current_map: List[List[int]], observer: Observer) -> Tuple[int, int]:
        rows, cols = len(current_map), len(current_map[0])
        visited = [[False] * cols for _ in range(rows)]
        current_pos = (observer.position.y, observer.position.x)

        queue: Deque[Tuple[Tuple[int, int], Optional[Tuple[int, int]]]] = deque([(current_pos, None)])
        visited[current_pos[0]][current_pos[1]] = True

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            (row, col), prev_coord = queue.popleft()

            if current_map[row][col] == 0:
                return row, col

            for dr, dc in directions:
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                    queue.append(((nr, nc), (row, col)))
                    visited[nr][nc] = True

        return -1, -1

    @staticmethod
    def is_blocked(threshold: Tuple[int, int], value: int):
        return threshold[0] <= value <= threshold[1]

    @staticmethod
    def scan_neighbor_cells(
        current_map: List[List[int]],
        observer: Observer,
        th: Tuple[int, int],
        sensor_data: Tuple[int, int, int]
    ):
        left, front, right = sensor_data
        pos = [observer.position.y, observer.position.x]

        current_map[pos[0]][pos[1]] = 1

        # Define a helper function to check and update the cell based on the sensor value
        def check_and_update(offset, sensor_value):
            nonlocal pos
            new_pos = [pos[0] + offset[0], pos[1] + offset[1]]
            if 0 <= new_pos[0] < len(current_map) and 0 <= new_pos[1] < len(current_map[0]):
                curr = current_map[new_pos[0]][new_pos[1]]
                if Mowing.is_blocked(th, sensor_value):
                    current_map[new_pos[0]][new_pos[1]] = 2  # Obstacle
                else:
                    current_map[new_pos[0]][new_pos[1]] = 0 if curr == -1 else curr  # Free space or visited

        if observer.direction.value == D.N.value:
            check_and_update((0, -1), left)  # W
            check_and_update((0, 1), right)  # E
            check_and_update((-1, 0), front)  # N

        elif observer.direction.value == D.S.value:
            check_and_update((0, -1), right)  # W
            check_and_update((0, 1), left)  # E
            check_and_update((1, 0), front)  # S

        elif observer.direction.value == D.W.value:
            check_and_update((0, -1), front)  # W
            check_and_update((-1, 0), right)  # N
            check_and_update((1, 0), left)  # S

        elif observer.direction.value == D.E.value:
            check_and_update((0, 1), front)  # E
            check_and_update((-1, 0), left)  # N
            check_and_update((1, 0), right)  # S

    @staticmethod
    def calculate_next_move(
        current_map: List[List[int]],
        observer: Observer,
        mock_sensor_index: Optional[int] = None
    ) -> Tuple[int, int]:
        """
        Primary function
        """
        row, col = observer.position.y, observer.position.x
        threshold = (10, 30)  # adjust as required
        sensor_data = observer.get_all_sensor_data(mock_sensor_index)

        Mowing.scan_neighbor_cells(
            current_map=current_map,
            observer=observer,
            th=threshold,
            sensor_data=sensor_data
        )

        directions = [(D.S, 1, 0), (D.W, 0, -1), (D.N, -1, 0), (D.E, 0, 1)]
        for direction, dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if Mowing.is_valid_sensor_move(current_map, new_row, new_col, threshold, sensor_data):
                observer.position = Point(new_col, new_row)
                observer.direction = direction
                return new_row, new_col

        return Mowing.closest_unmowed_space(current_map, observer)

    # ----------

    @staticmethod
    def is_valid_bfs_move(matrix, visited, row, col):
        rows, cols = len(matrix), len(matrix[0])
        return 0 <= row < rows and 0 <= col < cols and matrix[row][col] == 1 and not visited[row][col]

    @staticmethod
    def bfs_connect(
        start: Tuple[int, int],
        end: Tuple[int, int],
        matrix: List[List[int]]
    ):
        rows, cols = len(matrix), len(matrix[0])
        visited = [[False] * cols for _ in range(rows)]

        queue = deque([(start[0], start[1], [])])  # (row, col, path)
        visited[start[0]][start[1]] = True

        while queue:
            current_row, current_col, path = queue.popleft()

            # Check if we reached the destination
            # if current_row == end[0] or current_col == end[1]:
            if (current_row, current_col) == end:
                return path + [(current_row, current_col)]

            # Explore four possible directions: up, down, left, right
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                new_row, new_col = current_row + dr, current_col + dc
                if Mowing.is_valid_bfs_move(matrix, visited, new_row, new_col):
                    new_path = path + [(current_row, current_col)]
                    queue.append((new_row, new_col, new_path))
                    visited[new_row][new_col] = True

        # If there is no path from start to end
        return None

    @staticmethod
    def connect_path(
        mod_land_array: List[List[int]],
        generated_path: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        connected_path = [generated_path[0]]

        last_step = generated_path[0]
        mod_land_array[last_step[0]][last_step[1]] = 1

        for step in generated_path[1:]:
            mod_land_array[step[0]][step[1]] = 1
            if (
                (abs(last_step[0] - step[0]) > 1 or abs(last_step[1] - step[1]) > 1) or
                (last_step[0] != step[0] and last_step[1] != step[1])
            ):
                # print(step, last_step, Mowing.bfs_connect(last_step, step, mod_land_array))
                additional_moves = Mowing.bfs_connect(last_step, step, mod_land_array)[1:-1]
                connected_path.extend(additional_moves)

            connected_path.append(step)
            last_step = step

        return connected_path

    @staticmethod
    def generate_connect_steps(path: List[Tuple[int, int]]):
        direction: D = D.S  # starts facing north w.r.t. the ascii array
        location: Tuple[int, int] = path[0]
        steps: List[str] = []  # forward, left (rotate), right (rotate)

        forward_count = 0

        def flush_forward():  # add all required forward steps to steps list
            nonlocal forward_count, steps
            steps.extend(["forward"] * forward_count)

        def switch_direction(new_direction: D):
            nonlocal direction, steps
            rotations = (new_direction.value - direction.value) % 4

            if rotations <= 2:
                steps.extend(['right'] * rotations)
            else:
                steps.extend(['left'] * (4 - rotations))

            direction = new_direction

        def process_direction(new_direction: D):
            nonlocal direction, forward_count
            if direction is new_direction:
                forward_count += 1
            else:
                flush_forward()
                switch_direction(new_direction)
                forward_count = 1

        for inst in path[1:]:  # instruction
            # only one case will apply at a time due to connected path
            if inst[0] > location[0]:  # y down
                process_direction(D.S)

            elif inst[0] < location[0]:  # y up
                process_direction(D.N)

            elif inst[1] > location[1]:  # x right
                process_direction(D.E)

            elif inst[1] < location[1]:  # x left
                process_direction(D.W)

            else:
                forward_count += 1

            location = inst

        flush_forward()
        return steps


class Mapping:
    @staticmethod
    def get_mock_scan_reads(m, p, d) -> Tuple[int, int, int]:
        def is_obstacle(y, x):
            return m[y][x] == 2 if 0 <= y < len(m) and 0 <= x < len(m[0]) else False

        left_condition = (p[1] == 0 or is_obstacle(p[0], p[1] - 1), D.W)
        front_condition = (p[0] == 0 or is_obstacle(p[0] - 1, p[1]), D.N)
        right_condition = (p[1] == len(m[0]) - 1 or is_obstacle(p[0], p[1] + 1), D.E)

        if d.value == D.S.value:
            left_condition, front_condition, right_condition = right_condition, (
                p[0] == len(m) - 1 or is_obstacle(p[0] + 1, p[1]), D.S), left_condition
        elif d.value == D.W.value:
            left_condition, front_condition, right_condition = front_condition, left_condition, right_condition
        elif d.value == D.E.value:
            left_condition, front_condition, right_condition = right_condition, front_condition, left_condition

        left, left_dir = (20, left_condition[1]) if left_condition[0] else (0, d)
        front, front_dir = (20, front_condition[1]) if front_condition[0] else (0, d)
        right, right_dir = (20, right_condition[1]) if right_condition[0] else (0, d)

        return left, front, right

    @staticmethod
    def generate_sensor_data_from_path(
        land_map: List[List[int]],
        steps: List[str],
        start: Tuple[int, int],
        direction: D = D.S
    ) -> List[Tuple[int, int, int]]:
        """
        Simulation function to test sensor-based algorithm
        """

        sensor_data = []
        pos = start
        curr_dir: D = direction

        directions = [D.N, D.E, D.S, D.W]
        change = [(-1, 0), (0, 1), (1, 0), (0, -1)]

        for step in steps:
            if step == "right":
                curr_dir = directions[(curr_dir.value + 1) % 4]
            elif step == "left":
                curr_dir = directions[(curr_dir.value - 1) % 4]
            elif step == "forward":
                sensor_data.append(Mapping.get_mock_scan_reads(land_map, pos, curr_dir))
                c = change[curr_dir.value]
                pos = (pos[0] + c[0], pos[1] + c[1])

        return sensor_data


def main():
    """
    Main function
    """

    landscape = Landscape(length=10, width=20)

    # observer positioned top right of grid
    observer = Observer(
        position=Point(0, 0),
        height=1,
        width=1,
        direction=D.S
    )

    landscape.set_observer(observer)

    # Add obstacles to the landscape
    landscape.add_obstacle(
        Obstacle(
            start=Point(2, 2),
            height=2,
            width=3
        )
    )
    landscape.add_obstacle(
        Obstacle(
            start=Point(11, 5),
            height=4,
            width=4
        )
    )

    # print(str(landscape))

    land_arr = landscape.generate_land()  # Generate the land using the observer
    # print("\n".join("".join(map(str, row)) for row in land_arr))

    mowing_path = Mowing.traverse(land_arr, landscape.observer)
    connected_path = Mowing.connect_path(list(map(list, land_arr)), mowing_path)
    mowing_steps = Mowing.generate_connect_steps(connected_path)

    # Mock mowing
    ####################

    observer.mock_sensor_data = Mapping.generate_sensor_data_from_path(
        land_map=land_arr,
        steps=mowing_steps,
        start=(0, 0)
    )
    print(observer.mock_sensor_data)

    sensor_mowing_path = []
    sensor_land = Landscape.generate_empty_land(10, 20)
    mock_index = 0

    sensor_mowing_move = Mowing.calculate_next_move(
        sensor_land,
        observer,
        0
    )

    while sensor_mowing_move != (-1, -1):
        mock_index += 1
        sensor_mowing_path.append(sensor_mowing_move)
        sensor_mowing_move = Mowing.calculate_next_move(
            sensor_land,
            observer,
            mock_index
        )

        print(sensor_mowing_move, observer.mock_sensor_data[mock_index], observer.direction)
        print(Landscape.land_str(sensor_land))
        print("  " + "".join(str(i)[-1] for i in range(len(land_arr[0]))))
        print("-------------------")

        sleep(0.5)

    print(sensor_mowing_path)

    ####################

    # steps_index = 0
    # _visited = [[False] * len(land_arr[0]) for _ in range(len(land_arr))]  # Initialize visited matrix
    #
    # for step in connected_path:
    #     # if not Mowing.is_valid_move(step[0], step[1], land_arr, visited):
    #     #     print("Obstacle detected! Stopping.")
    #     #     break
    #
    #     land_arr[step[0]][step[1]] = 1
    #
    #     print(f"> {step[::-1]}")
    #
    #     if steps_index < len(mowing_steps):
    #         print("Next step(s):", end=" ")
    #         while mowing_steps[steps_index] != "forward" and steps_index < len(mowing_steps) - 1:
    #             print(mowing_steps[steps_index] + "; s: " + str(observer.mock_sensor_data[steps_index]), end=" ")
    #             steps_index += 1
    #         print("forward" + "; sensors: " + str(observer.mock_sensor_data[steps_index]))
    #         steps_index += 1
    #
    #     print(Landscape.land_str(land_arr))
    #     print("  " + "".join(str(i)[-1] for i in range(len(land_arr[0]))))
    #
    #     print("-------------------")
    #
    #     sleep(0.01)  # Simulate wait time after each move


if __name__ == "__main__":
    main()
