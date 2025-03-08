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
    def __init__(self):
        # add sensor read instructions
        pass

    def get_distance(self) -> float:
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

    # need to pull each sensor data before using get function
    front_sensor: UltrasonicSensor
    left_sensor: UltrasonicSensor
    right_sensor: UltrasonicSensor

    def get_all_sensor_data(self) -> Tuple[float, float, float]:
        # add code to pull sensor data
        left_sensor = self.left_sensor.get_distance()
        front_sensor = self.front_sensor.get_distance()
        right_sensor = self.right_sensor.get_distance()

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
    def is_valid_sensor_move(current_map: List[List[int]], row: int, col: int):
        return (
            0 <= row < len(current_map)
            and 0 <= col < len(current_map[0])
            and current_map[row][col] == 0
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

        # comments are w.r.t. mapping
        # N = up, E = right, S = down, W = left

        if observer.direction.value == D.N.value:
            if pos[1] > 0:  # travelling north, check west
                curr = current_map[pos[0]][pos[1] - 1]  # W
                current_map[pos[0]][pos[1] - 1] = 2 if Mowing.is_blocked(th, left) else (0 if curr == -1 else curr)
            if pos[1] < len(current_map[0]) - 1:  # travelling north, check east
                curr = current_map[pos[0]][pos[1] + 1]  # E
                current_map[pos[0]][pos[1] + 1] = 2 if Mowing.is_blocked(th, right) else (0 if curr == -1 else curr)
            if pos[0] > 0:  # travelling north, check north
                curr = current_map[pos[0] - 1][pos[1]]  # N
                current_map[pos[0] - 1][pos[1]] = 2 if Mowing.is_blocked(th, front) else (0 if curr == -1 else curr)

        if observer.direction.value == D.S.value:
            if pos[1] > 0:  # travelling south, check west
                curr = current_map[pos[0]][pos[1] - 1]  # W
                current_map[pos[0]][pos[1] - 1] = 2 if Mowing.is_blocked(th, right) else (0 if curr == -1 else curr)
            if pos[1] < len(current_map[0]) - 1:  # travelling south, check east
                curr = current_map[pos[0]][pos[1] + 1]  # E
                current_map[pos[0]][pos[1] + 1] = 2 if Mowing.is_blocked(th, left) else (0 if curr == -1 else curr)
            if pos[0] < len(current_map) - 1:  # travelling south, check south
                curr = current_map[pos[0] + 1][pos[1]]  # S
                current_map[pos[0] + 1][pos[1]] = 2 if Mowing.is_blocked(th, front) else (0 if curr == -1 else curr)

        if observer.direction.value == D.W.value:
            if pos[1] > 0:  # travelling west, check west
                curr = current_map[pos[0]][pos[1] - 1]  # W
                current_map[pos[0]][pos[1] - 1] = 2 if Mowing.is_blocked(th, front) else (0 if curr == -1 else curr)
            if pos[0] > 0:  # travelling west, check north
                curr = current_map[pos[0] - 1][pos[1]]  # N
                current_map[pos[0] - 1][pos[1]] = 2 if Mowing.is_blocked(th, right) else (0 if curr == -1 else curr)
            if pos[0] < len(current_map) - 1:  # travelling west, check south
                curr = current_map[pos[0] + 1][pos[1]]  # S
                current_map[pos[0] + 1][pos[1]] = 2 if Mowing.is_blocked(th, left) else (0 if curr == -1 else curr)

        if observer.direction.value == D.E.value:
            if pos[1] < len(current_map[0]) - 1:  # travelling east, check east
                curr = current_map[pos[0]][pos[1] + 1]  # E
                current_map[pos[0]][pos[1] + 1] = 2 if Mowing.is_blocked(th, front) else (0 if curr == -1 else curr)
            if pos[0] > 0:  # travelling west, check north
                curr = current_map[pos[0] - 1][pos[1]]  # N
                current_map[pos[0] - 1][pos[1]] = 2 if Mowing.is_blocked(th, left) else (0 if curr == -1 else curr)
            if pos[0] < len(current_map) - 1:  # travelling west, check south
                curr = current_map[pos[0] + 1][pos[1]]  # S
                current_map[pos[0] + 1][pos[1]] = 2 if Mowing.is_blocked(th, right) else (0 if curr == -1 else curr)

    @staticmethod
    def calculate_next_step(
        current_map: List[List[int]],  # passed as reference
        observer: Observer,
        sensor_data: Optional[Tuple[int, int, int]]
    ) -> str:
        """
        Primary function
        """

        row, col = observer.position.y, observer.position.x
        threshold = (0, 35)  # TODO: adjust as required
        # sensor_data = observer.get_all_sensor_data(mock_sensor_index)

        Mowing.scan_neighbor_cells(
            current_map=current_map,
            observer=observer,
            th=threshold,
            sensor_data=sensor_data
        )

        directions = [(D.S, 1, 0), (D.W, 0, -1), (D.N, -1, 0), (D.E, 0, 1)]
        for direction, dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if Mowing.is_valid_sensor_move(current_map, new_row, new_col):
                generated_step = Mowing.generate_connect_steps(
                    path=[(row, col), (new_row, new_col)],
                    direction=observer.direction
                )[0]

                if generated_step == "forward":
                    observer.position = Point(new_col, new_row)
                else:
                    observer.direction = direction

                return generated_step

        new_row, new_col = Mowing.closest_unmowed_space(current_map, observer)
        if new_row == -1 or new_col == -1:
            return "stop"

        generated_step = Mowing.generate_connect_steps(
            path=[(row, col), (new_row, new_col)],
            direction=observer.direction
        )[0]

        if generated_step == "forward":
            change = [(-1, 0), (0, 1), (1, 0), (0, -1)]
            c = change[observer.direction.value]
            observer.position = Point(col + c[1], row + c[0])
        else:
            direction_names = [D.N, D.E, D.S, D.W]
            mod = 1 if generated_step == "right" else -1
            observer.direction = direction_names[(observer.direction.value + mod) % 4]

        return generated_step

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
        generated_path: List[Tuple[int, int]],
        keep_right: Optional[bool] = False
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
                if keep_right:
                    additional_moves = Mowing.bfs_connect(last_step, step, mod_land_array)[1:]
                else:
                    additional_moves = Mowing.bfs_connect(last_step, step, mod_land_array)[1:-1]
                connected_path.extend(additional_moves)

            connected_path.append(step)
            last_step = step

        return connected_path

    @staticmethod
    def generate_connect_steps(path: List[Tuple[int, int]], direction: D = D.S):
        # direction: D = D.S  # starts facing north w.r.t. the ascii array
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

    @staticmethod
    def back_to_start(pos: Tuple[int, int], matrix: List[List[int]], direction: D):
        # directions = [D.S, D.W, D.N, D.E]
        # pre_moves = []
        # rot = directions[direction.value].value
        # if rot > 2:
        #     pre_moves.extend(["right"] * rot)
        # else:
        #     pre_moves.extend(["left"] * rot)

        back_steps = Mowing.bfs_connect(pos, (0, 0), matrix)
        total_back_moves = Mowing.generate_connect_steps(back_steps, direction)

        # cleanup
        # i = 0
        # while i < len(total_back_moves) - 1:
        #     if (
        #         (total_back_moves[i] == "left" and total_back_moves[i + 1] == "right") or
        #         (total_back_moves[i] == "right" and total_back_moves[i + 1] == "left")
        #     ):
        #         total_back_moves.pop(i)
        #         total_back_moves.pop(i)
        #         i = max(0, i - 1)
        #     elif (i < len(total_back_moves) - 3 and (
        #         total_back_moves[i:i + 4] == ["left", "left", "left", "left"] or
        #         total_back_moves[i:i + 4] == ["right", "right", "right", "right"]
        #     )):
        #         total_back_moves.pop(i)
        #         total_back_moves.pop(i)
        #         total_back_moves.pop(i)
        #         total_back_moves.pop(i)
        #     elif i < len(total_back_moves) - 2 and total_back_moves[i:i + 3] == ["left", "left", "left"]:
        #         directions[i:i + 3] = ["right"]
        #     elif i < len(total_back_moves) - 2 and total_back_moves[i:i + 3] == ["right", "right", "right"]:
        #         total_back_moves[i:i + 3] = ["left"]
        #     else:
        #         i += 1

        return total_back_moves


class Mapping:
    @staticmethod
    def generate_mock_map(length, width) -> List[List[int]]:
        landscape = Landscape(length=length, width=width)

        # observer positioned top right of grid
        # observer = Observer(
        #     position=Point(0, 0),
        #     height=1,
        #     width=1,
        #     direction=D.S,
        #     left_sensor=UltrasonicSensor(),
        #     front_sensor=UltrasonicSensor(),
        #     right_sensor=UltrasonicSensor()
        # )
        #
        # landscape.set_observer(observer)

        # Add obstacles to the landscape
        # landscape.add_obstacle(
        #     Obstacle(
        #         # start=Point(2, 2),
        #         # height=2,
        #         # width=3
        #         start=Point(3, 1),
        #         height=1,
        #         width=1
        #     )
        # )
        # landscape.add_obstacle(
        #     Obstacle(
        #         # start=Point(11, 5),
        #         # height=4,
        #         # width=4
        #         start=Point(1, 3),
        #         height=2,
        #         width=2
        #     )
        # )

        # print(Landscape.land_str(landscape.generate_land()))
        return landscape.generate_land()

    @staticmethod
    def get_scan_reads():
        # Implement in server main file
        pass

    @staticmethod
    def get_mock_scan_reads(m, p, d) -> Tuple[int, int, int]:  # map, position, direction -> (left, front, right)
        if d.value == D.N.value:
            left = 20 if p[1] == 0 or (p[1] > 0 and m[p[0]][p[1] - 1] == 2) else 0  # W
            front = 20 if p[0] == 0 or (p[0] > 0 and m[p[0] - 1][p[1]] == 2) else 0  # N
            right = 20 if p[1] == len(m[0]) - 1 or (p[1] < len(m[0]) - 1 and m[p[0]][p[1] + 1] == 2) else 0  # E

        elif d.value == D.S.value:
            left = 20 if p[1] == len(m[0]) - 1 or (p[1] < len(m[0]) - 1 and m[p[0]][p[1] + 1] == 2) else 0  # E
            front = 20 if p[0] == len(m) - 1 or (p[0] < len(m) - 1 and m[p[0] + 1][p[1]] == 2) else 0  # S
            right = 20 if p[1] == 0 or (p[1] > 0 and m[p[0]][p[1] - 1] == 2) else 0  # W

        elif d.value == D.W.value:
            left = 20 if p[0] == len(m) - 1 or (p[0] < len(m) - 1 and m[p[0] + 1][p[1]] == 2) else 0  # S
            front = 20 if p[1] == 0 or (p[1] > 0 and m[p[0]][p[1] - 1] == 2) else 0  # W
            right = 20 if p[0] == 0 or (p[0] > 0 and m[p[0] - 1][p[1]] == 2) else 0  # N

        elif d.value == D.E.value:
            left = 20 if p[0] == 0 or (p[0] > 0 and m[p[0] - 1][p[1]] == 2) else 0  # N
            front = 20 if p[1] == len(m[0]) - 1 or (p[1] < len(m[0]) - 1 and m[p[0]][p[1] + 1] == 2) else 0  # E
            right = 20 if p[0] == len(m) - 1 or (p[0] < len(m) - 1 and m[p[0] + 1][p[1]] == 2) else 0  # S

        else:
            left = 20
            front = 20
            right = 20

        return left, front, right

    # @staticmethod
    # def generate_sensor_data_from_path(
    #     land_map: List[List[int]],
    #     steps: List[str],
    #     start: Tuple[int, int],
    #     direction: D = D.S
    # ) -> List[Tuple[int, int, int]]:
    #     """
    #     Simulation function to test sensor-based algorithm
    #     """
    #
    #     sensor_data = []
    #     pos = start
    #     curr_dir: D = direction
    #
    #     directions = [D.N, D.E, D.S, D.W]
    #     change = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    #
    #     sensor_data.append(Mapping.get_mock_scan_reads(land_map, pos, curr_dir))
    #
    #     for step in steps:
    #         if step == "right":
    #             curr_dir = directions[(curr_dir.value + 1) % 4]
    #         elif step == "left":
    #             curr_dir = directions[(curr_dir.value - 1) % 4]
    #         elif step == "forward":
    #             c = change[curr_dir.value]
    #             pos = (pos[0] + c[0], pos[1] + c[1])
    #
    #         sensor_data.append(Mapping.get_mock_scan_reads(land_map, pos, curr_dir))
    #
    #     return sensor_data


def main():
    """
    Main function
    """

    # print(str(landscape))

    # land_arr = Mapping.generate_mock_map(10, 20)  # Generate the land using the observer
    # print("\n".join("".join(map(str, row)) for row in land_arr))

    # mowing_path = Mowing.traverse(land_arr, landscape.observer)
    # connected_path = Mowing.connect_path(list(map(list, land_arr)), mowing_path)
    # mowing_steps = Mowing.generate_connect_steps(connected_path)

    # Mock mowing
    ####################

    # observer.mock_sensor_data = Mapping.generate_sensor_data_from_path(
    #     land_map=land_arr,
    #     steps=mowing_steps,
    #     start=(0, 0)
    # )
    # print(observer.mock_sensor_data)

    sensor_mowing_steps = []
    sensor_land = Landscape.generate_empty_land(6, 4)

    observer = Observer(
        position=Point(0, 0),
        height=1,
        width=1,
        direction=D.S,
        left_sensor=UltrasonicSensor(),
        front_sensor=UltrasonicSensor(),
        right_sensor=UltrasonicSensor()
    )

    mock_map = Mapping.generate_mock_map(6, 4)

    sensor_mowing_step = Mowing.calculate_next_step(
        current_map=sensor_land,
        observer=observer,
        sensor_data=Mapping.get_mock_scan_reads(
            m=mock_map,
            p=(observer.position.y, observer.position.x),
            d=observer.direction
        )
    )

    try:
        while sensor_mowing_step != "stop":
            sensor_mowing_steps.append(sensor_mowing_step)
            sensor_mowing_step = Mowing.calculate_next_step(
                current_map=sensor_land,
                observer=observer,
                sensor_data=Mapping.get_mock_scan_reads(
                    m=mock_map,
                    p=(observer.position.y, observer.position.x),
                    d=observer.direction
                )
            )

            print(sensor_mowing_step, observer.direction)

            backing_test = Mowing.back_to_start(
                pos=(observer.position.y, observer.position.x),
                matrix=sensor_land,
                direction=observer.direction
            )
            print(f"To go back from {(observer.position.y, observer.position.x)}: {backing_test}")

            print(Landscape.land_str(sensor_land))
            print("  " + "".join(str(i)[-1] for i in range(len(sensor_land[0]))))
            print("-------------------")

            sleep(0.1)

    finally:
        print(sensor_mowing_steps)

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