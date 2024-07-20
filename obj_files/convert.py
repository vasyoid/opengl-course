def convert(input_filename, output_filename):
    v = []
    vn = []
    vt = []
    f = []

    with open(input_filename) as file:
        for line in file.readlines():
            tokens = line.split()
            if len(tokens) == 0:
                continue
            if tokens[0] == "v":
                v.append(list(map(float, tokens[1:])))
            elif tokens[0] == "vn":
                vn.append(list(map(float, tokens[1:])))
            elif tokens[0] == "vt":
                vt.append(list(map(float, tokens[1:])))
            elif tokens[0] == "f":
                f.append(tokens[1:])

    vertex_by_index = {}
    v_new = []
    vn_new = []
    vt_new = []
    f_new = []

    for face in f:
        for index in face:
            if index.count("/") == 2 and index.count("//") == 0:
                if index not in vertex_by_index:
                    vertex_by_index[index] = len(v_new)
                    vi, vti, vni = map(int, index.split("/"))
                    v_new.append(v[vi - 1])
                    vn_new.append(vn[vni - 1])
                    vt_new.append(vt[vti - 1])

    for face in f:
        if face[0].count("/") == 2 and face[0].count("//") == 0:
            f_new.append((vertex_by_index[index] + 1 for index in face[:3]))
            if len(face) == 4:
                f_new.append((vertex_by_index[index] + 1 for index in (face[0], face[2], face[3])))

    with open(output_filename, "wt") as file:
        for vertex in v_new:
            file.write("v " + " ".join(map(str, vertex)) + "\n")
        for vertex_normal in vn_new:
            file.write("vn " + " ".join(map(str, vertex_normal)) + "\n")
        for vertex_texture in vt_new:
            file.write("vt " + " ".join(map(str, vertex_texture)) + "\n")
        for face in f_new:
            file.write("f " + " ".join(map(str, face)) + "\n")


convert("cottage_indexed_fixed.obj", "cottage.obj")
