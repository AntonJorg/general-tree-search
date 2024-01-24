import sys
import pathlib
import subprocess
import requests
import tarfile
import io

import gts


GGP_BASE_URL = "http://github.com/ggp-org/ggp-base/archive/master.tar.gz"
GUAVA_URL = "https://repo1.maven.org/maven2/com/google/guava/guava/17.0/guava-17.0.jar"
GUAVA_DEPENDENCY_URL = "https://repo1.maven.org/maven2/com/google/guava/failureaccess/1.0.1/failureaccess-1.0.1.jar"

JUNIT_URL = "https://repo1.maven.org/maven2/junit/junit/4.13.2/junit-4.13.2.jar"
JUNIT_DEPENDENCY_URL = "https://repo1.maven.org/maven2/org/hamcrest/hamcrest-core/1.3/hamcrest-core-1.3.jar"

ALLOYGGP_URL = "https://repo1.maven.org/maven2/net/alloyggp/alloy-ggp-base/0.0.15/alloy-ggp-base-0.0.15.jar"
GGP_VALIDATION_URL = "https://repo1.maven.org/maven2/net/alloyggp/gdl-validation/0.2.2/gdl-validation-0.2.2.jar"

JAVA_CUP_URL = (
    "https://repo1.maven.org/maven2/com/github/vbmacher/java-cup/11b/java-cup-11b.jar"
)
JAVA_CUP_RUNTIME_URL = "https://repo1.maven.org/maven2/com/github/vbmacher/java-cup-runtime/11b/java-cup-runtime-11b.jar"


def get_source_paths():
    p = pathlib.Path(gts.__file__)
    p = p.parent
    p = p / "games" / "ggp"
    return p / "GGPServer.java", p / "GGPServer.class"


def get_jar_path():
    p = pathlib.Path(sys.executable)
    p = p.parents[1]
    p = p / "share" / "py4j"
    return next(p.glob("*.jar"))


def get_external_java_paths():
    p = pathlib.Path(gts.__file__)
    p = p.parent
    p = p / "java"
    return p / "src", p / "bin", p / "jar"


def download_external_source():
    if not pathlib.Path.is_dir(java_jar):
        pathlib.Path.mkdir(java_jar)

    response = requests.get(GUAVA_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Couldn't download Guava jar!")

    with open(java_jar / "guava.jar", "wb") as f:
        f.write(response.raw.read())

    response = requests.get(GUAVA_DEPENDENCY_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Couldn't download Failureaccess jar!")

    with open(java_jar / "failureaccess.jar", "wb") as f:
        f.write(response.raw.read())

    response = requests.get(JUNIT_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Couldn't download Junit jar!")

    with open(java_jar / "junit.jar", "wb") as f:
        f.write(response.raw.read())

    response = requests.get(JUNIT_DEPENDENCY_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Couldn't download Hamcrest jar!")

    with open(java_jar / "hamcrest.jar", "wb") as f:
        f.write(response.raw.read())

    response = requests.get(ALLOYGGP_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Couldn't download AlloyGGP jar!")

    with open(java_jar / "alloyggp.jar", "wb") as f:
        f.write(response.raw.read())

    response = requests.get(GGP_VALIDATION_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Couldn't download GGP Validation jar!")

    with open(java_jar / "ggp-validation.jar", "wb") as f:
        f.write(response.raw.read())

    response = requests.get(JAVA_CUP_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Couldn't download Java Cup jar!")

    with open(java_jar / "java-cup.jar", "wb") as f:
        f.write(response.raw.read())

    response = requests.get(JAVA_CUP_RUNTIME_URL, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Couldn't download Java Cup Runtime jar!")

    with open(java_jar / "java-cup-runtime.jar", "wb") as f:
        f.write(response.raw.read())

    response = requests.get(GGP_BASE_URL, stream=True)

    if response.status_code != 200:
        raise RuntimeError("Couldn't download ggp-base Java source!")

    fileobj = io.BytesIO(response.raw.read())

    def filter(member: tarfile.TarInfo, path: str) -> tarfile.TarInfo | None:
        base = pathlib.Path("org", "ggp", "base")
        external = pathlib.Path("external")
        paths_to_download = [
            base / "util" / "concurrency",
            base / "util" / "files",
            base / "util" / "game",
            base / "util" / "gdl",
            base / "util" / "prover",
            base / "util" / "propnet",
            base / "util" / "reasoner",
            base / "util" / "statemachine",
            base / "util" / "symbol",
            base / "validator",
            external,
        ]

        tar_path = pathlib.Path(member.name)
        tar_path = pathlib.Path(*tar_path.parts[4:])

        if any(str(tar_path).startswith(str(p)) for p in paths_to_download):
            print(tar_path)
            return member.replace(name=pathlib.Path(path, tar_path).as_posix())
        return None

    with tarfile.open(fileobj=fileobj, mode="r:gz") as t:
        t.extractall(path=java_source, filter=filter)


def compile_source():
    source_files = java_source.glob("**/*.java")
    source_files = " ".join((str(f) for f in source_files))

    print("JAR:", java_jar / "*")

    result = subprocess.run(
        f"javac -Xlint:none -classpath '{java_jar/'*'}' -d {java_bin} {source_files}",
        shell=True,
        check=False,
        capture_output=True,
    )

    if result.returncode == 0:
        print(result.stdout.decode())
    else:
        print(result.stderr.decode())
        raise RuntimeError("Could not compile Java source!")

    result = subprocess.run(
        f"javac -Xlint:none -classpath {jar_path}:'{java_jar/'*'}':'{java_bin/'*'}' {raw_source_path}",
        shell=True,
        check=False,
        capture_output=True,
    )

    if result.returncode == 0:
        print(result.stdout.decode())
    else:
        print(result.stderr.decode())
        raise RuntimeError("Could not compile GGPServer!")


def run():
    cmd = f"java -classpath {compiled_source_path.parent}:{java_jar}:{java_jar / '*'}:{jar_path}:{java_bin} GGPServer"
    print(cmd)
    result = subprocess.run(
        cmd,
        shell=True,
        check=False,
        capture_output=True,
    )

    if result.returncode == 0:
        print(result.stdout.decode())
    else:
        print(result.stderr.decode())


raw_source_path, compiled_source_path = get_source_paths()
jar_path = get_jar_path()
java_source, java_bin, java_jar = get_external_java_paths()

# if not pathlib.Path.is_file(compiled_source_path):
download_external_source()

compile_source()

run()
