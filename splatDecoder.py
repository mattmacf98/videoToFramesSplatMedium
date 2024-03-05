import math
import sys
import os
import struct

SH_C0 = 0.28209479177387814
ROW_LENGTH = 3 * 4 + 3 * 4 + 4 + 4
# pos[f32;3] (x,y,z), scale[f32;3] (x,y,z), colors[i8;4] (r,g,b,a), rots[i8;4] (w,x,y,z)


def get_ply_header(vertex_count):
    return f"""ply
format binary_little_endian 1.0
element vertex {vertex_count}
property float x
property float y
property float z
property float f_dc_0
property float f_dc_1
property float f_dc_2
property float opacity
property float scale_0
property float scale_1
property float scale_2
property float rot_0
property float rot_1
property float rot_2
property float rot_3
end_header
"""


def read_vertex(file):
    p_x = struct.unpack('f', file.read(4))[0]
    p_y = struct.unpack('f', file.read(4))[0]
    p_z = struct.unpack('f', file.read(4))[0]

    s_x = struct.unpack('f', file.read(4))[0]
    s_y = struct.unpack('f', file.read(4))[0]
    s_z = struct.unpack('f', file.read(4))[0]

    r = struct.unpack('B', file.read(1))[0]
    g = struct.unpack('B', file.read(1))[0]
    b = struct.unpack('B', file.read(1))[0]
    a = struct.unpack('B', file.read(1))[0]

    r_w = struct.unpack('B', file.read(1))[0]
    r_x = struct.unpack('B', file.read(1))[0]
    r_y = struct.unpack('B', file.read(1))[0]
    r_z = struct.unpack('B', file.read(1))[0]

    return {
        "position": {
            "x": p_x,
            "y": p_y,
            "z": p_z
        },
        "scale": {
            "x": s_x,
            "y": s_y,
            "z": s_z
        },
        "color": {
            "r": r,
            "g": g,
            "b": b,
            "a": a
        },
        "rotation": {
            "w": r_w,
            "x": r_x,
            "y": r_y,
            "z": r_z
        },
    }


def turn_vertex_info_to_binary(vertex):
    # Convert each component to binary representation
    position_binary = struct.pack('fff', vertex['position']['x'], vertex['position']['y'], vertex['position']['z'])

    a = vertex['color']['a']

    if a == 0.0:
        a = 0.001
    term = 255/a - 1
    if term <= 0.0:
        term = 0.001
    a = -1 * math.log(term)
    color_binary = struct.pack('ffff', (vertex['color']['r']/255 - 0.5)/SH_C0, (vertex['color']['g']/255 -0.5)/SH_C0, (vertex['color']['b']/255 - 0.5)/SH_C0, a)
    scale_binary = struct.pack('fff', math.log(vertex['scale']['x']), math.log(vertex['scale']['y']), math.log(vertex['scale']['z']))
    rotation_binary = struct.pack('ffff', (vertex['rotation']['w'] - 128)/128, (vertex['rotation']['x'] - 128)/128, (vertex['rotation']['y'] - 128)/128, (vertex['rotation']['z'] - 128)/128)
    # Concatenate binary representations
    serialized_data = position_binary + color_binary + scale_binary + rotation_binary

    return serialized_data


def print_file_info(file_name):
    try:
        # Get file size
        file_size = os.path.getsize(file_name)
        vertex_count = math.floor(file_size/ROW_LENGTH)
        print("File size:", file_size, "bytes")
        print(f"estimated vertices {vertex_count}")

        with open(file_name, 'rb') as file:
            with open('out.ply', 'w') as out_file:
                ply_header = get_ply_header(vertex_count)
                out_file.write(ply_header)
            with open('out.ply', 'ab') as out_file:
                for i in range(vertex_count):
                    vertex = read_vertex(file)
                    out_file.write(turn_vertex_info_to_binary(vertex))

    except FileNotFoundError:
        print("File not found.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <file_name>")
    else:
        file_name = sys.argv[1]
        print_file_info(file_name)