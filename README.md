Impasse
=======

![Python Test Status](https://github.com/SaladDais/Impasse/workflows/Run%20Python%20Tests/badge.svg) [![codecov](https://codecov.io/gh/SaladDais/Impasse/branch/master/graph/badge.svg?token=yCiY7MUMW5)](https://codecov.io/gh/SaladDais/Impasse)

A simple Python wrapper for [assimp](https://github.com/assimp/assimp) using `cffi` to access the library.
Requires Python >= 3.7.

It's a fork of [PyAssimp](https://github.com/assimp/assimp/tree/master/port/PyAssimp),
Assimp's official Python port. In contrast to PyAssimp, it strictly targets modern Python 3 and
provides type hints. It also aims to allow mutating scenes before exporting by having
all wrapper classes operate directly on the underlying C data structures.

## Usage

### Complete example: 3D viewer

`impasse` comes with a simple 3D viewer that shows how to load and display a 3D
model using a shader-based OpenGL pipeline.

![Screenshot](https://raw.githubusercontent.com/SaladDais/Impasse/master/3d_viewer_screenshot.png)

To use it:

```bash
python ./scripts/3d_viewer.py <path to your model>
```

You can use this code as starting point in your applications.

### Writing your own code

To get started with `impasse`, examine the simpler `sample.py` script in `scripts/`,
which illustrates the basic usage. All Assimp data structures are wrapped using
`ctypes`. All the data+length fields in Assimp's data structures (such as
`aiMesh::mNumVertices`, `aiMesh::mVertices`) are replaced by list-like wrapper classes,
so you can call `len()` on them to get their respective size and access
members using `[]`.

For example, to load a file named `hello.3ds` and print the first
vertex of the first mesh, you would do (proper error handling
substituted by assertions ...):

```python3
from impasse import load

scene = load('hello.3ds')

assert len(scene.meshes)
mesh = scene.meshes[0]

assert len(mesh.vertices)
print(mesh.vertices[0])
```

Another example to list the 'top nodes' in a
scene:

```python
from impasse import load

scene = load('hello.3ds')
for c in scene.root_node.children:
    print(str(c))
```

All of assimp's coordinate classes are returned as NumPy arrays, so you can
work with them using library for 3d math that handles NumPy arrays. Using transforms.py
to modify the scene:

```python
import math

import numpy
import transformations
import impasse

# assimp returns an immutable scene, we have to copy it if we want to change it
scene = impasse.load('hello.3ds').copy_mutable()
transform = scene.root_node.transformation
# Rotate the root node's transform by 180 deg on X
transform = numpy.dot(transformations.rotation_matrix(math.pi, (1, 0, 0)), transform)
scene.root_node.transformation = transform
impasse.export(scene, 'whatever.obj', 'obj')
```

# Installing

Install `impasse` by running:

```bash
pip install impasse
```

or, if you want to install from the source directory:

```bash
pip install -e .
```

Impasse requires an assimp dynamic library (`DLL` on Windows,
`.so` on linux, `.dynlib` on macOS) in order to work. The default search directories are:
  - the current directory
  - on linux additionally: `/usr/lib`, `/usr/local/lib`,
    `/usr/lib/<CPU_ARCH>-linux-gnu`

To build that library, refer to the Assimp master `INSTALL`
instructions. To look in more places, edit `./impasse/helper.py`.
There's an `additional_dirs` list waiting for your entries.

# Progress

All features present in PyAssimp are now present in Assimp (plus a few more!) Since the API
largely mirrors PyAssimp's, most existing code should work in Impasse with minor changes.

Note that Impasse is not complete. Many assimp features are still missing, mostly around mutating
scenes. Notably, anything that would require a `new` or `delete` in assimp's C++ API is not supported.

# Performance

Impasse tries to avoid unnecessary copies or conversions of data owned by C, and most classes
are just thin layers around the underlying CFFI structs. NumPy arrays that directly map to the
underlying structs' memory are used for the coordinate structs like `Matrix4x4` and `Vector3D`.

Testing with a similar `quicktest.py` script against assimp's test model directory:

## Impasse

```
** Loaded 169 models, got controlled errors for 28 files, 0 uncontrolled

real	0m1.460s
user	0m1.676s
sys	0m0.571s
```

## PyAssimp

```
** Loaded 165 models, got controlled errors for 28 files, 4 uncontrolled

real	0m7.607s
user	0m7.746s
sys	0m0.579s
```
