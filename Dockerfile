FROM python:3.9-slim-bullseye 
LABEL maintainer="jsolislemus <j.solis-lemus@imperial.ac.uk>"

RUN apt-get update --fix-missing && \
    apt-get install -y --no-install-recommends \
    git libsm6 libxext6 libxrender-dev libgl1-mesa-glx ffmpeg \
    build-essential cmake libopenmpi-dev mesa-common-dev mesa-utils freeglut3-dev \
    ninja-build && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV VIRTUAL_ENV=/opt/venv \
    PATH="$VIRTUAL_ENV/bin:$PATH" \
    PYTHONPATH="${PYTHONPATH}:/code"

# Clone VTK source code
WORKDIR /code
RUN python3 -m venv $VIRTUAL_ENV && \
    /opt/venv/bin/python3 -m pip install --upgrade pip && \
    mkdir -p /code /data && \
    git clone --branch v9.2.6 --depth 1 https://gitlab.kitware.com/vtk/vtk.git && \
    mkdir -p /code/vtk/build

# Build VTK
WORKDIR /code/vtk/build
RUN cmake \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DBUILD_SHARED_LIBS:BOOL=ON \
    -DBUILD_TESTING:BOOL=OFF \
    -DVTK_WRAP_PYTHON:BOOL=ON \
    -GNinja -DVTK_WHEEL_BUILD=ON \
    -DVTK_PYTHON_VERSION:STRING=3 \
    -DVTK_USE_SYSTEM_EXPAT:BOOL=ON \
    -DVTK_USE_SYSTEM_ZLIB:BOOL=ON \
    -DVTK_USE_SYSTEM_PNG:BOOL=ON \
    -DVTK_USE_SYSTEM_JPEG:BOOL=ON \
    -DVTK_USE_SYSTEM_TIFF:BOOL=ON \
    -DVTK_USE_SYSTEM_FREETYPE:BOOL=ON \
    -DVTK_USE_SYSTEM_HDF5:BOOL=ON \
    -DVTK_USE_SYSTEM_JSONCPP:BOOL=ON \
    -DVTK_USE_SYSTEM_LIBXML2:BOOL=ON \
    -DVTK_USE_SYSTEM_NETCDF:BOOL=ON \
    -DVTK_USE_SYSTEM_OGGTHEORA:BOOL=ON \
    -DVTK_USE_SYSTEM_ZLIB:BOOL=ON \
    -DVTK_USE_SYSTEM_LZ4:BOOL=ON \
    -DVTK_USE_SYSTEM_BLOSC:BOOL=ON \
    -DVTK_USE_SYSTEM_SNAPPY:BOOL=ON \
    -DVTK_USE_SYSTEM_LIBARCHIVE:BOOL=ON \
    -DVTK_USE_SYSTEM_SQLITE:BOOL=ON \
    -DVTK_USE_SYSTEM_TBB:BOOL=ON \
    -DVTK_USE_SYSTEM_GL2PS:BOOL=ON \
    -DVTK_USE_SYSTEM_FFMPEG:BOOL=ON \
    -DVTK_USE_SYSTEM_OSMESA:BOOL=ON \
    ..
# -DVTK_INSTALL_PYTHON_MODULE_DIR:PATH=/opt/venv/lib/python3.10/site-packages \

RUN ninja && /opt/venv/bin/python3 -m pip install wheel && \
    /opt/venv/bin/python3 setup.py bdist_wheel 

# Install the wheel
WORKDIR /code/vtk/build/dist
RUN /opt/venv/bin/python3 -m pip install vtk*.whl

COPY reqs.txt /code/
RUN /opt/venv/bin/python3 -m pip install -r /code/reqs.txt 

# Copy the rest of the application code
COPY ./seg_scripts/ /code/seg_scripts
COPY ./docker /code/docker

# Specify the command to run on container start
ENTRYPOINT ["/opt/venv/bin/python3", "/code/docker/entrypoint.py"]
