import subprocess, sys

try:
    from setuptools import setup
except ImportError:
    python_exe = sys.executable
    try:
        subprocess.check_call([python_exe, "-m", "pip", "install", "setuptools"])
        from setuptools import setup
    except Exception as e:
        print("Ошибка установки setuptools:", e)

try:
    import numpy
except ImportError:
    python_exe = sys.executable
    try:
        subprocess.check_call([python_exe, "-m", "pip", "install", "numpy"])
        import numpy
    except Exception as e:
        print("Ошибка установки numpy:", e)

try:
    from Cython.Build import cythonize
except ImportError:
    python_exe = sys.executable
    try:
        subprocess.check_call([python_exe, "-m", "pip", "install", "Cython"])
        from Cython.Build import cythonize
    except Exception as e:
        print("Ошибка установки Cython:", e)

setup(
    ext_modules=cythonize("dither.pyx"),
    include_dirs=[numpy.get_include()]
)